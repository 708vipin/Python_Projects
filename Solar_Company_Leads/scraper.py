from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False, slow_mo = 500)
    page = browser.new_page()
    web_site = page.goto("https://www.newenergytech.org.au/find-an-approved-seller")