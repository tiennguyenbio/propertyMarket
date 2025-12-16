"""
PROPERTY PRICE & MARKET DATA STRUCTURE

1. House Price Guide
   1.1 Median Price Snapshot
       - Buy:  all, 2-bed, 3-bed, 4-bed
       - Rent: all, 2-bed, 3-bed, 4-bed

   1.2 Five-Year Median Price Trend
       - Buy:  all, 2-bed, 3-bed, 4-bed
       - Rent: all, 2-bed, 3-bed, 4-bed

   1.3 Property Market Insights (Houses)
       - Buy:  all, 2-bed, 3-bed, 4-bed
       - Rent: all, 2-bed, 3-bed, 4-bed

2. Unit & Apartment Price Guide
   2.1 Median Price Snapshot
       - Buy:  all, 1-bed, 2-bed, 3-bed
       - Rent: all, 1-bed, 2-bed, 3-bed

   2.2 Five-Year Median Price Trend
       - Buy:  all, 1-bed, 2-bed, 3-bed
       - Rent: all, 1-bed, 2-bed, 3-bed

   2.3 Property Market Insights (Units)
       - Buy:  all, 1-bed, 2-bed, 3-bed
       - Rent: all, 1-bed, 2-bed, 3-bed

3. Median Price Summary Table
   - Buy  (6 x 2): 2-bed-house, 3-bed-house, 4-bed-house, 1-bed-unit, 2-bed-unit, 3-bed-unit
   - Rent (6 x 2): 2-bed-house, 3-bed-house, 4-bed-house, 1-bed-unit, 2-bed-unit, 3-bed-unit

4. Property Market Summary
   - <p> text </p>
"""

# ========================== COMBINE (1. HOUSE PRICE GUIDE)===========================

import time
import json
from playwright.sync_api import sync_playwright, TimeoutError

URL = "https://www.realestate.com.au/act/curtin-2605/"
BEDROOMS = ["all", 2, 3, 4]

# -------------------------
# Helpers
# -------------------------
def get_text(locator, timeout=60000):
    try:
        text = locator.text_content(timeout=timeout)
        return text.strip() if text else None
    except TimeoutError:
        return None

# -------------------------
# Scrape Median rental price snapshot - House price guide
# -------------------------
def scrape_insights(page):
    """
    Scrape insight cards for BOTH Buy and Rent
    Structure:
    {
      "buy":  { "all-bed": [...], "2-bed": [...], "3-bed": [...], "4-bed": [...] },
      "rent": { "all-bed": [...], "2-bed": [...], "3-bed": [...], "4-bed": [...] }
    }
    """
    insights_result = {}

    for tab_type in ["Buy", "Rent"]:
        insights_result[tab_type.lower()] = {}

        # Switch tab
        page.locator(
            "#listing-switcher-house-price-guide button[role='tab']",
            has_text=tab_type
        ).click()
        time.sleep(0.5)

        for beds in BEDROOMS:
            bed_key = "all-bed" if beds == "all" else f"{beds}-bed"
            bed_id = "all" if beds == "all" else beds

            container = f"#house-price-data-{tab_type.lower()}-{bed_id}-bedrooms"

            try:
                page.wait_for_selector(container, state="attached", timeout=5000)

                cards = page.locator(
                    f'{container} div[data-testid="insight-card"]'
                )

                insights = []
                for i in range(cards.count()):
                    card = cards.nth(i)
                    insights.append({
                        "value": card.locator("span.dvLQhh").text_content().strip(),
                        "description": card.locator("span.jMuOMW").text_content().strip()
                    })

                insights_result[tab_type.lower()][bed_key] = insights

            except Exception as e:
                print(f"Insight error ({tab_type} {bed_key}): {e}")
                insights_result[tab_type.lower()][bed_key] = []

    return insights_result


# -------------------------
# Scrape median snapshot
# -------------------------
def scrape_median_snapshot(page):
    snapshot = {}

    for data_type in ["buy", "rent"]:
        snapshot[data_type] = {}

        for beds in ["all", "2", "3", "4"]:
            selector_base = f"#house-price-data-{data_type}-{beds}-bedrooms"

            snapshot[data_type][f"{beds}-bed"] = {
                "median_price": get_text(
                    page.locator(
                        f"{selector_base} span[data-testid='price-text-{data_type}-house-{beds}-bed']"
                    )
                ),
                "median_time": get_text(
                    page.locator(
                        f"{selector_base} span.indexstyles__DateText-sc-10e5b9w-5"
                    )
                ),
                "past_12m_growth": get_text(
                    page.locator(
                        f"{selector_base} div.MedianPriceGrowth__GrowthWrapper-sc-1styeqa-0"
                    )
                )
            }

    return snapshot


