import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

SEED_URL = "https://en.wikipedia.org/wiki/Category:Software_companies_based_in_California"
HEADERS = {"User-Agent": "Mozilla/5.0"}
def get_company_links():
    r = requests.get(SEED_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    # Grab only anchors that actually have an href
    items = soup.select("div.mw-category a[href]")
    links = []
    for a in items:
        href = a.get("href", "")
        name = a.get_text(strip=True)
        if href.startswith("/wiki/") and not href.startswith("/wiki/Category:"):
            links.append(("https://en.wikipedia.org" + href, name))
    # de-duplicate by URL
    seen = set()
    deduped = []
    for url, name in links:
        if url not in seen:
            seen.add(url)
            deduped.append((url, name))
    return deduped


def get_official_site(wiki_url):
    r = requests.get(wiki_url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    s = BeautifulSoup(r.text, "lxml")
    infobox = s.select_one("table.infobox")
    if not infobox:
        return None
    # Look for the row whose header is 'Website'
    for row in infobox.select("tr"):
        th = row.find("th")
        if th and th.get_text(strip=True).lower() == "website":
            a = row.find("a", href=True)
            if a and a["href"].startswith("http"):
                return a["href"]
    return None

def main():
    links = get_company_links()
    rows = []
    for wiki_url, name in links[:60]:  # keep it small for now
        site = get_official_site(wiki_url)
        rows.append({"Company": name, "Website": site, "Wikipedia": wiki_url})
    df = pd.DataFrame(rows)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    out = Path("data/processed/companies_seed.csv")
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} rows to {out}")

if __name__ == "__main__":
    main()
