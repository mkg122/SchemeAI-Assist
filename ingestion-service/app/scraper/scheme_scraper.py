from playwright.sync_api import sync_playwright

BASE_URL = "https://www.myscheme.gov.in"


def parse_scheme_detail(context, url):
    page = context.new_page()
    print("\n\n Test 1 \n\n")
    page.goto(url, timeout=60000)
    page.wait_for_selector("h1")

    print("\n\n Test 2 \n\n")
    data = {
        "scheme_name": "",
        "ministry": "",
        "details": "",
        "benefits": "",
        "eligibility": "",
        "application_process": "",
        "documents_required": "",
        "exclusions": "",
        "states": ""
    }

    # Title
    title = page.locator("h1").first
    if title.count() > 0:
        data["scheme_name"] = title.inner_text().strip()

    # Ministry
    ministry = page.locator("h2").first
    if ministry.count() > 0:
        data["ministry"] = ministry.inner_text().strip()

    # Sections
    sections = page.locator("h2, h3")
    count = sections.count()

    print(f"\n\n Test 3 : {count} \n\n")
    for i in range(count):
        section = sections.nth(i)
        heading = section.inner_text().strip().lower()
        # print("\n\n Test 4 \n\n")
        try:
            # Find parent section using closest div with id
            parent_section = section.locator("xpath=ancestor::div[@id][1]")

            section_id = parent_section.get_attribute("id") if parent_section.count() else ""

            if section_id:
                content_container = page.locator(f"#{section_id} .markdown-options")

                if content_container.count() > 0:
                    content = content_container.first.inner_text().strip()
                else:
                    content = ""
            else:
                content = ""

        except Exception as e:
            print("Error:", e)
            content = ""

        if not content:
            continue
        # print(content)
        if "benefit" in heading:
            data["benefits"] = content
        elif "eligib" in heading:
            data["eligibility"] = content
        elif "application" in heading or "apply" in heading:
            data["application_process"] = content
        elif "document" in heading:
            data["documents_required"] = content
        elif "exclusion" in heading:
            data["exclusions"] = content
        elif "state" in heading:
            data["states"] = content
        elif "detail" in heading or "about" in heading or "description" in heading:
            data["details"] = content

    page.close()
    print("\n\n Test 1 \n\n")
    print(data)
    return data


def fetch_schemes():
    all_schemes = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(f"{BASE_URL}/search/ministry/all-ministries", timeout=60000)
        page.wait_for_selector("#ministryBasedSchemes")

        cards = page.locator("#ministryBasedSchemes > div")
        total_cards = cards.count()

        for i in range(total_cards):
            print(f"Processing ministry {i+1}/{total_cards}")

            if i==1:
                break
            card = cards.nth(i)
            ministry_name = card.get_attribute("title")

            card.click()

            page.wait_for_selector("div[role='article']", timeout=15000)

            scheme_cards = page.locator("div[role='article']")
            scheme_count = scheme_cards.count()

            for j in range(scheme_count):
                scheme = scheme_cards.nth(j)

                link = scheme.locator("a[href^='/schemes/']")
                if link.count() == 0:
                    continue

                href = link.first.get_attribute("href")
                if not href:
                    continue

                full_url = BASE_URL + href

                try:
                    print(f"  Scraping: {full_url}")
                    data = parse_scheme_detail(context, full_url)

                    if not data["ministry"]:
                        data["ministry"] = ministry_name

                    all_schemes.append(data)

                except Exception as e:
                    print(f"  Error: {e}")
                    continue

            page.go_back()
            page.wait_for_selector("#ministryBasedSchemes")

        browser.close()

    # Deduplicate
    unique = {s["scheme_name"]: s for s in all_schemes if s["scheme_name"]}
    return list(unique.values())


if __name__ == "__main__":
    schemes = fetch_schemes()

    print(f"\nTotal schemes scraped: {len(schemes)}")

    for s in schemes[:3]:
        print("\n----------------------")
        for k, v in s.items():
            print(f"{k}: {v}")