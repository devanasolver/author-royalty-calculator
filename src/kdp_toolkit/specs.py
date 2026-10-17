"""KDP specification data, verified against live KDP Help pages in October 2026.

Sources (kdp.amazon.com help topics):
- Trim size / bleed / margins : GVBQ3CMEQW3W2VL6
- Paperback cover + spine math: G201953020
- Paperback printing cost     : G201834340
- Paperback royalty           : G201834330
- eBook pricing / royalty     : G200634500
- eBook list price limits     : G200634560

Everything here is paperback + eBook. Hardcover is not covered yet.
"""

IN = 72.0  # points per inch
BLEED_IN = 0.125  # KDP trims 0.125" from top, bottom and outside edge

# ---------------------------------------------------------------- trim sizes
# name -> (width_in, height_in, large)
# "large" = width > 6.12" or height > 9"  -> different printing costs
TRIM_SIZES = {
    "5x8":        (5.0, 8.0, False),
    "5.06x7.81":  (5.06, 7.81, False),
    "5.25x8":     (5.25, 8.0, False),
    "5.5x8.5":    (5.5, 8.5, False),
    "6x9":        (6.0, 9.0, False),
    "6.14x9.21":  (6.14, 9.21, True),
    "6.69x9.61":  (6.69, 9.61, True),
    "7x10":       (7.0, 10.0, True),
    "7.44x9.69":  (7.44, 9.69, True),
    "7.5x9.25":   (7.5, 9.25, True),
    "8x10":       (8.0, 10.0, True),
    "8.25x6":     (8.25, 6.0, True),
    "8.25x8.25":  (8.25, 8.25, True),
    "8.5x8.5":    (8.5, 8.5, True),
    "8.5x11":     (8.5, 11.0, True),
    "8.27x11.69": (8.27, 11.69, True),  # A4
}

# Min/max page counts per trim size, per ink+paper combo.
# Keys: ink_paper -> (min, max).  Standard set applies unless overridden below.
INK_PAPERS = {
    "bw-white":        "Black ink, white paper",
    "bw-cream":        "Black ink, cream paper",
    "bw-groundwood":   "Black ink, groundwood paper",
    "color-standard":  "Standard color ink, white paper",
    "color-premium":   "Premium color ink, white paper",
}
_DEFAULT_LIMITS = {
    "bw-white": (24, 828), "bw-cream": (24, 776), "bw-groundwood": (24, 812),
    "color-standard": (72, 600), "color-premium": (24, 828),
}
_LIMIT_OVERRIDES = {  # trim -> {ink_paper: (min, max)}
    "8.25x6":    {"bw-white": (24, 800), "bw-cream": (24, 750), "bw-groundwood": (24, 784), "color-premium": (24, 800)},
    "8.25x8.25": {"bw-white": (24, 800), "bw-cream": (24, 750), "bw-groundwood": (24, 784), "color-premium": (24, 800)},
    "8.5x8.5":   {"bw-white": (24, 590), "bw-cream": (24, 550), "bw-groundwood": (24, 578), "color-premium": (24, 590)},
    "8.5x11":    {"bw-white": (24, 590), "bw-cream": (24, 550), "bw-groundwood": (24, 578), "color-premium": (24, 590)},
    "8.27x11.69": {"bw-white": (24, 780), "bw-cream": (24, 730), "bw-groundwood": (24, 764), "color-premium": (24, 590)},
}

def page_limits(trim, ink_paper):
    """(min, max) page count for a trim size and ink/paper combo."""
    over = _LIMIT_OVERRIDES.get(trim, {})
    if ink_paper in over:
        return over[ink_paper]
    return _DEFAULT_LIMITS[ink_paper]

# ---------------------------------------------------------------- margins
# Outside (top/bottom/side) minimum margins in inches.
OUTSIDE_MARGIN_MIN = {"no_bleed": 0.25, "bleed": 0.375}
# Inside (gutter) minimum by page count: (max_pages_in_tier, gutter_in)
GUTTER_TIERS = [(150, 0.375), (300, 0.5), (500, 0.625), (700, 0.75), (828, 0.875)]

def gutter_min(page_count):
    for hi, g in GUTTER_TIERS:
        if page_count <= hi:
            return g
    return GUTTER_TIERS[-1][1]

# ---------------------------------------------------------------- spine width
# Inches per page, from the KDP cover help page.
SPINE_PER_PAGE = {
    "bw-white": 0.002252,
    "bw-cream": 0.0025,
    # KDP has not published a groundwood factor; white is the closest match.
    "bw-groundwood": 0.002252,
    "color-standard": 0.002252,
    "color-premium": 0.002347,
}
SPINE_TEXT_MIN_PAGES = 80        # KDP prints spine text only above 79 pages
SPINE_TEXT_CLEARANCE_IN = 0.0625 # space between spine text and spine edge
SPINE_FOLD_VARIANCE_IN = 0.0625  # fold lines can shift this much either side

