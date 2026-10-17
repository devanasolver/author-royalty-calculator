"""kdp - the all-in-one KDP toolkit command line."""

import argparse
import json
import sys

from . import __version__
from . import specs


def _print_report(rep):
    tag = "OK  " if rep["ok"] else "FAIL"
    print(f"{tag} {rep['file']}")
    for n in rep["notes"]:
        print(f"  ok    {n}")
    for w in rep["warnings"]:
        print(f"  warn  {w}")
    for e in rep["errors"]:
        print(f"  ERROR {e}")


def cmd_new(a):
    from .scaffold import new_project
    files = new_project(a.folder, a.title, a.author)
    print(f"created {a.folder}/ with: {', '.join(files)}")
    print(f"next: edit manuscript.md and metadata.json, then:")
    print(f"  kdp interior {a.folder}/manuscript.md --title \"{a.title}\" "
          f"--author \"{a.author}\" -o {a.folder}/interior.pdf")


def cmd_interior(a):
    from .interior import build_interior
    info = build_interior(
        a.manuscript, a.output, title=a.title, author=a.author,
        trim=a.trim, ink_paper=a.ink_paper, bleed=a.bleed,
        body_size=a.font_size)
    print(f"wrote {a.output}")
    print(f"  pages: {info['pages']}  (KDP allows {info['page_limit'][0]}-"
          f"{info['page_limit'][1]} for {info['trim']} {info['ink_paper']})")
    print(f"  page size: {info['page_size_in'][0]}x{info['page_size_in'][1]} in"
          f"  gutter: {info['gutter_in']} in")
    print(f"  spine width for the cover: {info['spine_width_in']} in")
    if not info["within_limits"]:
        print("  WARNING: page count is outside KDP limits for this "
              "trim and ink/paper")
    print("  next: kdp validate", a.output)


def cmd_cover(a):
    from .cover import build_cover
    back_text = a.back_text or ""
    if a.back_text_file:
        back_text = open(a.back_text_file, encoding="utf-8").read().strip()
    info = build_cover(
        a.output, a.title, author=a.author, trim=a.trim,
        page_count=a.pages, ink_paper=a.ink_paper,
        front_image=a.front_image, back_image=a.back_image,
        background=a.background, text_color=a.text_color,
        back_text=back_text, spine_text=a.spine_text, guides=a.guides)
    print(f"wrote {a.output}")
    print(f"  cover size: {info['width_in']}x{info['height_in']} in "
          f"(spine {info['spine_in']} in for {info['pages']} pages)")
    if info["spine_note"]:
        print("  note:", info["spine_note"])
    if info["guides"]:
        print("  guides version - for checking only, do NOT upload")
    print("  next: kdp validate", a.output, "--cover --pages", a.pages)


def cmd_validate(a):
    from .validate import validate_cover, validate_interior
    if a.cover:
        if not a.pages:
            print("error: --cover needs --pages N (the interior page count)",
                  file=sys.stderr)
            return 2
        rep = validate_cover(a.pdf, a.trim, a.pages, a.ink_paper)
    else:
        rep = validate_interior(a.pdf, a.trim, a.ink_paper, bleed=a.bleed)
    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        _print_report(rep)
    return 0 if rep["ok"] else 1


def cmd_royalty(a):
    from .royalty import compare_ebook, compare_paperback
    if a.print and a.marketplace not in ("com", "ca", "co.uk", "eu", "pl",
                                         "se", "com.au", "co.jp"):
        print(f"error: no print cost table for {a.marketplace} - paperback "
              "math supports com, ca, co.uk, eu, pl, se, com.au, co.jp",
              file=sys.stderr)
        return 2
    if a.print:
        rows, extra = compare_paperback(a.price, a.pages, a.ink_paper,
                                        a.trim, a.marketplace)
        print(f"Selling a {a.pages}-page {a.trim} paperback at "
              f"{a.price:.2f} {extra['currency']}, you keep per sale:\n")
        for r in rows:
            print(f"  {r['store']:<38} {r['royalty']:>7.2f} {r['currency']}  "
                  f"({r['note']})")
        print(f"\n  printing cost: {extra['print_cost']:.2f} "
              f"{extra['currency']}  |  lowest price KDP allows: "
              f"{extra['min_price']:.2f} {extra['currency']}")
    else:
        rows = compare_ebook(a.price, a.size_mb, a.marketplace)
        cur = rows[0]["currency"]
        print(f"Selling an ebook at {a.price:.2f} {cur}, you keep per sale:\n")
        for r in rows:
            pct = f"{r['royalty'] / a.price * 100:.0f}%" if a.price else "-"
            print(f"  {r['store']:<38} {r['royalty']:>7.2f} {r['currency']}  "
                  f"{pct:>4}  ({r['note']})")


