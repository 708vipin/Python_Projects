from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless = False, slow_mo = 500)
    page = browser.new_page()
    web = page.goto("https://www.yellowpages.com.au/search/listings?clue=Interior+Designers&locationClue=&lat=&lon=")
