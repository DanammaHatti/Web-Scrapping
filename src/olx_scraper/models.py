# src/olx_scraper/models.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class Listing:
    id: str
    title: str
    price: Optional[str]
    location: Optional[str]
    url: str
    description: Optional[str] = None