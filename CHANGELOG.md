# Changelog

## Unreleased

- Repo hygiene: removed the accidentally committed `.venv/` virtualenv plus `*.egg-info` and `__pycache__` build artifacts, and added a `.gitignore` (`.venv`, `__pycache__`, `*.egg-info`, `dist`, `.env`, `client_secrets.json`, `token*.json`). Git history was squashed so the virtualenv is gone from history too.

## 0.1.0 — 2026-10-17

First release.
- `royalties <price>`: per-sale take-home on KDP (ebook 70%/35% plans with delivery fee), Kobo, Apple Books, Barnes & Noble Press, and your own website (card processing only).
- `--print --pages N` for KDP paperback math (60% minus printing).
- `--json` output. 9 offline tests.
