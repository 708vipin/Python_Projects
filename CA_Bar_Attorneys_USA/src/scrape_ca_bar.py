# src/scrape_ca_bar.py
import re, time, csv
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed

OUT_XLSX = Path("outputs/CA_Bar_1k.xlsx")
OUT_CSV  = Path("outputs/CA_Bar_1k.csv")
DETAIL = "https://apps.calbar.ca.gov/attorney/Licensee/Detail/{barno}"
HEADERS = {"User-Agent": "Mozilla/5.0 (portfolio-scraper)"}

def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()

def parse_name_and_bar(header_text: str):
    m = re.match(r"^(.*?)\s*#\s*(\d+)$", clean(header_text))
    return (clean(m.group(1)), m.group(2)) if m else ("","")

def parse_field_block(soup: BeautifulSoup, label: str):
    txt = soup.get_text("\n", strip=True)
    m = re.search(rf"{label}\s*:\s*(.+)", txt, flags=re.I)
    return clean(m.group(1)) if m else ""

def parse_present_status(soup):
    return parse_field_block(soup, "License Status")

def parse_address(soup):
    return clean(parse_field_block(soup, "Address"))

def parse_phone(soup):
    return clean(parse_field_block(soup, "Phone").split("|")[0])

def parse_email(soup):
    a = soup.select_one('a[href^="mailto:"]')
    if a:
        return clean(a.get_text()) or clean(a["href"].replace("mailto:", ""))
    txt = soup.get_text(" ", strip=True)
    m = re.search(r"Email:\s*([^\s]+@[^\s]+)", txt, flags=re.I)
    return m.group(1) if m else ""

def parse_admission_date(soup):
    for key in ["Admitted to the Bar", "Date Admitted", "Admission Date"]:
        v = parse_field_block(soup, key)
        if v:
            return v
    dates = re.findall(r"\b\d{1,2}/\d{1,2}/\d{4}\b", soup.get_text(" ", strip=True))
    return dates[-1] if dates else ""

def parse_city_zip(address: str):
    z = re.search(r"\b(\d{5})(-\d{4})?\b", address)
    zipc = z.group(0) if z else ""
    parts = [p.strip() for p in address.split(",")]
    city = parts[-2] if len(parts) >= 3 else ""
    return city, zipc

def parse_firm(address: str):
    parts = [p.strip() for p in address.split(",")]
    return parts[0] if len(parts) >= 3 else ""

@retry(stop=stop_after_attempt(2), wait=wait_fixed(0.6))
def fetch_detail(barno: int) -> requests.Response:
    r = requests.get(DETAIL.format(barno=barno), headers=HEADERS, timeout=7)
    if r.status_code != 200:
        raise requests.HTTPError(f"{r.status_code}")
    return r

def scrape_seek(start_no=150000, target_count=1000, max_scan=200000, delay_sec=0.28):
    rows, found, scanned = [], 0, 0
    barno = start_no
    print(f"[start] seeking from {start_no} for {target_count} rows (max_scan={max_scan})", flush=True)

    while found < target_count and scanned < max_scan:
        scanned += 1
        try:
            resp = fetch_detail(barno)
        except Exception:
            barno += 1
            if scanned % 400 == 0:
                print(f"[progress] scanned ~{scanned}, found {found} (last bar {barno})", flush=True)
            time.sleep(0.02)
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        header = soup.select_one("h1, h2, h3")
        if header:
            name, bar_number = parse_name_and_bar(header.get_text())
            if name and bar_number:
                address = parse_address(soup)
                row = {
                    "Attorney Name": name,
                    "Firm Name": parse_firm(address),
                    "Address": address,
                    "City": parse_city_zip(address)[0],
                    "Zip Code": parse_city_zip(address)[1],
                    "Phone Number": parse_phone(soup),
                    "Email": parse_email(soup),
                    "Present Status": parse_present_status(soup),
                    "Admission Date": parse_admission_date(soup),
                    "Bar Number": bar_number,
                }
                rows.append(row)
                found += 1
                if found % 25 == 0:
                    print(f"[found] {found}/{target_count} (bar {barno})", flush=True)

        barno += 1
        time.sleep(delay_sec)

    print(f"[done] scanned ~{scanned}, found {found}", flush=True)
    return rows

def main():
    Path("outputs").mkdir(parents=True, exist_ok=True)
    data = scrape_seek(start_no=150000, target_count=1000, max_scan=250000, delay_sec=0.30)
    df = pd.DataFrame(data, columns=[
        "Attorney Name","Firm Name","Address","City","Zip Code",
        "Phone Number","Email","Present Status","Admission Date","Bar Number"
    ])
    df.to_excel(OUT_XLSX, index=False)
    df.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"[saved] {len(df)} rows -> {OUT_XLSX} / {OUT_CSV}", flush=True)

if __name__ == "__main__":
    main()
