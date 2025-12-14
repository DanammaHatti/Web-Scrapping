# quick_test.py
import requests
URL = "https://www.olx.in/items/q-bike"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}
try:
    r = requests.get(URL, headers=HEADERS, timeout=60, allow_redirects=True)
    print("Status:", r.status_code)
    print("Len:", len(r.content))
    print("Headers:", r.headers)
    print("First 500 chars:\n", r.text[:500])
except Exception as e:
    import traceback
    traceback.print_exc()
    print("ERROR:", type(e), e)
