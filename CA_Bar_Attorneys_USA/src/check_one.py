# src/check_one.py
import sys, requests, re
from bs4 import BeautifulSoup

DETAIL = "https://apps.calbar.ca.gov/attorney/Licensee/Detail/{barno}"
ua = {"User-Agent": "Mozilla/5.0 (portfolio-check)"}

barno = int(sys.argv[1]) if len(sys.argv) > 1 else 150000

r = requests.get(DETAIL.format(barno=barno), headers=ua, timeout=8)
print("HTTP:", r.status_code)
if r.status_code == 200:
    soup = BeautifulSoup(r.text, "lxml")
    h = soup.select_one("h1, h2, h3")
    print("Header:", h.get_text(strip=True) if h else "(no header)")
