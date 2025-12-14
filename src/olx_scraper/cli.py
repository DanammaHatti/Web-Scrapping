# src/olx_scraper/cli.py
import argparse
from .fetcher import fetch
from .parser import parse_listings, parse_listing_detail
from .storage import save_to_csv
from urllib.parse import urljoin
import sys

def main():
    parser = argparse.ArgumentParser(description="Simple OLX scraper (educational)")
    parser.add_argument("--url", required=True, help="Search/result page URL to scrape")
    parser.add_argument("--out", default="data/listings.csv", help="CSV output path")
    parser.add_argument("--limit", type=int, default=10, help="Max number of listings to fetch details for")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout seconds for requests or selenium page loads")
    parser.add_argument("--no-selenium", action="store_true", help="Use requests only (may fail on some sites)")

    args = parser.parse_args()

    try:
        html = fetch(args.url, use_selenium=not args.no_selenium, timeout=args.timeout)
    except Exception as exc:
        print("ERROR fetching page:", exc, file=sys.stderr)
        sys.exit(1)

    # Save raw HTML for debugging
    try:
        with open("debug.html", "w", encoding="utf-8") as fh:
            fh.write(html)
        print("Saved raw HTML to debug.html")
    except Exception as e:
        print("Warning: could not save debug.html:", e)

    listings = parse_listings(html, base_url=args.url)

    # normalize relative URLs and optionally fetch details
    for i, L in enumerate(listings[: args.limit]):
        if L.url and not L.url.startswith("http"):
            L.url = urljoin(args.url, L.url)
        try:
            detail_html = fetch(L.url, use_selenium=not args.no_selenium, timeout=args.timeout)
            full = parse_listing_detail(detail_html, L.url)
            listings[i] = full
        except Exception:
            # if detail fetch fails, keep the original summary object
            pass

    save_to_csv(args.out, listings[: args.limit])
    print(f"Saved {min(len(listings), args.limit)} listings to {args.out}")

if __name__ == "__main__":
    main()