def spine_width_in(page_count, ink_paper):
    return page_count * SPINE_PER_PAGE[ink_paper]

# Keep the back-cover bottom-right area clear for the barcode KDP adds.
# From the KDP cover templates (the pink "barcode area"): ~2.0 x 1.2 inches.
BARCODE_ZONE = (2.0, 1.2)

# ---------------------------------------------------------------- printing cost
# Fixed cost + (pages * per-page).  fixed_only_below: page counts at or under
# this number pay only the fixed cost (no per-page part).
# currency, fixed_only_below, fixed_small, fixed_large, per_page_small, per_page_large
_PRINT = {
    # (currency, fixed_only_below, fixed_small_only, fixed_large_only,
    #  fixed_perpage, per_page_small, per_page_large)
    # fixed_*_only: page count <= fixed_only_below pays ONLY that fixed cost.
    # fixed_perpage + pages*per_page_* otherwise.
    "bw-white": {  # cream paper identical (KDP publishes one table for both)
        "com":    ("USD", 110, 2.30, 2.84, 1.00, 0.012, 0.017),
        "ca":     ("CAD", 110, 2.99, 3.53, 1.26, 0.016, 0.021),
        "co.uk":  ("GBP", 110, 1.93, 2.15, 0.85, 0.010, 0.012),
        "eu":     ("EUR", 110, 2.05, 2.48, 0.75, 0.012, 0.016),
        "pl":     ("PLN", 110, 9.58, 11.61, 3.51, 0.056, 0.075),
        "se":     ("SEK", 110, 22.84, 27.67, 8.37, 0.134, 0.179),
        "com.au": ("AUD", 108, 4.74, 5.28, 2.42, 0.022, 0.027),
        "co.jp":  ("JPY", 110, 422.0, 530.0, 206.0, 2.0, 3.0),
    },
    "bw-groundwood": {
        "com":    ("USD", 112, 2.23, 2.75, 1.00, 0.0114, 0.0162),
        "ca":     ("CAD", 112, 2.90, 3.42, 1.26, 0.0152, 0.0200),
        "co.uk":  ("GBP", 112, 1.88, 2.08, 0.85, 0.0095, 0.0114),
        "eu":     ("EUR", 112, 1.98, 2.39, 0.75, 0.0114, 0.0152),
        "pl":     ("PLN", 112, 9.26, 11.21, 3.51, 0.0532, 0.0713),
        "se":     ("SEK", 112, 22.12, 26.74, 8.37, 0.1273, 0.1701),
        "com.au": ("AUD", 112, 4.62, 5.14, 2.42, 0.0209, 0.0257),
        "co.jp":  ("JPY", 112, 411.20, 513.80, 206.0, 1.90, 2.85),
    },
    "color-premium": {
        "com":    ("USD", 40, 3.60, 4.20, 1.00, 0.065, 0.08),
        "ca":     ("CAD", 40, 4.66, 5.26, 1.26, 0.085, 0.10),
        "co.uk":  ("GBP", 40, 2.59, 3.24, 0.85, 0.0435, 0.0598),
        "eu":     ("EUR", 40, 2.85, 3.61, 0.75, 0.0525, 0.0715),
        "pl":     ("PLN", 40, 12.86, 15.32, 3.51, 0.267, 0.337),
        "se":     ("SEK", 40, 30.65, 36.51, 8.37, 0.636, 0.804),
        "com.au": ("AUD", 40, 5.82, 6.42, 2.42, 0.085, 0.100),
        "co.jp":  ("JPY", 40, 475.0, 475.0, 206.0, 4.0, 5.0),
    },
    "color-standard": {  # 72-600 pages, always fixed + per-page
        "com":    ("USD", 0, 0, 0, 1.00, 0.0255, 0.0402),
        "ca":     ("CAD", 0, 0, 0, 1.26, 0.037, 0.052),
        "co.uk":  ("GBP", 0, 0, 0, 0.85, 0.020, 0.027),
        "eu":     ("EUR", 0, 0, 0, 0.75, 0.024, 0.035),
        "pl":     ("PLN", 0, 0, 0, 3.51, 0.112, 0.164),
        "se":     ("SEK", 0, 0, 0, 8.37, 0.268, 0.3691),
        "co.jp":  ("JPY", 0, 0, 0, 206.0, 3.50, 4.50),
    },
}
_PRINT["bw-cream"] = _PRINT["bw-white"]

def printing_cost(pages, ink_paper, trim, marketplace="com"):
    """KDP paperback printing cost. Returns (amount, currency)."""
    currency, fixed_only_below, fixed_s, fixed_l, fixed_pp, pp_s, pp_l = \
        _PRINT[ink_paper][marketplace]
    large = TRIM_SIZES[trim][2]
    if fixed_only_below and pages <= fixed_only_below:
        return (fixed_l if large else fixed_s), currency
    return fixed_pp + pages * (pp_l if large else pp_s), currency

