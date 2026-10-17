# Changelog

## 1.0.0 — 2026-10-17

The royalty calculator grew into the full KDP toolkit. Same free repo, now the whole pipeline.

- `kdp new` - book project scaffold (manuscript + metadata templates)
- `kdp interior` - plain-text manuscript to print-ready interior PDF: trim sizes, gutter margins that grow with page count, bleed option, chapters on right-hand pages, page numbers, embedded Gentium Book Plus font
- `kdp cover` - exact-size cover wrap PDF with KDP spine-width math, back-cover text, spine text (skipped under 80 pages, as KDP requires), optional guide overlay
- `kdp validate` - preflight: page size vs trim (with/without bleed), page count vs KDP limits, all fonts embedded, cover size vs the exact formula
- `kdp keywords` - ideas from Amazon autocomplete (free, no key) plus offline expansion, packed into the 7 x 50-character KDP slots
- `kdp metadata` - checks title, description, and keywords against KDP rules (lengths, banned claims, duplicates)
- `kdp ads` - Amazon Ads quick-start plan + keyword CSV
- `kdp report` - summarizes the KDP royalty report (xlsx/csv) by title and marketplace
- `kdp specs` - prints the verified spec tables
- Royalty math updated to current KDP terms: paperback 50%/60% tiers (the 2025 change), ebook 70% band $2.99-$12.99 (the July 2026 change), full printing-cost tables for all marketplaces and ink/paper types
- All spec numbers verified against live KDP help pages (sources in `src/kdp_toolkit/specs.py`); 23 tests re-check the math against KDP's own worked examples
- The old `royalties` command still works (it now calls `kdp royalty`)

## 0.1.0 — 2026-10-17

First release.
- `royalties <price>`: per-sale take-home on KDP (ebook 70%/35% plans with delivery fee), Kobo, Apple Books, Barnes & Noble Press, and your own website (card processing only).
- `--print --pages N` for KDP paperback math (60% minus printing).
- `--json` output. 9 offline tests.
- Repo hygiene: removed an accidentally committed `.venv/`, added `.gitignore`, squashed history.
