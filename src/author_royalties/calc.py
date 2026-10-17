"""Royalty math for the big ebook and print platforms.

Rates are each platform's published standard terms as of October 2026
(KDP, Kobo Writing Life, Apple Books for Authors, Barnes & Noble Press).
They change; check the platform before making a big decision.
"""

from __future__ import annotations

from dataclasses import dataclass

# KDP ebook delivery fee is charged per megabyte on the 70% plan.
KDP_DELIVERY_PER_MB = 0.15
# Stripe-style card processing for selling from your own website.
DIRECT_PROCESSING_PCT = 0.029
DIRECT_PROCESSING_FIXED = 0.30
# KDP paperback printing: fixed base + per page (black ink, US, regular trim).
KDP_PRINT_FIXED = 1.00
KDP_PRINT_PER_PAGE = 0.012


@dataclass
class Royalty:
    platform: str
    per_sale: float
    pct: float
    note: str = ""


def kdp_ebook(price: float, size_mb: float = 1.0) -> Royalty:
    if 2.99 <= price <= 9.99:
        earning = price * 0.70 - size_mb * KDP_DELIVERY_PER_MB
        note = "70% plan minus a small delivery fee"
    else:
        earning = price * 0.35
        note = "35% plan (price outside $2.99-$9.99), no delivery fee"
    return Royalty("Amazon KDP (ebook)", round(earning, 2), round(earning / price * 100, 1), note)


def kdp_print(price: float, pages: int = 200) -> Royalty:
    printing = KDP_PRINT_FIXED + pages * KDP_PRINT_PER_PAGE
    earning = price * 0.60 - printing
    return Royalty("Amazon KDP (paperback)", round(earning, 2), round(earning / price * 100, 1),
                   f"60% of list minus about ${printing:.2f} printing for {pages} pages")


def kobo(price: float) -> Royalty:
    rate = 0.70 if price >= 2.99 else 0.45
    return Royalty("Kobo", round(price * rate, 2), round(rate * 100, 1),
                   "70% at $2.99 and up, 45% below")


def apple(price: float) -> Royalty:
    return Royalty("Apple Books", round(price * 0.70, 2), 70.0, "70% at any price, no delivery fee")


def bn(price: float) -> Royalty:
    rate = 0.70 if 2.99 <= price <= 9.99 else (0.40 if price < 2.99 else 0.65)
    return Royalty("Barnes & Noble Press", round(price * rate, 2), round(rate * 100, 1))


def direct(price: float) -> Royalty:
    fee = price * DIRECT_PROCESSING_PCT + DIRECT_PROCESSING_FIXED
    earning = price - fee
    return Royalty("Your own website", round(earning, 2), round(earning / price * 100, 1),
                   "Only card processing (~2.9% + 30c) comes out")


def compare(price: float, size_mb: float = 1.0, pages: int = 200, kind: str = "ebook") -> list:
    if kind == "print":
        rows = [kdp_print(price, pages), direct(price)]
    else:
        rows = [kdp_ebook(price, size_mb), kobo(price), apple(price), bn(price), direct(price)]
    return sorted(rows, key=lambda r: -r.per_sale)
