# import csv
# from playwright.sync_api import sync_playwright, TimeoutError

# INPUT_CSV = "url_domain.csv"
# OUTPUT_CSV = "output_domain.csv"

# def safe_text(locator, timeout=3000):
#     try:
#         return locator.first.inner_text(timeout=timeout).strip()
#     except (TimeoutError, Exception):
#         return None

# def value_by_label(container, label):
#     return safe_text(container.locator(f'xpath=.//h4[contains(normalize-space(), "{label}")]/following-sibling::div'), timeout=2000)

# def scrape_market_segment(page, button, segment_name):
#     try:
#         button.wait_for(state="visible", timeout=5000)
#         button.click()

#         expanded = button.locator("xpath=ancestor::tr/following-sibling::tr[contains(@class,'css-1wpy7ho')]")
#         expanded.wait_for(state="visible", timeout=5000)

#         data = {
#             "segment": segment_name,
#             "median_price": value_by_label(expanded, "Median price"),
#             "entry_level": value_by_label(expanded, "Entry level"),
#             "high_end": value_by_label(expanded, "High end"),
#             "sold_this_year": value_by_label(expanded, "Sold this year"),
#             "rental_median": value_by_label(expanded, "Rental median price"),
#             "auction_clearance": value_by_label(expanded, "Auction clearance"),
#             "avg_days_on_market": value_by_label(expanded, "Average days on market"),
#         }

#         # Yearly table
#         rows = expanded.locator("#suburb-insights__table tbody tr")
#         yearly_list = []
#         for i in range(rows.count()):
#             cells = rows.nth(i).locator("td")
#             yearly_list.append(
#                 f"{safe_text(cells.nth(0))}={safe_text(cells.nth(1))}({safe_text(cells.nth(2))})[{safe_text(cells.nth(3))}]"
#             )
#         data["yearly"] = "; ".join(yearly_list) if yearly_list else None

#         try:
#             button.click()  # Collapse
#             expanded.wait_for(state="hidden", timeout=5000)
#         except TimeoutError:
#             pass

#         return data

#     except Exception as e:
#         print(f"⚠️ Segment {segment_name} failed: {e}")
#         return {
#             "segment": segment_name,
#             "median_price": None,
#             "entry_level": None,
#             "high_end": None,
#             "sold_this_year": None,
#             "rental_median": None,
#             "auction_clearance": None,
#             "avg_days_on_market": None,
#             "yearly": None
#         }

# def process_url(url, browser):
#     context = browser.new_context()
#     page = context.new_page()
#     results = []

#     try:
#         print(f"\nProcessing: {url}")
#         page.goto(url, timeout=30000, wait_until="domcontentloaded")

#         buttons = page.locator('button[data-testid="market-button"]')
#         if buttons.count() == 0:
#             results.append({
#                 "url": url,
#                 "segment": None,
#                 "median_price": None,
#                 "entry_level": None,
#                 "high_end": None,
#                 "sold_this_year": None,
#                 "rental_median": None,
#                 "auction_clearance": None,
#                 "avg_days_on_market": None,
#                 "yearly": None
#             })
#         else:
#             for i in range(buttons.count()):
#                 button = buttons.nth(i)
#                 segment_name = button.get_attribute("name") or f"segment_{i+1}"
#                 results.append({ "url": url, **scrape_market_segment(page, button, segment_name) })

#     except Exception as e:
#         print(f"❌ Failed: {url} -> {e}")
#         results.append({
#             "url": url,
#             "segment": "ERROR",
#             "median_price": None,
#             "entry_level": None,
#             "high_end": None,
#             "sold_this_year": None,
#             "rental_median": None,
#             "auction_clearance": None,
#             "avg_days_on_market": None,
#             "yearly": None
#         })
#     finally:
#         context.close()

#     return results

# def main():
#     with open(INPUT_CSV, newline="", encoding="utf-8") as f:
#         urls = [row["link"] for row in csv.DictReader(f) if row.get("link")]

#     print(f"Found {len(urls)} URLs")

#     all_rows = []
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         for url in urls:
#             all_rows.extend(process_url(url, browser))
#         browser.close()

#     fieldnames = [
#         "url", "segment", "median_price", "entry_level", "high_end",
#         "sold_this_year", "rental_median", "auction_clearance", "avg_days_on_market", "yearly"
#     ]
#     with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(all_rows)

#     print(f"\n✅ Saved {len(all_rows)} rows to {OUTPUT_CSV}")

# if __name__ == "__main__":
#     main()

#########################

# import csv
# import time
# import random
# from playwright.sync_api import sync_playwright, TimeoutError

# INPUT_CSV = "url_domain copy.csv"
# OUTPUT_CSV = "output_domain.csv"

# # ---------------- HELPERS ----------------

# def human_pause(a=0.8, b=2.0):
#     time.sleep(random.uniform(a, b))

# def safe_text(locator, timeout=3000):
#     try:
#         return locator.first.inner_text(timeout=timeout).strip()
#     except Exception:
#         return None

