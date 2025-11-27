from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# The target URL.
TARGET_URL = "https://www.barchart.com/stocks/quotes/ATD.TO/profile"

# Target the entire content container for the Recent Dividend History widget
WIDGET_CONTAINER_SELECTOR = 'div.bc-side-widget-header:has-text("Recent Dividend History") + div.bc-side-widget-content'
# The table is expected to be inside this container
TABLE_SELECTOR = 'table.table'


def get_dividend_data_final(url: str) -> list[dict]:
    """
    Uses Playwright to get the HTML of the dividend widget and BeautifulSoup
    to parse the Date and Value columns.

    :param url: The Barchart stock profile URL.
    :return: A list of dictionaries with 'Date' and 'Value' for each dividend.
    """
    dividend_data = []

    try:
        with sync_playwright() as p:
            print("Launching browser and navigating...")
            # Set headless=False for debugging, change to True for production scraping.
            browser = p.chromium.launch(headless=False) # Changed back to True for final script
            page = browser.new_page()
            
            page.goto(url, wait_until="domcontentloaded")
            
            # Wait for the entire widget container to be visible. This is often more reliable
            # than waiting for a deeply nested <table> element.
            print("Waiting for the Dividend History widget to be visible...")
            page.wait_for_selector(WIDGET_CONTAINER_SELECTOR, timeout=15000)

            # Get the inner HTML content of the widget container
            print("Extracting widget HTML content...")
            widget_html = page.inner_html(WIDGET_CONTAINER_SELECTOR)
            
            browser.close()

            # Parse the extracted HTML snippet (which is just the widget)
            soup = BeautifulSoup(widget_html, 'html.parser')
            dividend_table = soup.find('table', class_='table')

            if not dividend_table:
                print("Error: Could not find the table inside the widget content.")
                return []
            
            # Extract data: columns are Ex-Dividend Date (Col 0) and Amount (Col 1)
            rows = dividend_table.find('tbody').find_all('tr')
            print(f"Successfully found {len(rows)} dividend records.")

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    date = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)
                    
                    # Basic cleaning
                    value = value.replace('$', '').replace('C', '').strip()

                    dividend_data.append({'Date': date, 'Value': value})
                
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        # If an error happens, the browser might still be open in headful mode, 
        # so it's good practice to close it in the error handler if possible, 
        # though the 'with' block usually handles this.
        try:
            browser.close()
        except:
            pass # Ignore if already closed

    return dividend_data

# --- Run the scraper ---
if __name__ == "__main__":
    dividends = get_dividend_data_final(TARGET_URL)

    if dividends:
        print("\n--- Extracted Dividend Data (Ex-Dividend Date, Value) ---")
        print(f"{'Date':<15}{'Value':<10}")
        print("-" * 25)
        for item in dividends:
            print(f"{item['Date']:<15}{item['Value']:<10}")
    else:
        print("\nNo dividend data could be extracted.")