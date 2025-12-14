## How to run

```bash
git clone https://github.com/<username>/olx-scraper.git
cd olx-scraper
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
mkdir data
python -m src.olx_scraper.cli --url "https://www.olx.in/items/q-bike" --out data/listings.csv --limit 5

---

# Want me to help further?

I can:
- Review your **GitHub repo** and fix issues
- Add **Selenium / Playwright** for OLX blocking
- Improve **CSV schema** (price as number, year, km)
- Add **pagination**
- Make it installable via `pip install -e .`