# -------------------------
# Scrape price charts
# -------------------------
def scrape_price_charts(page, tab_type: str, steps: int = 100):
    assert tab_type in ["Buy", "Rent"]

    results = {}

    page.locator(
        "#listing-switcher-house-price-guide button[role='tab']",
        has_text=tab_type
    ).click()
    time.sleep(0.5)

    for beds in BEDROOMS:
        bed_key = "all-bed" if beds == "all" else f"{beds}-bed"
        bed_id = "all" if beds == "all" else beds
        container = f"#house-price-data-{tab_type.lower()}-{bed_id}-bedrooms"

        try:
            page.wait_for_selector(container, state="attached", timeout=5000)

            page.evaluate(f"""() => {{
                const el = document.querySelector("{container}");
                if (el) el.removeAttribute("hidden");
            }}""")

            page.locator(container).scroll_into_view_if_needed()
            time.sleep(0.5)

            chart = page.locator(f"{container} .recharts-wrapper").first
            svg = chart.locator("svg")
            box = svg.bounding_box()

            tooltip_period = page.locator(".CustomTooltip__HeaderContainer-sc-124e1m-1")
            tooltip_price = page.locator(".CustomTooltip__BodyContainer-sc-124e1m-4")

            x_start = box["x"] + box["width"] * 0.05
            x_end   = box["x"] + box["width"] * 0.98
            y = box["y"] + box["height"] * 0.5

            seen, data = set(), []

            for i in range(steps):
                x = x_start + (x_end - x_start) * i / (steps - 1)
                page.mouse.move(x, y)
                time.sleep(0.06)

                if tooltip_period.is_visible():
                    period = tooltip_period.inner_text().strip()
                    price = tooltip_price.inner_text().strip()
                    if (period, price) not in seen:
                        seen.add((period, price))
                        data.append({"period": period, "price": price})

            results[bed_key] = data

        except Exception as e:
            print(f"Chart error ({tab_type} {bed_key}): {e}")
            results[bed_key] = []

    return results


# -------------------------
# Main runner
# -------------------------
with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)
    page = browser.new_page(viewport={"width": 1380, "height": 800})
    page.set_default_timeout(90000)

    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_selector("#house-price-data-buy-all-bedrooms")

    final_result = {
        "url": URL,
        "title": page.title(),
        "insights": scrape_insights(page),
        "median_snapshot": scrape_median_snapshot(page),
        "price_charts": {
            "buy": scrape_price_charts(page, "Buy"),
            "rent": scrape_price_charts(page, "Rent")
        }
    }

    browser.close()


# -------------------------
# Export JSON
# -------------------------
output_file = "curtin_2605_full_property_data.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(final_result, f, indent=2, ensure_ascii=False)

print(f"Exported to {output_file}")

# ============================= DRAFT ==================================

# from playwright.sync_api import sync_playwright
# import time

# url = "https://www.realestate.com.au/act/curtin-2605/"

# with sync_playwright() as p:
#     browser = p.firefox.launch(headless=False)
#     page = browser.new_page()
#     page.goto(url)
#     # data = page.locator("div.heading__HeadingWrapper-sc-14r98bt-3.esflH").all_inner_texts()

#     # med_price_allbed = page.locator("#house-price-data-buy-all-bedrooms span[data-testid='price-text-buy-house-all-bed']").text_content()
#     # med_time_allbed = page.locator("#house-price-data-buy-all-bedrooms span.indexstyles__DateText-sc-10e5b9w-5.GMmEA").text_content()
#     # past_12m_allbed = page.locator("#house-price-data-buy-all-bedrooms div.MedianPriceGrowth__GrowthWrapper-sc-1styeqa-0.kXLSlS").text_content()

#     # med_price_2bed = page.locator("#house-price-data-buy-2-bedrooms span[data-testid='price-text-buy-house-2-bed']").text_content()
#     # med_time_2bed = page.locator("#house-price-data-buy-2-bedrooms span.indexstyles__DateText-sc-10e5b9w-5.GMmEA").text_content()
#     # past_12m_2bed = page.locator("#house-price-data-buy-2-bedrooms div.MedianPriceGrowth__GrowthWrapper-sc-1styeqa-0.kXLSlS").text_content()

