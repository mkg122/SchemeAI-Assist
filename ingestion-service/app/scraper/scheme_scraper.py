from playwright.sync_api import sync_playwright

SCHEME_URL = "https://www.myscheme.gov.in"

def fetch_schemes():
    schemes = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless = True)
        page = browser.new_page()

        page.goto(f"{SCHEME_URL}/search/ministry/all-ministries", timeout=60000)

        # Wait for actual scheme links to appear
        page.wait_for_selector("a[href*='/schemes/']", timeout=15000)

        links = page.query_selector_all("a[href*='/schemes/']")

        for link in links:
            title = link.inner_text().strip()
            href = link.get_attribute("href")

            if title and href:
                schemes.append({
                    "title": title,
                    "url": SCHEME_URL + href
                })
        browser.close()
    
    unique_scheme = {s["url"]: s for s in schemes}
    return list(unique_scheme.values())