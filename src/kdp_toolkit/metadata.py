"""KDP metadata checks: title, description, the 7 keyword slots.

Rules come from KDP's metadata guidelines. Keyword slot rules:
7 slots, up to 50 characters each, no quotation marks, no subjective or
time-limited claims ("best seller", "free", "new"), no other authors'
names or book titles.
"""

import json
import re

TITLE_MAX = 200
DESCRIPTION_MAX = 4000
KEYWORD_SLOTS = 7
KEYWORD_MAX = 50

# words and claims KDP tells authors not to use as keywords
BANNED_KEYWORD_TERMS = [
    "free", "best seller", "bestseller", "best-selling", "sale",
    "new release", "kindle unlimited", "amazon", "discounted",
]


def check_metadata(meta):
    """meta: dict with title/subtitle/author/description/keywords/categories.
    Returns (errors, warnings, notes)."""
    errors, warns, notes = [], [], []

    title = (meta.get("title") or "").strip()
    if not title:
        errors.append("title is missing")
    elif len(title) > TITLE_MAX:
        errors.append(f"title is {len(title)} characters; KDP allows {TITLE_MAX}")
    else:
        notes.append(f"title: {len(title)} characters (max {TITLE_MAX})")

    if not (meta.get("author") or "").strip():
        warns.append("author name is empty - KDP requires a contributor")

    desc = (meta.get("description") or "").strip()
    if not desc:
        errors.append("description is missing - it is your sales page")
    else:
        if len(desc) > DESCRIPTION_MAX:
            errors.append(f"description is {len(desc)} characters; "
                          f"KDP allows {DESCRIPTION_MAX}")
        else:
            notes.append(f"description: {len(desc)} characters "
                         f"(max {DESCRIPTION_MAX})")
        if len(desc) < 200:
            warns.append("description is very short - 2-3 short paragraphs "
                         "usually sell better")

    keywords = meta.get("keywords") or []
    if not isinstance(keywords, list):
        errors.append("keywords must be a list of up to 7 phrases")
        keywords = []
    if len(keywords) > KEYWORD_SLOTS:
        errors.append(f"{len(keywords)} keywords; KDP has {KEYWORD_SLOTS} slots")
    if len(keywords) < KEYWORD_SLOTS:
        warns.append(f"only {len(keywords)} of {KEYWORD_SLOTS} keyword "
                     "slots used - fill all 7")
    seen = set()
    for i, kw in enumerate(keywords, 1):
        kw_clean = " ".join(str(kw).split())
        if not kw_clean:
            continue
        if len(kw_clean) > KEYWORD_MAX:
            errors.append(f'keyword {i} is {len(kw_clean)} characters '
                          f'(max {KEYWORD_MAX}): "{kw_clean}"')
        if '"' in kw_clean or "'" in kw_clean:
            warns.append(f'keyword {i}: remove quotation marks - "{kw_clean}"')
        low = kw_clean.lower()
        for term in BANNED_KEYWORD_TERMS:
            if term in low:
                errors.append(f'keyword {i} uses "{term}" - KDP bans '
                              "subjective/promotional claims in keywords")
        if low in seen:
            warns.append(f'keyword {i} is a duplicate: "{kw_clean}"')
        seen.add(low)

    categories = meta.get("categories") or []
    if not categories:
        warns.append("no categories listed - pick yours in the KDP "
                     "category browser during upload")
    return errors, warns, notes


def check_metadata_file(path):
    return check_metadata(json.load(open(path, encoding="utf-8")))


def fit_keywords(candidates):
    """Pack candidate phrases into the 7 slots, joining short ones with
    spaces (Amazon reads the whole slot). Returns 7 slot strings."""
    slots = []
    current = ""
    for cand in candidates:
        cand = " ".join(cand.split())[:KEYWORD_MAX]
        if not cand:
            continue
        trial = (current + " " + cand).strip()
        if len(trial) <= KEYWORD_MAX:
            current = trial
        else:
            if current:
                slots.append(current)
            current = cand[:KEYWORD_MAX]
        if len(slots) == KEYWORD_SLOTS:
            break
    if current and len(slots) < KEYWORD_SLOTS:
        slots.append(current)
    return slots[:KEYWORD_SLOTS]