#     # med_price_3bed = page.locator("#house-price-data-buy-3-bedrooms span[data-testid='price-text-buy-house-3-bed']").text_content()
#     # med_time_3bed = page.locator("#house-price-data-buy-3-bedrooms span.indexstyles__DateText-sc-10e5b9w-5.GMmEA").text_content()
#     # past_12m_3bed = page.locator("#house-price-data-buy-3-bedrooms div.MedianPriceGrowth__GrowthWrapper-sc-1styeqa-0.kXLSlS").text_content()

#     # med_price_4bed = page.locator("#house-price-data-buy-4-bedrooms span[data-testid='price-text-buy-house-4-bed']").text_content()
#     # med_time_4bed = page.locator("#house-price-data-buy-4-bedrooms span.indexstyles__DateText-sc-10e5b9w-5.GMmEA").text_content()
#     # past_12m_4bed = page.locator("#house-price-data-buy-4-bedrooms div.MedianPriceGrowth__GrowthWrapper-sc-1styeqa-0.kXLSlS").text_content()

#     # print(med_price_2bed)
#     # print(med_time_2bed)
#     # print(past_12m_2bed)

#     # rent_price_allbed = page.locator("#house-price-data-rent-all-bedrooms span[data-testid='price-text-rent-house-all-bed']").text_content()
#     # rent_time_allbed = page.locator("#house-price-data-rent-all-bedrooms span.indexstyles__DateText-sc-10e5b9w-5.GMmEA").text_content()
#     # rent_past_12m_allbed = page.locator("#house-price-data-rent-all-bedrooms div.MedianPriceGrowth__GrowthWrapper-sc-1styeqa-0.kXLSlS").text_content()

#     # print(rent_price_allbed)
#     # print(rent_time_allbed)
#     # print(rent_past_12m_allbed)


#     # page.close()
#     # browser.close()

# #======================== (1.1) GET MEDIAN PRICE SNAPSHOT ==================================================
"""buy:
    {all bedrooms:
    2-bedrooms:
    3-bedrooms:
    4-bedrooms:}

rent:
    {all bedrooms:
    2-bedrooms:
    3-bedrooms:
    4-bedrooms:}"""

# from playwright.sync_api import sync_playwright, TimeoutError

# url = "https://www.realestate.com.au/act/curtin-2605/"

# def get_text(locator, timeout=60000):
#     """Safely get text content from a locator."""
#     try:
#         return locator.text_content(timeout=timeout).strip()
#     except TimeoutError:
#         return None

# with sync_playwright() as p:
#     browser = p.firefox.launch(headless=False)
#     page = browser.new_page()
#     page.set_default_timeout(90000)
    
#     page.goto(url, wait_until="domcontentloaded")
#     page.wait_for_selector("#house-price-data-buy-all-bedrooms")  # wait for main element
    
#     title = page.title()
    
#     results = {}
#     for data_type in ["buy", "rent"]:
#         results[data_type] = {}
#         for beds in ["all", "2", "3", "4"]:
#             selector_base = f"#house-price-data-{data_type}-{beds}-bedrooms"
#             results[data_type][beds] = {
#                 "median_price": get_text(page.locator(f"{selector_base} span[data-testid='price-text-{data_type}-house-{beds}-bed']")),
#                 "median_time": get_text(page.locator(f"{selector_base} span.indexstyles__DateText-sc-10e5b9w-5.GMmEA")),
#                 "past_12m_growth": get_text(page.locator(f"{selector_base} div.MedianPriceGrowth__GrowthWrapper-sc-1styeqa-0.kXLSlS"))
#             }
    
#     print("Page Title:", title)
#     for data_type, beds_data in results.items():
#         print(f"\n--- {data_type.upper()} Data ---")
#         for beds, data in beds_data.items():
#             print(f"{beds}-bedroom {data_type}:")
#             for key, value in data.items():
#                 print(f"  {key}: {value}")
    
#     page.close()
#     browser.close()


# #=================== (1.2) GET 5 YEAR MEDIAN PRICE TREND (CHART) ===============================================
"""Output
{
  "all-bed": [
    { "period": "Dec 2019", "price": "$1.05m" }
  ],
  "2-bed": [...],
  "3-bed": [...],
  "4-bed": [...]
}
# """

# import time
# from playwright.sync_api import sync_playwright

