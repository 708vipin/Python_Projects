# LinkedIn Scraper (Portfolio Project)

## 📌 Overview
This project is a **full-scale LinkedIn scraping framework** designed for portfolio demonstration.  
It simulates how to collect **50,000+ prospects** who posted in the last 30 days and use Sales Navigator.  

⚠️ **Note:** Actual LinkedIn scraping may violate LinkedIn’s Terms of Service.  
For portfolio purposes, this repo contains only framework + sample data.

---

## 📂 Project Structure

LinkedIn_Scraper/
│
├── raw/ # Raw HTML/JSON dumps
├── data/ # Cleaned datasets (CSV, Excel, JSON)
├── logs/ # Logs & errors
├── src/ # Core source code
│ ├── config.py # Settings: creds, proxies, timeouts
│ ├── login.py # LinkedIn login/session handler
│ ├── scraper.py # Main scraping logic
│ ├── parser.py # Extract data into structured dicts
│ ├── exporter.py # Save outputs
│ ├── utils.py # Helper functions
│ └── init.py
├── tests/ # Unit tests for each module
├── requirements.txt # Dependencies
├── README.md # Documentation
└── main.py # Entry point



---

## 🚀 How It Works
1. **Login** → Secure login with Selenium/Playwright.  
2. **Scraping** → Collect profiles who posted recently.  
3. **Parsing** → Extract Name, Title, Company, Post Date, etc.  
4. **Exporting** → Save structured data into CSV/Excel.  
5. **Scaling** → Supports proxies, retries, and batch runs up to 50k+.  

---

## 🛠️ Tech Stack
- **Python 3.10+**  
- **Selenium / Playwright** (headless browser automation)  
- **BeautifulSoup4 / lxml** (HTML parsing)  
- **Pandas** (data cleaning & export)  

---

## 📊 Example Output (sample only)
| Name          | Title                | Company       | Post Date | Profile URL        |
|---------------|----------------------|---------------|-----------|-------------------|
| John Doe      | Marketing Director   | ABC Corp      | 2025-08-25| linkedin.com/in/.. |
| Jane Smith    | Sales Manager        | XYZ Ltd       | 2025-08-28| linkedin.com/in/.. |

---

## ✅ Next Steps
- Implement login flow (`login.py`).  
- Test scraping of 10 profiles (`scraper.py`).  
- Scale with proxies + retries.  
- Save output to `/data` in CSV/Excel.  

---

## 👨‍💻 Author
Project built by **Vipin Pandey** as part of a **real-world scraping portfolio**.


Tech Stack Description

Notes

selenium → Automates LinkedIn with browser.

playwright → Alternative to Selenium (more stealth, modern).

beautifulsoup4 + lxml → Parse profile HTML.

pandas + openpyxl → Clean/export data to CSV/Excel.

requests → For lightweight calls (non-browser scraping parts).

tqdm → Progress bar for large scraping jobs.

loguru → Clean logging system (all logs saved in /logs).