# def value_by_label(container, label):
#     return safe_text(
#         container.locator(
#             f'xpath=.//h4[contains(normalize-space(), "{label}")]/following-sibling::div'
#         ),
#         timeout=2000
#     )

# # ---------------- MARKET SCRAPER ----------------

# def scrape_market_segment(page, button, segment_name):
#     try:
#         button.scroll_into_view_if_needed()
#         human_pause(0.5, 1.2)
#         button.click()

#         expanded = button.locator(
#             "xpath=ancestor::tr/following-sibling::tr[contains(@class,'css-1wpy7ho')]"
#         )
#         expanded.wait_for(state="visible", timeout=8000)

#         data = {
#             "segment": segment_name,
#             "median_price": value_by_label(expanded, "Median price"),
#             "entry_level": value_by_label(expanded, "Entry level"),
#             "high_end": value_by_label(expanded, "High end"),
#             "sold_this_year": value_by_label(expanded, "Sold this year"),
#             "rental_median": value_by_label(expanded, "Rental median price"),
#             "auction_clearance": value_by_label(expanded, "Auction clearance"),
#             "avg_days_on_market": value_by_label(expanded, "Average days on market"),
#         }

#         # Yearly table
#         rows = expanded.locator("#suburb-insights__table tbody tr")
#         yearly = []
#         for i in range(rows.count()):
#             cells = rows.nth(i).locator("td")
#             yearly.append(
#                 f"{safe_text(cells.nth(0))}="
#                 f"{safe_text(cells.nth(1))}"
#                 f"({safe_text(cells.nth(2))})"
#                 f"[{safe_text(cells.nth(3))}]"
#             )

#         data["yearly"] = "; ".join(yearly) if yearly else None

#         human_pause(0.4, 1.0)
#         button.click()
#         expanded.wait_for(state="hidden", timeout=5000)

#         return data

#     except Exception as e:
#         print(f"⚠️ Segment failed: {segment_name} -> {e}")
#         return {
#             "segment": segment_name,
#             "median_price": None,
#             "entry_level": None,
#             "high_end": None,
#             "sold_this_year": None,
#             "rental_median": None,
#             "auction_clearance": None,
#             "avg_days_on_market": None,
#             "yearly": None
#         }

# # ---------------- URL PROCESSOR ----------------

# def process_url(url, browser):
#     context = browser.new_context(
#         user_agent=(
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
#             "AppleWebKit/537.36 (KHTML, like Gecko) "
#             "Chrome/128.0.0.0 Safari/537.36"
#         ),
#         viewport={"width": 1366, "height": 768},
#         locale="en-AU",
#         timezone_id="Australia/Brisbane"
#     )

#     page = context.new_page()
#     page.add_init_script(
#         "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
#     )

#     results = []

#     try:
#         print(f"\nProcessing: {url}")
#         page.goto(url, timeout=30000, wait_until="networkidle")
#         human_pause(1.2, 2.5)

#         buttons = page.locator('button[data-testid="market-button"]')

#         if buttons.count() == 0:
#             results.append({
#                 "url": url,
#                 "segment": None,
#                 "median_price": None,
#                 "entry_level": None,
#                 "high_end": None,
#                 "sold_this_year": None,
#                 "rental_median": None,
#                 "auction_clearance": None,
#                 "avg_days_on_market": None,
#                 "yearly": None
#             })
#         else:
#             for i in range(buttons.count()):
#                 button = buttons.nth(i)
#                 segment_name = button.get_attribute("name") or f"segment_{i+1}"
#                 segment_data = scrape_market_segment(page, button, segment_name)
#                 results.append({ "url": url, **segment_data })
#                 human_pause(0.8, 1.8)

#     except Exception as e:
#         print(f"❌ Failed: {url} -> {e}")
#         results.append({
#             "url": url,
#             "segment": "ERROR",
#             "median_price": None,
#             "entry_level": None,
#             "high_end": None,
#             "sold_this_year": None,
#             "rental_median": None,
#             "auction_clearance": None,
#             "avg_days_on_market": None,
#             "yearly": None
#         })
#     finally:
#         context.close()

#     return results

# # ---------------- MAIN ----------------

# def main():
#     with open(INPUT_CSV, newline="", encoding="utf-8") as f:
#         urls = [row["link"] for row in csv.DictReader(f) if row.get("link")]

#     print(f"Found {len(urls)} URLs")

#     all_rows = []

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)  # headless=False = safer
#         for url in urls:
#             all_rows.extend(process_url(url, browser))
#             human_pause(2, 4)
#         browser.close()

#     fieldnames = [
#         "url", "segment", "median_price", "entry_level", "high_end",
#         "sold_this_year", "rental_median", "auction_clearance",
#         "avg_days_on_market", "yearly"
#     ]

#     with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(all_rows)

#     print(f"\n✅ Saved {len(all_rows)} rows to {OUTPUT_CSV}")

# if __name__ == "__main__":
#     main()

#######################

import csv
import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError

start_time = time.time()

INPUT_CSV = "url_domain_0_99.csv"
OUTPUT_CSV = "output_domain_0_99.csv"
BATCH_SIZE = 2
MAX_RETRIES = 2

