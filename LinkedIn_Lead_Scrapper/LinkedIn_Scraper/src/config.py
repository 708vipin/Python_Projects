# src/config.py
"""
Configuration for LinkedIn_Scraper (keep this file small and non-sensitive).

IMPORTANT:
- Put credentials and real proxy strings in environment variables (or a .env file you do NOT commit).
- This module defines defaults and helper values used across the project.
"""

import os
import json
from pathlib import Path
from typing import List, Optional

# -----------------------
# Basic paths (auto-resolves relative to repo)
# -----------------------
BASE_DIR = Path(__file__).resolve().parents[1]  # LinkedIn_Scraper/
RAW_DIR = BASE_DIR / "raw"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Ensure folders exist when module is imported
for _d in (RAW_DIR, DATA_DIR, LOGS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# -----------------------
# Credentials (load from environment)
# -----------------------
# Set these in your terminal / CI, do NOT hard-code them here.
LINKEDIN_EMAIL: str = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD: str = os.getenv("LINKEDIN_PASSWORD", "")

# Optional: path to saved session/cookies to avoid re-login every run
COOKIE_PATH: Path = Path(os.getenv("COOKIE_PATH", str(BASE_DIR / "raw" / "cookies.json")))

# -----------------------
# Browser / automation choices
# -----------------------
# 'playwright' recommended for stealth / modern API; fallback 'selenium' if you prefer.
BROWSER: str = os.getenv("BROWSER", "playwright")  # values: 'playwright' or 'selenium'
HEADLESS: bool = os.getenv("HEADLESS", "1") != "0"  # set '0' to run visibly (good for debugging)

# -----------------------
# Proxy rotation (recommended for large-scale runs)
# -----------------------
# Provide proxies as a comma-separated env var, or JSON array.
# Example:
#   PROXIES="http://user:pass@1.2.3.4:8000,http://user:pass@5.6.7.8:8000"
# or
#   PROXIES='["http://user:pass@1.2.3.4:8000","http://user:pass@5.6.7.8:8000"]'
PROXIES_RAW: str = os.getenv("PROXIES", "").strip()

def parse_proxies(raw: str) -> List[str]:
    """Return a list of proxy strings from raw env value (robust to JSON or CSV)."""
    if not raw:
        return []
    raw = raw.strip()
    # try JSON array first
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
            return [p.strip() for p in parsed if p and p.strip()]
        except Exception:
            pass
    # fallback: comma-separated
    return [p.strip() for p in raw.split(",") if p.strip()]

PROXIES: List[str] = parse_proxies(PROXIES_RAW)

# -----------------------
# User-Agent rotation (small sample; expand as needed)
# -----------------------
# Rotating UA reduces fingerprinting. Keep a longer list for large runs.
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    # add more real UA strings here for production
]

# -----------------------
# Timeouts, delays, and rate-limiting
# -----------------------
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))         # seconds for web requests
PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))     # browser page load timeout
MIN_DELAY: float = float(os.getenv("MIN_DELAY", "1.0"))                # min random delay between actions (sec)
MAX_DELAY: float = float(os.getenv("MAX_DELAY", "4.0"))                # max random delay (sec)

# -----------------------
# Concurrency / scaling
# -----------------------
MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))   # parallel workers (threads/processes)
BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "100"))   # items to process/save per batch

# -----------------------
# Retry / backoff behavior
# -----------------------
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF: float = float(os.getenv("RETRY_BACKOFF", "2.0"))  # multiplier for exponential backoff

# -----------------------
# Sales Navigator detection and filtering
# -----------------------
# We will attempt to infer Sales Navigator usage (CHECK_SALES_NAVIGATOR=True).
# Implementation: check for Sales Nav profile elements / account-only UI, cookies or some Sales Nav-only page access.
CHECK_SALES_NAVIGATOR: bool = os.getenv("CHECK_SALES_NAVIGATOR", "1") != "0"

# -----------------------
# Output filenames (use DATA_DIR)
# -----------------------
OUTPUT_CSV: Path = DATA_DIR / os.getenv("OUTPUT_CSV", "linkedin_prospects_sample.csv")
OUTPUT_JSON: Path = DATA_DIR / os.getenv("OUTPUT_JSON", "linkedin_prospects_sample.json")

# -----------------------
# Logging & debug
# -----------------------
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # used by loguru or logging setup
SAVE_RAW_HTML: bool = os.getenv("SAVE_RAW_HTML", "0") != "0"  # set to 1 to save raw HTML per profile (for debugging)

# -----------------------
# Lightweight helper functions
# -----------------------
import random

def get_random_user_agent() -> str:
    """Return a random user agent from the list (used by requests/playwright)."""
    return random.choice(USER_AGENTS)

def get_proxy_for_worker(worker_index: int) -> Optional[str]:
    """
    Simple deterministic proxy picker for worker_index (0..n).
    Returns None if no proxies configured.
    """
    if not PROXIES:
        return None
    return PROXIES[worker_index % len(PROXIES)]

# -----------------------
# Safety note (dont commit secrets)
# -----------------------
"""
SECURITY REMINDER:
- Never commit LINKEDIN_EMAIL, LINKEDIN_PASSWORD, PROXIES with credentials, or COOKIE files to GitHub.
- Use environment variables in local dev or CI secrets in production.
- If you want a local .env for convenience, install 'python-dotenv' and load it in your entrypoint (main.py) only in local dev.
"""

# End of config.py
