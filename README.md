## How to run

```bash
git clone https://github.com/<username>/olx-scraper.git
cd olx-scraper
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
mkdir data
python -m src.olx_scraper.cli --url "https://www.olx.in/items/q-bike" --out data/listings.csv --limit 5
