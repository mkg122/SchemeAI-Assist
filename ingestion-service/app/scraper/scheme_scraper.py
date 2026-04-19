from playwright.sync_api import sync_playwright

SCHEME_PORTAL_URL = "https://www.myscheme.gov.in"

def extract_scheme_name(page):
    scheme_selectors = [
        "#scrollDiv h1",          
        "div[role='main'] h1"                
    ]

    for selector in scheme_selectors:
        scheme_loc = page.locator(selector)
        if scheme_loc.count() > 0:
            first_element = scheme_loc.first
            scheme_name = first_element.get_attribute("title") or first_element.inner_text()
            if scheme_name:
                return scheme_name.strip()
    return ""

def parse_scheme_data(context, url, ministry):
    page = context.new_page()
    print(f"Loading scheme page: {url}")
    
    data = {
        "scheme_name": "",
        "ministry": ministry,
        "details": "",
        "benefits": "",
        "eligibility": "",
        "application_process": "",
        "documents_required": "",
        "exclusions": "",
        "states": ""
    }

    try:
        page.goto(url, wait_until="networkidle", timeout=60000)
        
        page.wait_for_selector("#scrollDiv", timeout=15000)

        data["scheme_name"] = extract_scheme_name(page)
                    
        section_map = {
            "details": "details",
            "benefits": "benefits",
            "eligibility": "eligibility",
            "application-process": "application_process",
            "documents-required": "documents_required",
            "exclusions": "exclusions"
        }

        for element_id, data_key in section_map.items():
            section_locator = page.locator(f"#{element_id}")
            if section_locator.count() > 0:
                data[data_key] = section_locator.inner_text().strip()

    except Exception as e:
        print(f"Error parsing {url}: {e}")
    finally:
        page.close()
    return data

def fetch_schemes():
    all_schemes = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context()
        page = context.new_page()

        ministries_url = f"{SCHEME_PORTAL_URL}/search/ministry/all-ministries"
        print(f"Navigating to {ministries_url}")
        page.goto(ministries_url, timeout=60000)
        page.wait_for_selector("#ministryBasedSchemes")

        ministries_count = page.locator("#ministryBasedSchemes > div").count()
        print(f"Found {ministries_count} ministries.")

        for i in range(ministries_count):
            print(f"\nProcessing ministry {i+1}/{ministries_count}")
            
            page.wait_for_selector("#ministryBasedSchemes > div", timeout=15000)
            cards = page.locator("#ministryBasedSchemes > div")
            card = cards.nth(i)
            
            ministry_name = card.get_attribute("title") or "Unknown Ministry"
            print(f"Ministry: {ministry_name}")
            
            card.click()
            
            page.wait_for_selector("div[role='article']", timeout=15000)
            scheme_cards = page.locator("div[role='article']")
            scheme_count = scheme_cards.count()
            
            print(f"Found {scheme_count} schemes for {ministry_name}")
            
            scheme_urls = []
            for j in range(scheme_count):
                link = scheme_cards.nth(j).locator("a[href^='/schemes/']")
                if link.count() > 0:
                    href = link.first.get_attribute("href")
                    if href:
                        scheme_urls.append(SCHEME_PORTAL_URL + href)

            for scheme_url in scheme_urls:
                data = parse_scheme_data(context, scheme_url, ministry_name)
                all_schemes.append(data)
            
            page.go_back()
            page.wait_for_selector("#ministryBasedSchemes", timeout=15000)

        browser.close()
        
    return unique_scheme(all_schemes)


def unique_scheme(all_schemes):
    unique = {s["scheme_name"]: s for s in all_schemes if s["scheme_name"]}
    return list(unique.values())