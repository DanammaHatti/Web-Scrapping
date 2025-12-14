# src/olx_scraper/storage.py
from typing import Iterable
import csv
from .models import Listing
import sqlite3




def save_to_csv(path: str, listings: Iterable[Listing]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "title", "price", "location", "url", "description"])
        for L in listings:
            writer.writerow([L.id, L.title, L.price or "", L.location or "", L.url, L.description or ""])




def save_to_sqlite(db_path: str, listings: Iterable[Listing]):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS listings (
            id TEXT PRIMARY KEY,
            title TEXT,
            price TEXT,
            location TEXT,
            url TEXT,
            description TEXT
        )"""
    )
    for L in listings:
        cur.execute(
            "INSERT OR REPLACE INTO listings (id, title, price, location, url, description) VALUES (?, ?, ?, ?, ?, ?)",
            (L.id, L.title, L.price, L.location, L.url, L.description),
        )
    conn.commit()
    conn.close()