def cmd_keywords(a):
    from .keywords import research_keywords
    from .metadata import fit_keywords
    candidates, live_ok = research_keywords(a.seeds, live=not a.offline)
    if live_ok:
        print(f"{len(candidates)} keyword ideas (Amazon autocomplete + "
              "local expansion):\n")
    else:
        print("no internet or Amazon did not answer - using local "
              "expansion only\n")
    for kw in candidates[:a.limit]:
        print(" ", kw)
    slots = fit_keywords(candidates)
    print("\npacked into the 7 KDP slots (50 characters each):")
    for i, s in enumerate(slots, 1):
        print(f"  {i}. [{len(s):>2}] {s}")
    if a.write:
        meta = json.load(open(a.write, encoding="utf-8"))
        meta["keywords"] = slots
        json.dump(meta, open(a.write, "w", encoding="utf-8"), indent=2)
        print(f"\nwritten into {a.write}")


def cmd_metadata(a):
    from .metadata import check_metadata_file
    errors, warns, notes = check_metadata_file(a.file)
    for n in notes:
        print("  ok   ", n)
    for w in warns:
        print("  warn ", w)
    for e in errors:
        print("  ERROR", e)
    print("PASS" if not errors else "FAIL - fix the errors before upload")
    return 0 if not errors else 1


def cmd_ads(a):
    from .ads import make_ads_plan
    from .royalty import compare_paperback
    royalty = a.royalty
    if royalty is None:
        if a.pages:
            rows, extra = compare_paperback(a.price, a.pages)
            royalty = rows[0]["royalty"]
        else:
            royalty = a.price * 0.7
    keywords = []
    if a.keywords_file:
        keywords = [l.strip() for l in open(a.keywords_file, encoding="utf-8")
                    if l.strip()]
    plan, csvp = make_ads_plan(a.title, a.price, royalty, keywords,
                               a.output_prefix, budget=a.budget, bid=a.bid)
    print(f"wrote {plan} and {csvp}")


def cmd_report(a):
    from .report import parse_report
    res = parse_report(a.file)
    print(f"rows: {res['rows']}   total: {res['total']:.2f}")
    print("\nby marketplace:")
    for mk, amt in sorted(res["by_market"].items(), key=lambda x: -x[1]):
        print(f"  {mk:<12} {amt:>10.2f}")
    print("\ntop titles:")
    for t, amt in sorted(res["by_title"].items(), key=lambda x: -x[1])[:a.top]:
        print(f"  {t[:50]:<52} {amt:>10.2f}")
    print("\nnote:", res["currency_note"])


def cmd_specs(a):
    from .specs import (GUTTER_TIERS, INK_PAPERS, OUTSIDE_MARGIN_MIN,
                        TRIM_SIZES, page_limits, spine_width_in)
    print("KDP paperback trim sizes (page limits are for black ink, "
          "white paper):")
    for name, (w, h, large) in TRIM_SIZES.items():
        lo, hi = page_limits(name, "bw-white")
        print(f"  {name:<12} {w}x{h} in  {'large ' if large else 'regular'}"
              f"  {lo}-{hi} pages")
    print("\nmargins: outside at least"
          f" {OUTSIDE_MARGIN_MIN['no_bleed']} in (no bleed) or"
          f" {OUTSIDE_MARGIN_MIN['bleed']} in (bleed); gutter by page count:")
    for hi, g in GUTTER_TIERS:
        print(f"  up to {hi:>3} pages: {g} in")
    print(f"\nspine width per page (inches):")
    for k, v in specs.SPINE_PER_PAGE.items():
        print(f"  {k:<16} {v}")
    print("\nall numbers verified against KDP help pages, October 2026.")


