# import json
# import time
from playwright.sync_api import sync_playwright, Playwright

# def run(playwright: Playwright):
#     browser = playwright.firefox.launch()
#     page = browser.new_page()
#     page.goto("https://www.realestate.com.au/australia/")
#     print(page.title())
#     print(page.url)
#     browser.close()

# with sync_playwright() as playwright:
#     run(playwright)

# from playwright.sync_api import sync_playwright

# base_url = "https://auspost.com.au"

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)
#     page = browser.new_page()
#     page.goto(f"{base_url}/postcode/suburb-index/a", wait_until="networkidle")

#     # Get all pagination URLs
#     pagination_links = page.query_selector_all("ul.pagination li.page_link a")
#     page_urls = [link.get_attribute("href") for link in pagination_links]
#     page_urls = [f"{base_url}{url}" for url in page_urls]

#     # Always include the first page
#     page_urls = [f"{base_url}/postcode/suburb-index/a"] + page_urls

#     suburbs = []

#     for url in page_urls:
#         page.goto(url, wait_until="networkidle")
#         links = page.query_selector_all("ul.pol-suburb-index-list a.pol-suburb-index-link")
#         for link in links:
#             href = link.get_attribute("href")
#             # name = link.inner_text().strip()
#             # suburbs.append((href, name))

#     browser.close()

#     for href, name in suburbs:
#         print(href)

import time
import random
import csv
from playwright.sync_api import sync_playwright

BASE_URL = "https://auspost.com.au"
LETTERS = [
    "a","b","c","d","e","f","g","h","i","k","l","m","n","o",
    "p","q","r","s","t","u","v","w","x","y","z"
]

def human_delay(a=1.2, b=2.8):
    """Random delay to reduce load and mimic human browsing."""
    time.sleep(random.uniform(a, b))

def scrape_suburbs_to_csv(csv_filename="auspost_suburbs.csv"):
    all_suburbs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            )
        )

        for letter in LETTERS:
            print(f"Scraping letter: {letter.upper()}")
            start_url = f"{BASE_URL}/postcode/suburb-index/{letter}"
            page.goto(start_url, wait_until="networkidle")
            human_delay()

            while True:
                # Extract href and suburb name
                links = page.query_selector_all("ul.pol-suburb-index-list a.pol-suburb-index-link")
                for link in links:
                    href = link.get_attribute("href")
                    name = link.inner_text().strip()
                    all_suburbs.append([href, name])

                # Check for next page
                next_link = page.query_selector("li.next_link a")
                if next_link:
                    next_href = next_link.get_attribute("href")
                    page.goto(BASE_URL + next_href, wait_until="networkidle")
                    human_delay()
                else:
                    break

        browser.close()

    # Save to CSV
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["href", "suburb"])
        writer.writerows(all_suburbs)

    print(f"\nSaved {len(all_suburbs)} suburbs to {csv_filename}")

if __name__ == "__main__":
    scrape_suburbs_to_csv()