# ---------------------------------------------------------------- paperback royalty
# KDP tier change: 50% at or below the threshold list price, 60% at or above.
ROYALTY_TIER_THRESHOLD = {  # marketplace -> (threshold price for 60%, currency)
    "com": (9.99, "USD"), "eu": (9.99, "EUR"), "co.uk": (7.99, "GBP"),
    "ca": (13.99, "CAD"), "com.au": (13.99, "AUD"), "co.jp": (1000, "JPY"),
    "pl": (40, "PLN"), "se": (110, "SEK"),
}
EXPANDED_DISTRIBUTION_RATE = 0.40

def paperback_royalty_rate(list_price, marketplace="com"):
    threshold, _ = ROYALTY_TIER_THRESHOLD[marketplace]
    return 0.60 if list_price >= threshold else 0.50

def paperback_royalty(list_price, pages, ink_paper, trim, marketplace="com",
                      expanded=False):
    """Royalty per sale. Returns (royalty, rate, print_cost, currency)."""
    cost, currency = printing_cost(pages, ink_paper, trim, marketplace)
    rate = EXPANDED_DISTRIBUTION_RATE if expanded else paperback_royalty_rate(list_price, marketplace)
    return rate * list_price - cost, rate, cost, currency

def min_paperback_price(pages, ink_paper, trim, marketplace="com", expanded=False):
    """Lowest list price KDP allows: printing cost / royalty rate."""
    cost, currency = printing_cost(pages, ink_paper, trim, marketplace)
    if expanded:
        return cost / EXPANDED_DISTRIBUTION_RATE, currency
    threshold, _ = ROYALTY_TIER_THRESHOLD[marketplace]
    at60 = cost / 0.60
    if at60 >= threshold:
        return at60, currency
    return cost / 0.50, currency

# ---------------------------------------------------------------- ebook royalty
# 70% band (expanded by KDP on 2026-07-07) and delivery cost per marketplace.
EBOOK_70_BAND = {  # marketplace -> (min, max, currency, delivery_per_mb)
    "com":    (2.99, 12.99, "USD", 0.15),
    "ca":     (2.99, 12.99, "CAD", 0.15),
    "co.uk":  (1.77, 12.99, "GBP", 0.10),
    "eu":     (2.69, 12.99, "EUR", 0.12),
    "com.au": (3.99, 15.99, "AUD", 0.15),
    "co.jp":  (250, 1650, "JPY", 1.0),
    "com.br": (5.99, 31.99, "BRL", 0.30),
    "com.mx": (34.99, 199.99, "MXN", 1.0),
    "in":     (99, 599, "INR", 7.0),
}
# 35% option minimums depend on file size (<3MB, 3-10MB, >=10MB); max is high.
EBOOK_35_BANDS = {
    "com":    [(0.99, 200.0), (1.99, 200.0), (2.99, 200.0)],
    "co.uk":  [(0.77, 150.0), (1.25, 150.0), (1.49, 150.0)],
    "eu":     [(0.89, 215.0), (1.29, 215.0), (2.69, 215.0)],
    "com.au": [(0.99, 220.0), (1.99, 220.0), (3.99, 220.0)],
    "ca":     [(0.99, 200.0), (1.99, 200.0), (2.99, 200.0)],
    "co.jp":  [(99, 20000), (99, 20000), (99, 20000)],
    "com.br": [(1.99, 400.0), (3.99, 400.0), (5.99, 400.0)],
    "com.mx": [(11.99, 2500.0), (24.99, 2500.0), (34.99, 2500.0)],
    "in":     [(49, 10999), (69, 10999), (99, 10999)],
}

def ebook_royalty(list_price, size_mb=1.0, marketplace="com"):
    """eBook royalty per sale (US-style, no VAT). Returns dict."""
    lo70, hi70, currency, per_mb = EBOOK_70_BAND[marketplace]
    size_idx = 0 if size_mb < 3 else (1 if size_mb < 10 else 2)
    lo35, hi35 = EBOOK_35_BANDS[marketplace][size_idx]
    in70 = lo70 <= list_price <= hi70
    if in70:
        delivery = max(per_mb * size_mb, 0.01)
        royalty = 0.70 * (list_price - delivery)
        plan = "70%"
    else:
        delivery = 0.0
        royalty = 0.35 * list_price
        plan = "35%"
    ok35 = lo35 <= list_price <= hi35
    return {"royalty": royalty, "plan": plan, "delivery_cost": delivery,
            "currency": currency, "band_70": (lo70, hi70),
            "price_ok": in70 or ok35, "min_35": lo35}
