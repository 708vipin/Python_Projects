# src/scrape_ca_bar.py
import re
import time
import csv
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed

# ---------- CONFIG ----------
OUT_XLSX = Path("outputs/CA_Bar_1k.xlsx")
OUT_CSV  = Path("outputs/CA_Bar_1k.csv")
DETAIL   = "https://apps.calbar.ca.gov/attorney/Licensee/Detail/{barno}"
HEADERS  = {"User-Agent": "Mozilla/5.0 (portfolio-scraper; CA Bar directory; educational use)"}

TARGET_COUNT       = 1000     # how many valid rows to collect
INITIAL_START_NO   = 48697    # set this to any real Bar Number you found
MAX_SCAN_ATTEMPTS  = 250_000  # hard stop after this many attempts
REQUEST_TIMEOUT_S  = 7
BASE_DELAY_S       = 0.28     # per-request delay
SPARSE_JUMP_AFTER  = 1500     # if we scanned this many without a single "found"
SPARSE_JUMP_STEP   = 10000    # jump this many bar numbers forward on sparse ranges


# ---------- HELPERS ----------
def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def parse_field_block(soup: BeautifulSoup, label: str) -> str:
    """
    Finds 'Label: Value' anywhere in page text (robust to layout changes).
    """
    txt = soup.get_text("\n", strip=True)
    m = re.search(rf"{label}\s*:\s*(.+)", txt, flags=re.I)
    return clean(m.group(1)) if m else ""


def parse_present_status(soup: BeautifulSoup) -> str:
    return parse_field_block(soup, "License Status")


def parse_address(soup: BeautifulSoup) -> str:
    return clean(parse_field_block(soup, "Address"))


def parse_phone(soup: BeautifulSoup) -> str:
    # strip Fax if present (e.g., "Phone: 123 | Fax: 456")
    v = parse_field_block(soup, "Phone")
    return clean(v.split("|")[0])


def parse_email(soup: BeautifulSoup) -> str:
    a = soup.select_one('a[href^="mailto:"]')
    if a:
        return clean(a.get_text()) or clean(a["href"].replace("mailto:", ""))
    txt = soup.get_text(" ", strip=True)
    m = re.search(r"Email:\s*([^\s]+@[^\s]+)", txt, flags=re.I)
    return m.group(1) if m else ""


def parse_admission_date(soup: BeautifulSoup) -> str:
    for key in ["Admitted to the Bar", "Date Admitted", "Admission Date"]:
        v = parse_field_block(soup, key)
        if v:
            return v
    # fallback: earliest/any date-looking token
    dates = re.findall(r"\b\d{1,2}/\d{1,2}/\d{4}\b", soup.get_text(" ", strip=True))
    return dates[-1] if dates else ""


def parse_city_zip(address: str) -> tuple[str, str]:
    z = re.search(r"\b(\d{5})(-\d{4})?\b", address)
    zipc = z.group(0) if z else ""
    parts = [p.strip() for p in address.split(",")]
    # Address often like: "Firm, 123 Main St, City, CA 90001-1234"
    city = parts[-2] if len(parts) >= 3 else ""
    return city, zipc


def parse_firm(address: str) -> str:
    parts = [p.strip() for p in address.split(",")]
    return parts[0] if len(parts) >= 3 else ""


def parse_name_and_bar_from_soup(soup: BeautifulSoup) -> tuple[str, str]:
    """
    Robustly locate 'Name #BarNumber' even if the page header says 'Attorney Profile'.
    Tries common elements; if not found, scans full text.
    """
    candidates = ["h1", "h2", "h3", ".licensee-name", ".profile-header", ".attorney-name", "title"]
    for sel in candidates:
        el = soup.select_one(sel)
        if el:
            text = clean(el.get_text(" ", strip=True))
            m = re.search(r"(.+?)\s*#\s*(\d{3,})\b", text)
            if m:
                return clean(m.group(1)), m.group(2)

    # Fallback: scan full text for the pattern
    all_text = soup.get_text("\n", strip=True)
    m = re.search(r"\n?([A-Z][A-Za-z.\-\' ]+?)\s*#\s*(\d{3,})\b", all_text)
    if m:
        return clean(m.group(1)), m.group(2)

    return "", ""


@retry(stop=stop_after_attempt(2), wait=wait_fixed(0.6))
def fetch_detail(barno: int) -> requests.Response:
    r = requests.get(DETAIL.format(barno=barno), headers=HEADERS, timeout=REQUEST_TIMEOUT_S)
    if r.status_code != 200:
        raise requests.HTTPError(f"{r.status_code}")
    return r


# ---------- SCRAPER ----------
def scrape_seek(start_no: int, target_count: int, max_scan: int, delay_sec: float):
    rows = []
    found = 0
    scanned = 0
    barno = start_no
    since_last_found = 0

    print(f"[start] seeking from {start_no} for {target_count} rows (max_scan={max_scan})", flush=True)

    while found < target_count and scanned < max_scan:
        scanned += 1
        since_last_found += 1

        try:
            resp = fetch_detail(barno)
        except Exception:
            # non-200 or timeout: skip forward
            barno += 1
            if scanned % 400 == 0:
                print(f"[progress] scanned ~{scanned}, found {found} (last bar {barno})", flush=True)
            time.sleep(0.02)
            continue

        soup = BeautifulSoup(resp.text, "lxml")

        # Robust name + bar number extraction
        name, bar_number = parse_name_and_bar_from_soup(soup)

        if name and bar_number:
            address = parse_address(soup)
            city, zipc = parse_city_zip(address)
            row = {
                "Attorney Name": name,
                "Firm Name": parse_firm(address),
                "Address": address,
                "City": city,
                "Zip Code": zipc,
                "Phone Number": parse_phone(soup),
                "Email": parse_email(soup),
                "Present Status": parse_present_status(soup),
                "Admission Date": parse_admission_date(soup),
                "Bar Number": bar_number,
            }
            rows.append(row)
            found += 1
            since_last_found = 0

            if found <= 3:
                # quick sanity preview of first few rows
                print(f"[sample] {row}", flush=True)

            if found % 25 == 0:
                print(f"[found] {found}/{target_count} (bar {barno})", flush=True)

        # auto-jump over sparse ranges
        if since_last_found >= SPARSE_JUMP_AFTER:
            jump_from = barno
            barno += SPARSE_JUMP_STEP
            since_last_found = 0
            print(f"[jump] sparse range detected; jumping from {jump_from} -> {barno}", flush=True)
        else:
            barno += 1

        time.sleep(delay_sec)

    print(f"[done] scanned ~{scanned}, found {found}", flush=True)
    return rows


def main():
    Path("outputs").mkdir(parents=True, exist_ok=True)

    data = scrape_seek(
        start_no=INITIAL_START_NO,              # <— change this if you want to start elsewhere
        target_count=TARGET_COUNT,
        max_scan=MAX_SCAN_ATTEMPTS,
        delay_sec=BASE_DELAY_S,
    )

    df = pd.DataFrame(data, columns=[
        "Attorney Name","Firm Name","Address","City","Zip Code",
        "Phone Number","Email","Present Status","Admission Date","Bar Number"
    ])

    df.to_excel(OUT_XLSX, index=False)
    df.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"[saved] {len(df)} rows -> {OUT_XLSX} / {OUT_CSV}", flush=True)


if __name__ == "__main__":
    main()
