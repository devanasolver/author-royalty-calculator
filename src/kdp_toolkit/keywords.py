"""Keyword ideas for KDP books from Amazon's free autocomplete.

The autocomplete endpoint is the same one the Amazon search box uses.
It is free and needs no API key. An offline fallback combines your seed
words with common book modifiers when there is no internet.
"""

import json
import urllib.parse
import urllib.request

AUTOCOMPLETE_URL = "https://completion.amazon.com/api/2017/suggestions"

BOOK_MODIFIERS = [
    "book", "books", "for beginners", "guide", "handbook", "workbook",
    "for kids", "for adults", "2026", "gift", "large print", "journal",
]


def amazon_suggestions(seed, limit=10, marketplace="com"):
    """Live suggestions from Amazon autocomplete. Raises on failure."""
    params = urllib.parse.urlencode({
        "prefix": seed, "alias": "stripbooks",
        "site-variant": "desktop", "version": "3",
        "mid": {"com": "ATVPDKIKX0DER", "co.uk": "A1F83G8C2ARO7P",
                "de": "A1PA6795UKMFR9", "ca": "A2EUQ1WTGCTBG2"}.get(
                    marketplace, "ATVPDKIKX0DER"),
    })
    req = urllib.request.Request(
        f"{AUTOCOMPLETE_URL}?{params}",
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                               "AppleWebKit/537.36 Chrome/126 Safari/537.36"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    out = []
    for s in data.get("suggestions", []):
        val = s.get("value", "").strip()
        if val:
            out.append(val)
    return out[:limit]


def offline_expansions(seeds, limit=40):
    """Seed words x common book modifiers, deduplicated, seeds first."""
    seen, out = set(), []
    for s in seeds:
        s = " ".join(str(s).split())
        if s and s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    for s in seeds:
        for mod in BOOK_MODIFIERS:
            cand = f"{s} {mod}".strip()
            if cand.lower() not in seen:
                seen.add(cand.lower())
                out.append(cand)
            if len(out) >= limit:
                return out
    return out


def research_keywords(seeds, live=True, limit_per_seed=8):
    """Combine live autocomplete with offline expansion. Returns
    (candidates, live_ok)."""
    seeds = [s.strip() for s in seeds if s and s.strip()]
    candidates, live_ok = [], False
    if live:
        for seed in seeds:
            try:
                candidates.extend(amazon_suggestions(seed, limit_per_seed))
                live_ok = True
            except Exception:
                pass
    candidates.extend(offline_expansions(seeds))
    seen, deduped = set(), []
    for c in candidates:
        if c.lower() not in seen:
            seen.add(c.lower())
            deduped.append(c)
    return deduped, live_ok