# ---------------- USER AGENTS ----------------
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

# ---------------- HELPERS ----------------
def human_pause(a=0.6, b=1.8):
    time.sleep(random.uniform(a, b))

def safe_text(locator, timeout=2000):
    try:
        return locator.first.inner_text(timeout=timeout).strip()
    except Exception:
        return None

def value_by_label(container, label):
    return safe_text(
        container.locator(
            f'xpath=.//h4[contains(normalize-space(), "{label}")]/following-sibling::div'
        )
    )

# ---------------- MARKET SCRAPER ----------------
def scrape_market_segment(page, button, segment_name):
    try:
        button.scroll_into_view_if_needed()
        human_pause(0.3, 0.7)
        button.click()

        expanded = button.locator(
            "xpath=ancestor::tr/following-sibling::tr[contains(@class,'css-1wpy7ho')]"
        )
        expanded.wait_for(state="visible", timeout=6000)

        data = {
            "segment": segment_name,
            "median_price": value_by_label(expanded, "Median price"),
            "entry_level": value_by_label(expanded, "Entry level"),
            "high_end": value_by_label(expanded, "High end"),
            "sold_this_year": value_by_label(expanded, "Sold this year"),
            "rental_median": value_by_label(expanded, "Rental median price"),
            "auction_clearance": value_by_label(expanded, "Auction clearance"),
            "avg_days_on_market": value_by_label(expanded, "Average days on market"),
        }

        # ---- Yearly Table ----
        rows = expanded.locator("#suburb-insights__table tbody tr")
        yearly = []
        for i in range(rows.count()):
            cells = rows.nth(i).locator("td")
            yearly.append(
                f"{safe_text(cells.nth(0))}="
                f"{safe_text(cells.nth(1))}"
                f"({safe_text(cells.nth(2))})"
                f"[{safe_text(cells.nth(3))}]"
            )

        data["yearly"] = "; ".join(yearly) if yearly else None

        human_pause(0.2, 0.5)
        button.click()
        expanded.wait_for(state="hidden", timeout=4000)

        return data

    except Exception as e:
        print(f"⚠️ Segment error [{segment_name}]: {e}")
        return {
            "segment": segment_name,
            "median_price": None,
            "entry_level": None,
            "high_end": None,
            "sold_this_year": None,
            "rental_median": None,
            "auction_clearance": None,
            "avg_days_on_market": None,
            "yearly": None
        }

# ---------------- URL PROCESSOR ----------------
def process_url(browser, url):
    results = []

    for attempt in range(1, MAX_RETRIES + 1):
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1366, "height": 768},
            locale="en-AU",
            timezone_id="Australia/Brisbane"
        )

        page = context.new_page()
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

        try:
            print(f"\nProcessing ({attempt}/{MAX_RETRIES}): {url}")
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            human_pause(1.0, 2.0)

            buttons = page.locator('button[data-testid="market-button"]')

            if buttons.count() == 0:
                results.append(empty_row(url))
                return results

            for i in range(buttons.count()):
                btn = buttons.nth(i)
                segment = btn.get_attribute("name") or f"segment_{i+1}"
                data = scrape_market_segment(page, btn, segment)
                results.append({"url": url, **data})
                human_pause(0.6, 1.4)

            return results

        except TimeoutError:
            print("⏱ Timeout, retrying...")
        except Exception as e:
            print(f"❌ URL error: {e}")
        finally:
            context.close()

    return [error_row(url)]

# ---------------- ROW HELPERS ----------------
def empty_row(url):
    return {
        "url": url,
        "segment": None,
        "median_price": None,
        "entry_level": None,
        "high_end": None,
        "sold_this_year": None,
        "rental_median": None,
        "auction_clearance": None,
        "avg_days_on_market": None,
        "yearly": None
    }

def error_row(url):
    row = empty_row(url)
    row["segment"] = "ERROR"
    return row

# ---------------- CSV WRITER ----------------
def write_batch(path, rows, fieldnames):
    file_exists = Path(path).exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

# ---------------- MAIN ----------------
def main():
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        urls = [r["link"] for r in csv.DictReader(f) if r.get("link")]

    print(f"Found {len(urls)} URLs")

    fieldnames = [
        "url", "segment", "median_price", "entry_level", "high_end",
        "sold_this_year", "rental_median", "auction_clearance",
        "avg_days_on_market", "yearly"
    ]

    buffer = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for idx, url in enumerate(urls, 1):
            buffer.extend(process_url(browser, url))

            if len(buffer) >= BATCH_SIZE:
                print(f"💾 Writing {len(buffer)} records")
                write_batch(OUTPUT_CSV, buffer, fieldnames)
                buffer.clear()

        browser.close()

    if buffer:
        print(f"💾 Writing final {len(buffer)} records")
        write_batch(OUTPUT_CSV, buffer, fieldnames)

    print("\n✅ Done")

if __name__ == "__main__":
    main()

end_time = time.time()
elapsed = end_time - start_time
print(f"⏱ Total time: {elapsed:.2f} seconds")