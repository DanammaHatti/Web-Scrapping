# src/olx_scraper/fetcher.py
import time
from typing import Optional
import requests

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class FetchError(Exception):
    pass

def fetch_requests(url: str, timeout: int = 30) -> str:
    """Lightweight requests-based fetch (may fail on OLX due to bot protections)."""
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        time.sleep(1.0)  # polite pause
        return resp.text
    except Exception as exc:
        raise FetchError(f"requests fetch failed for {url}: {exc}") from exc

def fetch_selenium(url: str, headless: bool = True, page_load_timeout: int = 60) -> str:
    """Fetch page using Selenium Chrome. More reliable for javascript / bot-protected pages."""
    options = Options()
    if headless:
        # use new headless mode if available
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # optional: reduce logging noise
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # set a common UA
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = None
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        driver.set_page_load_timeout(page_load_timeout)
        driver.get(url)
        # wait a little for JS
        time.sleep(4)
        html = driver.page_source
        driver.quit()
        return html
    except Exception as exc:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        raise FetchError(f"selenium fetch failed for {url}: {exc}") from exc

def fetch(url: str, use_selenium: bool = True, timeout: int = 30) -> str:
    """
    Convenience fetcher: tries requests first (fast) and falls back to Selenium if
    requests fails and use_selenium is True. Matches CLI which passes use_selenium.
    """
    if not use_selenium:
        return fetch_requests(url, timeout=timeout)

    # Try requests first (fast), then fallback to Selenium if a fetch error occurs.
    try:
        return fetch_requests(url, timeout=timeout)
    except FetchError:
        return fetch_selenium(url, headless=True, page_load_timeout=max(30, timeout))