# def scrape_price_chart_all_bedrooms(
#     url: str,
#     tab_type: str = "Buy",
#     steps: int = 100,
#     headless: bool = False
# ):
#     """
#     Scrape house or rent price chart data for all bedroom types from realestate.com.au.

#     Returns:
#         Dict[str, List[Dict]]:
#         {
#           "all-bed": [...],
#           "2-bed": [...],
#           "3-bed": [...],
#           "4-bed": [...]
#         }
#     """
#     assert tab_type in ["Buy", "Rent"], "tab_type must be 'Buy' or 'Rent'"

#     # include all-bedroom
#     bedroom_types = ["all", 2, 3, 4]
#     results = {}

#     with sync_playwright() as p:
#         browser = p.firefox.launch(headless=headless)
#         page = browser.new_page(viewport={"width": 1380, "height": 800})
#         page.goto(url, wait_until="domcontentloaded")

#         # Select Buy / Rent tab
#         tab = page.locator(
#             "#listing-switcher-house-price-guide button[role='tab']",
#             has_text=tab_type
#         )
#         tab.click()
#         time.sleep(0.5)

#         for beds in bedroom_types:
#             bed_key = f"{beds}-bed" if beds != "all" else "all-bed"
#             bed_id = "all" if beds == "all" else beds

#             container = f"#house-price-data-{tab_type.lower()}-{bed_id}-bedrooms"

#             try:
#                 page.wait_for_selector(container, state="attached", timeout=5000)

#                 # Unhide chart
#                 page.evaluate(f"""() => {{
#                     const el = document.querySelector("{container}");
#                     if (el) el.removeAttribute("hidden");
#                 }}""")

#                 page.locator(container).scroll_into_view_if_needed()
#                 time.sleep(0.5)

#                 chart = page.locator(f"{container} .recharts-wrapper").first
#                 svg = chart.locator("svg")
#                 svg_box = svg.bounding_box()

#                 tooltip_period = page.locator(".CustomTooltip__HeaderContainer-sc-124e1m-1")
#                 tooltip_price = page.locator(".CustomTooltip__BodyContainer-sc-124e1m-4")

#                 x_start = svg_box["x"] + svg_box["width"] * 0.05
#                 x_end   = svg_box["x"] + svg_box["width"] * 0.98
#                 y = svg_box["y"] + svg_box["height"] * 0.5

#                 bedroom_results = []
#                 seen = set()

#                 for i in range(steps):
#                     x = x_start + (x_end - x_start) * i / (steps - 1)
#                     page.mouse.move(x, y)
#                     time.sleep(0.06)

#                     if tooltip_period.is_visible():
#                         period = tooltip_period.inner_text().strip()
#                         price = tooltip_price.inner_text().strip()
#                         key = (period, price)

#                         if key not in seen:
#                             seen.add(key)
#                             bedroom_results.append({
#                                 "period": period,
#                                 "price": price
#                             })

#                 results[bed_key] = bedroom_results

#             except Exception as e:
#                 print(f"Container not found or error for {bed_key}: {e}")
#                 results[bed_key] = []

#         browser.close()
#         return results


# # -------------------------
# # Example usage
# # -------------------------
# URL = "https://www.realestate.com.au/act/curtin-2605/"

# buy_data = scrape_price_chart_all_bedrooms(URL, tab_type="Buy")
# rent_data = scrape_price_chart_all_bedrooms(URL, tab_type="Rent")

# print("Buy data points:", buy_data)
# print("Rent data points:", rent_data)

# result_json = {
#     "Buy": buy_data,
#     "Rent": rent_data
# }

# import json
# print(json.dumps(result_json, indent=2))

# =================== (1.3) GET PROPERTY MARKET INSIGHT ========================
"""
buy:
    {all bedrooms:
    2-bedrooms:
    3-bedrooms:
    4-bedrooms:}

rent:
    {all bedrooms:
    2-bedrooms:
    3-bedrooms:
    4-bedrooms:}
"""

# from playwright.sync_api import sync_playwright

# url = "https://www.realestate.com.au/act/curtin-2605/"

# BEDROOMS = ["all", 2, 3, 4]

# with sync_playwright() as p:
#     browser = p.firefox.launch(headless=False)
#     page = browser.new_page()
#     page.goto(url, wait_until="domcontentloaded")

#     # Select Buy tab
#     tab = page.locator(
#         "#listing-switcher-house-price-guide button[role='tab']",
#         has_text="Buy"
#     )
#     tab.click()

#     results = {}