def build_parser():
    p = argparse.ArgumentParser(
        prog="kdp",
        description="All-in-one Amazon KDP toolkit: interior PDF, cover PDF, "
                    "preflight checks, keywords, metadata, royalties, ads.")
    p.add_argument("--version", action="version",
                   version=f"kdp-toolkit {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common_paper(sp):
        sp.add_argument("--trim", default="6x9",
                        choices=list(specs.TRIM_SIZES))
        sp.add_argument("--ink-paper", default="bw-white",
                        choices=list(specs.INK_PAPERS))

    sp = sub.add_parser("new", help="start a book project folder")
    sp.add_argument("folder")
    sp.add_argument("--title", default="My Book")
    sp.add_argument("--author", default="")
    sp.set_defaults(fn=cmd_new)

    sp = sub.add_parser("interior", help="manuscript -> print-ready PDF")
    sp.add_argument("manuscript")
    sp.add_argument("-o", "--output", default="interior.pdf")
    sp.add_argument("--title", default="Untitled")
    sp.add_argument("--author", default="")
    sp.add_argument("--bleed", action="store_true")
    sp.add_argument("--font-size", type=float, default=11)
    common_paper(sp)
    sp.set_defaults(fn=cmd_interior)

    sp = sub.add_parser("cover", help="build the cover wrap PDF")
    sp.add_argument("-o", "--output", default="cover.pdf")
    sp.add_argument("--title", required=True)
    sp.add_argument("--author", default="")
    sp.add_argument("--pages", type=int, required=True,
                    help="interior page count (decides the spine width)")
    sp.add_argument("--front-image")
    sp.add_argument("--back-image")
    sp.add_argument("--background", default="#1d3557")
    sp.add_argument("--text-color", default="#ffffff")
    sp.add_argument("--back-text", default="")
    sp.add_argument("--back-text-file")
    sp.add_argument("--spine-text")
    sp.add_argument("--guides", action="store_true",
                    help="draw trim/spine/barcode guide lines (checking only)")
    common_paper(sp)
    sp.set_defaults(fn=cmd_cover)

    sp = sub.add_parser("validate", help="preflight a PDF against KDP rules")
    sp.add_argument("pdf")
    sp.add_argument("--cover", action="store_true")
    sp.add_argument("--pages", type=int)
    sp.add_argument("--bleed", action="store_true")
    sp.add_argument("--json", action="store_true")
    common_paper(sp)
    sp.set_defaults(fn=cmd_validate)

    sp = sub.add_parser("royalty", help="what you keep per sale")
    sp.add_argument("price", type=float)
    sp.add_argument("--print", action="store_true",
                    help="paperback math instead of ebook")
    sp.add_argument("--pages", type=int, default=200)
    sp.add_argument("--size-mb", type=float, default=1.0)
    sp.add_argument("--marketplace", default="com",
                    choices=list(specs.EBOOK_70_BAND))
    common_paper(sp)
    sp.set_defaults(fn=cmd_royalty)

    sp = sub.add_parser("keywords", help="keyword ideas for the 7 KDP slots")
    sp.add_argument("seeds", nargs="+")
    sp.add_argument("--offline", action="store_true")
    sp.add_argument("--limit", type=int, default=20)
    sp.add_argument("--write", help="write the 7 slots into metadata.json")
    sp.set_defaults(fn=cmd_keywords)

    sp = sub.add_parser("metadata", help="check a metadata.json against "
                                         "KDP rules")
    sp.add_argument("file")
    sp.set_defaults(fn=cmd_metadata)

    sp = sub.add_parser("ads", help="Amazon Ads quick-start plan + keyword CSV")
    sp.add_argument("--title", required=True)
    sp.add_argument("--price", type=float, required=True)
    sp.add_argument("--pages", type=int)
    sp.add_argument("--royalty", type=float)
    sp.add_argument("--keywords-file")
    sp.add_argument("--budget", type=float, default=5.0)
    sp.add_argument("--bid", type=float, default=0.35)
    sp.add_argument("--output-prefix", default="book")
    sp.set_defaults(fn=cmd_ads)

    sp = sub.add_parser("report", help="summarize a KDP royalty report "
                                       "(xlsx or csv)")
    sp.add_argument("file")
    sp.add_argument("--top", type=int, default=10)
    sp.set_defaults(fn=cmd_report)

    sp = sub.add_parser("specs", help="print the verified KDP spec tables")
    sp.set_defaults(fn=cmd_specs)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    rc = args.fn(args)
    return rc or 0


if __name__ == "__main__":
    sys.exit(main())
