# src/scrape_ca_bar.py
import re, time, csv
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed

BASE_DETAIL = "https://apps.calbar.ca.gov/attorney/Licensee/Detail/{barno}"
OUT_XLSX = Path("outputs/CA_Bar_1k.xlsx")
OUT_CSV  = Path("outputs/CA_Bar_1k.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (portfolio-scraper; CA Bar directory; educational use)"
}

# --- helpers ---
def clean(t: str) -> str:
    return re.sub(r"\s+", " ", t or "").strip()

def parse_name_and_bar(header_text: str):
    # Example: "Di Li #294173"
    m = re.match(r"^(.*?)\s*#\s*(\d+)$", clean(header_text))
    if m:
        return clean(m.group(1)), m.group(2)
    return clean(header_text), ""

def parse_city_zip(address: str):
    # Heuristic: last token like CA 90001-1234 or 5-digit ZIP
    zip_m = re.search(r"\b(\d{5})(-\d{4})?\b", address)
    zip_code = zip_m.group(0) if zip_m else ""
    city = ""
    # remove firm prefix if present (before first comma)
    # Address often: "Firm, 123 Main St, City, CA 90001"
    parts = [p.strip() for p in address.split(",")]
    if len(parts) >= 3:
        # city is usually the part before state
        city = parts[-2]
    return city, zip_code

def parse_firm(address: str):
    parts = [p.strip() for p in address.split(",")]
    if len(parts) >= 3:
        return parts[0]
    return ""

def parse_email(soup: BeautifulSoup):
    a = soup.select_one('a[href^="mailto:"]')
    if a:
        return clean(a.get_text()) or clean(a["href"].replace("mailto:", ""))
    # Some pages print Email: <value>
    t = soup.get_text(" ", strip=True)
    m = re.search(r"Email:\s*([^\s]+@[^\s]+)", t, flags=re.I)
    return m.group(1) if m else ""

def parse_field_block(soup: BeautifulSoup, label: str):
    # Tries to find "Label: Value" anywhere
    text = soup.get_text("\n", strip=True)
    m = re.search(rf"{label}\s*:\s*(.+)", text, flags=re.I)
    if m:
        return clean(m.group(1))
    return ""

def parse_present_status(soup: BeautifulSoup):
    # Usually "License Status: Active"
    return parse_field_block(soup, "License Status")

def parse_address(soup: BeautifulSoup):
    # Usually "Address: <line...>"
    val = parse_field_block(soup, "Address")
    # Sometimes multi-line; keep as single line
    return clean(val)

def parse_phone(soup: BeautifulSoup):
    val = parse_field_block(soup, "Phone")
    # strip trailing " | Fax: ..."
    return clean(val.split("|")[0])

def parse_admission_date(soup: BeautifulSoup):
    # Sometimes shows "Admitted to the Bar: mm/dd/yyyy" OR "Date Admitted"
    for key in ["Admitted to the Bar", "Date Admitted", "Admission Date"]:
        v = parse_field_block(soup, key)
        if v:
            return v
    # fallback: earliest date in status table
    text = soup.get_text("\n", strip=True)
    dates = re.findall(r"\b\d{1,2}/\d{1,2}/\d{4}\b", text)
    return dates[-1] if dates else ""

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def fetch_detail(barno: int) -> requests.Response:
    url = BASE_DETAIL.format(barno=barno)
    r = requests.get(url, headers=HEADERS, timeout=20)
    # Some non-existent IDs return 404; raise to use tenacity logic
    if r.status_code != 200:
        raise requests.HTTPError(f"{r.status_code}")
    return r

def scrape_range(start_no: int, end_no: int, target_count: int = 1000, delay_sec: float = 0.35):
    rows = []
    found = 0
    scanned = 0
    print(f"[start] scanning bar# {start_no}..{end_no} aiming for {target_count} rows", flush=True)

    for barno in range(start_no, end_no + 1):
        if found >= target_count:
            break
        scanned += 1
        if scanned % 500 == 0:
            print(f"[progress] scanned ~{scanned}, found {found}", flush=True)

        try:
            resp = fetch_detail(barno)
        except Exception:
            continue  # skip gaps / 404s

        soup = BeautifulSoup(resp.text, "lxml")
        header = soup.select_one("h1, h2, h3")
        if not header:
            continue
        name, bar_number = parse_name_and_bar(header.get_text())

        present_status = parse_present_status(soup)
        address = parse_address(soup)
        city, zip_code = parse_city_zip(address)
        phone = parse_phone(soup)
        email = parse_email(soup)
        admission_date = parse_admission_date(soup)
        firm = parse_firm(address)

        if not name or not bar_number:
            continue

        rows.append({
            "Attorney Name": name,
            "Firm Name": firm,
            "Address": address,
            "City": city,
            "Zip Code": zip_code,
            "Phone Number": phone,
            "Email": email,
            "Present Status": present_status,
            "Admission Date": admission_date,
            "Bar Number": bar_number,
        })
        found += 1

        if found % 50 == 0:
            print(f"[found] {found}/{target_count}", flush=True)

        time.sleep(delay_sec)

    print(f"[done] scanned ~{scanned}, found {found}", flush=True)
    return rows

def main():
    Path("outputs").mkdir(parents=True, exist_ok=True)
    start_no, end_no = 290000, 370000
    data = scrape_range(start_no, end_no, target_count=1000, delay_sec=0.35)
    df = pd.DataFrame(data, columns=[
        "Attorney Name","Firm Name","Address","City","Zip Code",
        "Phone Number","Email","Present Status","Admission Date","Bar Number"
    ])
    df.to_excel(OUT_XLSX, index=False)
    df.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"[saved] {len(df)} rows -> {OUT_XLSX} / {OUT_CSV}", flush=True)


if __name__ == "__main__":
    main()
