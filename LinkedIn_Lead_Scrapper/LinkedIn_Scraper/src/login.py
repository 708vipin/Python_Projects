# src/login.py
"""
Handles LinkedIn login using Playwright.
- Uses credentials from config.py (loaded from environment variables).
- Saves session cookies to avoid repeated logins.
"""

from playwright.sync_api import sync_playwright
import json
from pathlib import Path
import config


def login_and_save_cookies():
    """Login to LinkedIn and save cookies for reuse."""
    with sync_playwright() as p:
        # Launch browser (headless or visible based on config)
        browser = p.chromium.launch(headless=config.HEADLESS)
        context = browser.new_context()

        # Go to LinkedIn login page
        page = context.new_page()
        page.goto("https://www.linkedin.com/login")

        # Fill in email and password (from environment variables)
        page.fill("input#username", config.LINKEDIN_EMAIL)
        page.fill("input#password", config.LINKEDIN_PASSWORD)

        # Click login button
        page.click("button[type='submit']")

        # Wait until home feed loads (basic check: presence of search box)
        page.wait_for_selector("input[placeholder='Search']", timeout=15000)

        # Save cookies for later reuse
        cookies = context.cookies()
        Path(config.COOKIE_PATH).write_text(json.dumps(cookies, indent=2))

        print(f"✅ Login successful. Cookies saved at {config.COOKIE_PATH}")

        # Cleanup
        browser.close()


def load_cookies(context):
    """Load saved cookies into browser context (to skip login)."""
    cookie_file = Path(config.COOKIE_PATH)
    if cookie_file.exists():
        cookies = json.loads(cookie_file.read_text())
        context.add_cookies(cookies)
        print("✅ Cookies loaded from file.")
    else:
        print("⚠️ No cookies found, need to login first.")



