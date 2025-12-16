from playwright.sync_api import sync_playwright
import pandas as pd
import random
import time
import os

start_time = time.time()

CSV_FILE = "url_suburbs.csv"
CSV_OUTPUT = "postcode_raw.csv"
RESTART_EVERY = 100
SAVE_EVERY = 100

df = pd.read_csv(CSV_FILE)
urls = df["href"].tolist()
total = len(urls)

data = []
record_count = 0

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.7 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/118.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.5; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:118.0) Gecko/118.0 Firefox/118.0",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
]

# Remove old output if exists
if os.path.exists(CSV_OUTPUT):
    os.remove(CSV_OUTPUT)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ua = random.choice(USER_AGENTS)
    context = browser.new_context(user_agent=ua)
    
    for idx, url in enumerate(urls, start=1):

        if idx % RESTART_EVERY == 0:
            browser.close()
            browser = p.chromium.launch(headless=True)
            ua = random.choice(USER_AGENTS)
            context = browser.new_context(user_agent=ua)

        print(f"{idx}/{total} - Running: {url}")
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            cards_text = page.locator(
                "div.resultsDetails.seoHideResults div.location.suburb-map-results"
            ).all_inner_texts()

            for raw in cards_text:
                lines = [l.strip() for l in raw.split("\n") if l.strip()]
                if len(lines) < 2:
                    continue

                postcode = lines[0]
                suburb, state = [x.strip() for x in lines[1].split(",")]

                category = next(
                    (x.replace("Category", "").strip()
                     for x in lines if x.startswith("Category")),
                    None
                )

                details = next(
                    (x.replace("Details", "").strip()
                     for x in lines if x.startswith("Details")),
                    None
                )

                data.append({
                    "suburb": suburb,
                    "state": state,
                    "postcode": postcode,
                    "category": category,
                    "details": details,
                    "url": url
                })

                record_count += 1

                # Save in batches
                if record_count % SAVE_EVERY == 0:
                    pd.DataFrame(data).to_csv(
                        CSV_OUTPUT,
                        mode="a",
                        index=False,
                        header=not os.path.exists(CSV_OUTPUT)
                    )
                    data.clear()
                    print(f"Saved {record_count} records")

        except Exception as e:
            print(f"Error scraping {url}: {e}")

        finally:
            page.close()

        time.sleep(0.05)

    # Final flush
    if data:
        pd.DataFrame(data).to_csv(
            CSV_OUTPUT,
            mode="a",
            index=False,
            header=not os.path.exists(CSV_OUTPUT)
        )
        data.clear()
    browser.close()
end_time = time.time()
elapsed = end_time - start_time
print(f"Elapsed time: {elapsed:.2f} seconds")
print(f"Finished. Total records saved: {record_count}")