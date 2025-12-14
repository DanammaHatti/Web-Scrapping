# src/olx_scraper/parser.py
from bs4 import BeautifulSoup
from typing import List, Optional
from .models import Listing
import re
import json

PRICE_RE = re.compile(r"(₹\s?[0-9\.,]+)")
KM_YEAR_RE = re.compile(r"([0-9]{4})|([0-9\.,]+\s?km)")

def _extract_text(elem):
    if not elem:
        return ""
    return elem.get_text(" ", strip=True)

def _extract_price_from_text(text: str) -> Optional[str]:
    if not text:
        return None
    m = PRICE_RE.search(text)
    if m:
        return m.group(1).strip()
    return None

def _clean_title_remove_price(title: str) -> str:
    if not title:
        return title
    return PRICE_RE.sub("", title).strip()

def parse_listings(html: str, base_url: str = "") -> List[Listing]:
    """Robust parser for OLX-like result pages with price fallback from title text."""
    soup = BeautifulSoup(html, "lxml")
    listings: List[Listing] = []

    selectors = [
        "[data-testid*=ad-card]",
        "[data-aut-id*=itemBox]",
        "[data-id]",
        "li[class*='ad-list'] a[href]",
        "a[href*='/items/']",
        "a[href*='/p/']",
        "a[href*='/item/']",
    ]

    seen_urls = set()
    for sel in selectors:
        for card in soup.select(sel):
            a = card if card.name == "a" and card.get("href") else card.select_one("a[href]")
            if not a:
                continue
            href = a.get("href")
            if not href:
                continue
            if href.startswith("/"):
                href = base_url.rstrip("/") + href
            if href in seen_urls:
                continue
            seen_urls.add(href)

            # title heuristics
            title_elem = a.select_one("h2") or a.select_one("h3") or a
            raw_title = _extract_text(title_elem)
            # price heuristics (search inside card or anchor)
            price = None
            price_tag = card.select_one(".price, [data-aut-id*=price], ._3iKQx, .m7a2I") or a.select_one(".price, [data-aut-id*=price]")
            if price_tag:
                price = _extract_text(price_tag)

            # fallback: try to extract price from raw title or nearby text
            if not price:
                # check nearby nodes: card, a, or raw_title
                price = _extract_price_from_text(_extract_text(card)) or _extract_price_from_text(_extract_text(a)) or _extract_price_from_text(raw_title)

            # location heuristics
            loc_tag = card.select_one("[data-aut-id*=location], .geo, .-_2wQq8")
            location = _extract_text(loc_tag) if loc_tag else None

            # id heuristics
            item_id = a.get("data-id") or a.get("id") or re.sub(r'[^0-9]', '', href.split("/")[-1])[:50]

            # Clean title by removing price text if we pulled price from it
            title = _clean_title_remove_price(raw_title)

            # if title ends up empty, use raw_title
            if not title:
                title = raw_title

            listings.append(Listing(id=str(item_id), title=title or "", price=price, location=location, url=href))

    # 2) If none found, scan anchors (same fallback)
    if not listings:
        for a in soup.select("a[href]"):
            href = a.get("href")
            if not href:
                continue
            if re.search(r"/(p|item|ads?)/", href) or re.search(r"/[0-9]{5,}", href):
                if href.startswith("/"):
                    href = base_url.rstrip("/") + href
                if href in seen_urls:
                    continue
                seen_urls.add(href)
                raw_title = _extract_text(a.select_one("h2") or a.select_one("h3") or a)
                price = _extract_price_from_text(_extract_text(a)) or _extract_price_from_text(raw_title)
                title = _clean_title_remove_price(raw_title) or raw_title
                listings.append(Listing(id=str(re.sub(r'[^0-9]', '', href.split("/")[-1])[:50]), title=title or "", price=price, location=None, url=href))

    # 3) JSON-LD fallback unchanged
    if not listings:
        for script in soup.select("script[type='application/ld+json']"):
            try:
                data = json.loads(script.string or "{}")
            except Exception:
                continue
            if isinstance(data, dict):
                if data.get("@type") in ("ItemList", "Product", "Offer"):
                    items = data.get("itemListElement") or [data]
                    for it in items:
                        if isinstance(it, dict):
                            name = it.get("name") or (it.get("item") or {}).get("name")
                            url = it.get("url") or (it.get("item") or {}).get("url")
                            price = None
                            if it.get("offers"):
                                offers = it["offers"]
                                price = offers.get("price") if isinstance(offers, dict) else None
                            if url:
                                if url.startswith("/"):
                                    url = base_url.rstrip("/") + url
                                listings.append(Listing(id=str(re.sub(r'[^0-9]', '', url.split("/")[-1])[:50]), title=name or "", price=price, location=None, url=url))
            elif isinstance(data, list):
                for obj in data:
                    if isinstance(obj, dict) and obj.get("url"):
                        url = obj["url"]
                        if url.startswith("/"):
                            url = base_url.rstrip("/") + url
                        listings.append(Listing(id=str(re.sub(r'[^0-9]', '', url.split("/")[-1])[:50]), title=obj.get("name",""), price=None, location=None, url=url))

    # Dedupe
    deduped = []
    seen = set()
    for L in listings:
        if L.url and L.url not in seen:
            deduped.append(L)
            seen.add(L.url)

    # Debug print
    print(f"[parser] found {len(deduped)} candidate listings (showing up to 10):")
    for i, l in enumerate(deduped[:10]):
        print(f"  {i+1}. {l.title!r} | {l.price!r} | {l.url}")

    return deduped

def parse_listing_detail(html: str, url: str) -> Listing:
    """Conservative detail parser; fills missing price/location/description if possible."""
    soup = BeautifulSoup(html, "lxml")
    title_tag = soup.select_one("h1") or soup.select_one("[data-aut-id*=title]") or soup.select_one(".title")
    title = _extract_text(title_tag)
    price_tag = soup.select_one("[data-aut-id*=price]") or soup.select_one(".price")
    price = _extract_text(price_tag) if price_tag else _extract_price_from_text(title)
    location_tag = soup.select_one("[data-aut-id*=location]") or soup.select_one(".location")
    location = _extract_text(location_tag)
    desc_tag = soup.select_one("[data-aut-id*=description]") or soup.select_one(".description")
    description = _extract_text(desc_tag)
    listing_id = url.split("/")[-1]
    # if title contains price, remove it
    title = _clean_title_remove_price(title)
    return Listing(id=listing_id, title=title, price=price, location=location, url=url, description=description)
