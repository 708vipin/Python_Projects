# 🏛️ California Bar Attorneys Scraper:

## 📌 Project Overview
This project demonstrates how to **scrape attorney profile data** from the official  
[State Bar of California Directory](https://apps.calbar.ca.gov/attorney/LicenseeSearch/QuickSearch) and export it into structured **Excel/CSV files**.  

It is built as a **portfolio project for Upwork** to showcase skills in:
- ✅ Web scraping (requests, BeautifulSoup, regex)
- ✅ Data parsing & cleaning
- ✅ Automation with retry, rate-limiting, and error handling
- ✅ Exporting to Excel/CSV using pandas

---

## 📂 Output
The scraper collects **1,000 attorney entries** with the following columns:

| Column | Description |
|--------|-------------|
| Attorney Name | Full name of the attorney |
| Firm Name | Law firm / employer (if listed) |
| Address | Full business address |
| City | City extracted from address |
| Zip Code | Postal code |
| Phone Number | Primary phone number |
| Email | Email address (if available) |
| Present Status | License status (e.g., Active, Inactive, Suspended) |
| Admission Date | Date admitted to the CA Bar |
| Bar Number | Official Bar license number |

---

## 🛠️ Tech Stack
- **Python 3.11+**
- [Requests](https://pypi.org/project/requests/) → HTTP requests  
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/) → HTML parsing  
- [Tenacity](https://pypi.org/project/tenacity/) → Retry logic  
- [Pandas](https://pandas.pydata.org/) → Data cleaning + Excel/CSV export  

---

## ▶️ How to Run
```bash
# 1. Clone repo
git clone https://github.com/<your-username>/CA_Bar_Attorneys.git
cd CA_Bar_Attorneys

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run scraper
python -u src/scrape_ca_bar.py
