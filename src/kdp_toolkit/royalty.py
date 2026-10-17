"""Royalty and printing-cost math for KDP and the other big stores."""

from . import specs

# eBook store terms beyond KDP (standard published terms, October 2026 -
# stores change these; double-check before a big pricing decision).
OTHER_STORES = [
    # name, function of usd price -> royalty, note
    ("Your own website", lambda p: p - (0.029 * p + 0.30),
     "only card processing (~2.9% + 30c) comes out"),
    ("Kobo", lambda p: p * (0.70 if p >= 2.99 else 0.45),
     "70% at $2.99+, else 45%"),
    ("Apple Books", lambda p: p * 0.70, "70% flat, no delivery fee"),
    ("Barnes & Noble Press", lambda p: p * 0.70, "70% flat for ebooks"),
]


def compare_ebook(price, size_mb=1.0, marketplace="com"):
    rows = []
    kdp = specs.ebook_royalty(price, size_mb, marketplace)
    rows.append({
        "store": f"Amazon KDP ebook ({kdp['plan']} plan)",
        "royalty": kdp["royalty"],
        "note": ("70% plan minus a small delivery fee"
                 if kdp["plan"] == "70%" else
                 f"outside the {kdp['band_70'][0]}-{kdp['band_70'][1]} "
                 f"{kdp['currency']} 70% band, so 35%"),
        "currency": kdp["currency"],
    })
    for name, fn, note in OTHER_STORES:
        rows.append({"store": name, "royalty": fn(price), "note": note,
                     "currency": "USD"})
    rows.sort(key=lambda r: -r["royalty"])
    return rows


def compare_paperback(price, pages, ink_paper="bw-white", trim="6x9",
                      marketplace="com"):
    royalty, rate, cost, currency = specs.paperback_royalty(
        price, pages, ink_paper, trim, marketplace)
    min_price, _ = specs.min_paperback_price(pages, ink_paper, trim, marketplace)
    rows = [{
        "store": f"Amazon KDP paperback ({int(rate*100)}% tier)",
        "royalty": royalty,
        "note": f"{int(rate*100)}% of list minus {cost:.2f} {currency} printing",
        "currency": currency,
    }]
    exp_royalty, _, exp_cost, _ = specs.paperback_royalty(
        price, pages, ink_paper, trim, marketplace, expanded=True)
    rows.append({
        "store": "KDP expanded distribution (40%)",
        "royalty": exp_royalty,
        "note": "bookstores and libraries ordering through Ingram",
        "currency": currency,
    })
    return rows, {"print_cost": cost, "currency": currency,
                  "min_price": min_price, "rate": rate}
