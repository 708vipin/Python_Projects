# IT Companies Leads — USA (Portfolio Mini-Project)

**Goal:** Collect a clean sample list of IT/software companies (California) with verified contact info for outreach.

## Dataset
- Source: Wikipedia category “Software companies based in California” (seed) → official websites → Contact pages
- Final rows: 19 / 60 had at least one of **Email / Phone / Address**
- Files:
  - `outputs/IT_Companies_Leads.xlsx` — portfolio-ready
  - `outputs/IT_Companies_Leads.json` — API-friendly
  - `data/processed/companies_seed.csv` — seed from Wikipedia
  - `data/processed/it_companies_enriched.csv` — enriched

## Fields
- **Company** | **Contact_URL** | **Phone** | **Email** | **Address** | **Website** | **Wikipedia**

## Method
1. Seed company list from Wikipedia category page.
2. For each company, find official website and likely Contact page.
3. Extract first visible **email**, **phone**, and a light **address** line (US ZIP pattern).
4. Export to Excel with basic formatting.

## Tech
`Python` · `requests` · `BeautifulSoup` · `pandas` · `openpyxl`

## Notes / Limitations
- Many companies hide emails (contact forms only) → phones more common.
- Light address heuristic; for production, add structured address parsing.
- Respect robots and rate limits; this repo is a skills demo, not mass scraping.

## Next Improvements
- Try multiple Contact/About/Careers pages per site and merge results
- Pattern-based address extraction (USPS format)
- Email discovery via `/about`, `/press`, `/legal`, `mailto:` links
- De-dup + domain normalization