#     for beds in BEDROOMS:
#         bed_key = "all-bed" if beds == "all" else f"{beds}-bed"
#         bed_id = "all" if beds == "all" else beds

#         container = f"#house-price-data-buy-{bed_id}-bedrooms"

#         try:
#             page.wait_for_selector(container, state="attached", timeout=5000)

#             cards = page.locator(
#                 f'{container} div[data-testid="insight-card"]'
#             )
#             count = cards.count()

#             insights = []
#             for i in range(count):
#                 card = cards.nth(i)

#                 value = card.locator("span.dvLQhh").text_content().strip()
#                 description = card.locator("span.jMuOMW").text_content().strip()

#                 insights.append({
#                     "value": value,
#                     "description": description
#                 })

#             results[bed_key] = insights

#         except Exception as e:
#             print(f"Insight error for {bed_key}: {e}")
#             results[bed_key] = []

#     page.close()
#     browser.close()

# # -------------------------
# # Print results
# # -------------------------
# for bed, insights in results.items():
#     print(f"\n{bed.upper()}")
#     for item in insights:
#         print(item)


# ================= (3) GET PROPERTY MEDIAN PRICE SNAPSHOT ========================    
"""Buy Data: [{'name': '2 bed house', 'price': 'Unavailable'}, {'name': '3 bed house', 'price': '$1,210,000'}, {'name': '4 bed house', 'price': '$1,477,500'}, {'name': '1 bed unit', 'price': 'Unavailable'}, {'name': '2 bed unit', 'price': '$355,000'}, {'name': '3 bed unit', 'price': 'Unavailable'}]
Rent Data: [{'name': '2 bed house', 'price': 'Unavailable'}, {'name': '3 bed house', 'price': '$680 per week'}, {'name': '4 bed house', 'price': '$865 per week'}, {'name': '1 bed unit', 'price': '$455 per week'}, {'name': '2 bed unit', 'price': '$527 per week'}, {'name': '3 bed unit', 'price': 'Unavailable'}]
"""

# from playwright.sync_api import sync_playwright

# url = "https://www.realestate.com.au/act/curtin-2605/"

# def scrape_property_table(tab_type="Buy"):
#     """
#     Scrape property prices from Curtin for the specified tab type ('Buy' or 'Rent').
#     Returns a list of dictionaries with property name and price.
#     """
#     assert tab_type in ["Buy", "Rent"], "tab_type must be 'Buy' or 'Rent'"

#     with sync_playwright() as p:
#         browser = p.firefox.launch(headless=False)
#         page = browser.new_page()
#         page.goto(url)

#         # Click the appropriate tab
#         tab = page.locator("#listing-switcher-house-price-guide button[role='tab']", has_text=tab_type)
#         tab.click()

#         # Wait for the table to load
#         page.wait_for_selector("div.PropertyPriceDetail__MetricsTableContainer-sc-1is2q6f-0 table tbody tr")

#         # Get all rows
#         rows = page.locator("div.PropertyPriceDetail__MetricsTableContainer-sc-1is2q6f-0 table tbody tr")
#         data = []

#         for i in range(rows.count()):
#             row = rows.nth(i)
#             name = row.locator("div[data-testid]").inner_text().strip()
#             price = row.locator("span").inner_text().strip()
#             data.append({"name": name, "price": price})

#         page.close()
#         browser.close()

#         return data

# # Example usage
# buy_data = scrape_property_table("Buy")
# rent_data = scrape_property_table("Rent")

# print("Buy Data:", buy_data)
# print("Rent Data:", rent_data)


# ================== (4) GET PROPERTY MARKET SUMMARY ========================  
"""Last month Curtin had 31 properties available for rent and 34 properties for sale. 
Median property prices over the last year range from $1,422,500 for houses to $362,500 
for units. If you are looking for an investment property, consider houses in Curtin rent 
out for $750 PW with an annual rental yield of 3.1% and units rent for $495 PW with a 
rental yield of 6.2%. Curtin has seen an annual compound growth rate of 0.5% for houses 
and -7.1% for units."""

# from playwright.sync_api import sync_playwright

# url = "https://www.realestate.com.au/act/curtin-2605/"

# with sync_playwright() as p:
#     browser = p.firefox.launch(headless=False)
#     page = browser.new_page()
#     page.goto(url)
#     data = page.locator("p[data-testid='marketSummary']").inner_text().strip()
#     print(data)
#     page.close()
#     browser.close()