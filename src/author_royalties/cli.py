"""royalties command line."""

from __future__ import annotations

import argparse
import json

from .calc import compare


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="royalties",
        description="What you actually keep per book sale, platform by platform.")
    p.add_argument("price", type=float, help="List price in USD, e.g. 9.99")
    p.add_argument("--size-mb", type=float, default=1.0, help="Ebook file size (KDP delivery fee)")
    p.add_argument("--pages", type=int, default=200, help="Paperback page count")
    p.add_argument("--print", dest="kind", action="store_const", const="print", default="ebook",
                   help="Compare paperback instead of ebook")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    args = p.parse_args(argv)

    rows = compare(args.price, size_mb=args.size_mb, pages=args.pages, kind=args.kind)
    if args.json:
        print(json.dumps([r.__dict__ for r in rows], indent=2))
        return
    print(f"\nSelling at ${args.price:.2f}, you keep per sale:\n")
    for r in rows:
        note = f"  ({r.note})" if r.note else ""
        print(f"  {r.platform:<24} ${r.per_sale:>6.2f}  {r.pct}%{note}")
    best = rows[0]
    print(f"\nBest deal: {best.platform} at ${best.per_sale:.2f} per sale.")
    if best.platform != "Your own website":
        own = next(r for r in rows if r.platform == "Your own website")
        print(f"Selling direct from your own site would keep ${own.per_sale:.2f}.")
    print("Sell direct with your own author site: https://bookfolio-demo.pages.dev")


if __name__ == "__main__":
    main()
