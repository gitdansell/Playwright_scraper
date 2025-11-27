import asyncio
from playwright.async_api import async_playwright

TARGET_URL = "https://www.barchart.com/stocks/quotes/ATD.TO/profile"
WIDGET_CONTAINER_SELECTOR = '[data-widget-name="Dividend History"]'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print(f"Navigating to {TARGET_URL}...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")

        print("Waiting for the Dividend History widget to be visible...")
        try:
            await page.wait_for_selector(WIDGET_CONTAINER_SELECTOR, timeout=15000)
            print("Widget found.")
        except Exception as e:
            print(f"Widget not found: {e}")
            await page.screenshot(path="widget_error.png")
            await browser.close()
            return

        print("Extracting widget HTML content...")
        widget_html = await page.inner_html(WIDGET_CONTAINER_SELECTOR)
        print("Widget HTML (truncated):")
        print(widget_html[:1000])  # Preview first 1000 characters

        await page.screenshot(path="widget_snapshot.png")
        input("Press Enter to close the browser...")
        await browser.close()

asyncio.run(main())
