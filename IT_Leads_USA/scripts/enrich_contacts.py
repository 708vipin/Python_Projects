import re
import time
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path

HEADERS = {"User-Agent": "Mozilla/5.0"}
SEED_CSV = Path("data/processed/companies_seed.csv")
OUT_CSV = Path("data/processed/it_companies_enriched.csv")

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"""
    (?:(?:\+1[\s\-\.])?        # optional +1
     (?:\(?\d{3}\)?[\s\-\.]?)  # area code
     \d{3}[\s\-\.]?\d{4})      # local
""", re.X)

CANDIDATE_PATHS = ["contact", "contact-us", "contactus", "about", "company", "team"]

def get(url, timeout=20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code == 200 and "text/html" in r.headers.get("Content-Type", ""):
            return r.text
    except requests.RequestException:
        return None
    return None

def best_contact_url(site_url: str) -> str | None:
    """Find a likely Contact page from homepage links or common paths."""
    if not site_url:
        return None
    if not site_url.startswith("http"):
        site_url = "http://" + site_url

    html = get(site_url)
    if not html:
        return None

    soup = BeautifulSoup(html, "lxml")

    # 1) Look for nav/footer links containing 'contact'
    for a in soup.select("a[href]"):
        text = (a.get_text(" ", strip=True) or "").lower()
        href = a["href"].lower()
        if "contact" in text or "contact" in href:
            return urljoin(site_url, a["href"])

    # 2) Try common fallbacks
    base = site_url.rstrip("/")
    for slug in CANDIDATE_PATHS:
        candidate = f"{base}/{slug}"
        if get(candidate):
            return candidate

    return site_url  # fallback to homepage

def extract_email_phone_address(html: str) -> tuple[str | None, str | None, str | None]:
    if not html:
        return None, None, None
    # Simple text scrape
    text = BeautifulSoup(html, "lxml").get_text("\n", strip=True)

    emails = EMAIL_RE.findall(text)
    phones = PHONE_RE.findall(text)

    email = emails[0] if emails else None
    phone = phones[0] if phones else None

    # Very light address heuristic (look for lines with state abbreviations + ZIP)
    address = None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines:
        # e.g., San Jose, CA 95110
        if re.search(r",\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?$", ln):
            address = ln
            break

    return email, phone, address

def main():
    df = pd.read_csv(SEED_CSV)
    rows = []
    for i, row in df.iterrows():
        name = row.get("Company")
        site = row.get("Website")
        wiki = row.get("Wikipedia")
        contact_url = best_contact_url(site) if pd.notna(site) else None

        html = get(contact_url) if contact_url else None
        email, phone, address = extract_email_phone_address(html) if html else (None, None, None)

        rows.append({
            "Company": name,
            "Website": site,
            "Contact_URL": contact_url,
            "Email": email,
            "Phone": phone,
            "Address": address,
            "Wikipedia": wiki
        })

        print(f"[{i+1}/{len(df)}] {name}: email={email} phone={phone}")
        time.sleep(1)  # be polite

    out = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)
    print(f"Saved enriched rows to {OUT_CSV}")

if __name__ == "__main__":
    main()
