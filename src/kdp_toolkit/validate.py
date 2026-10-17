"""Preflight check for KDP interior and cover PDFs.

Checks the things KDP actually rejects files for:
- page size vs the chosen trim size (with and without bleed)
- page count vs the limits for the trim + ink/paper combo
- every font embedded (KDP requires all fonts embedded)
- cover dimensions vs the exact KDP formula for the page count
- even/odd and minimum spine requirements

What it cannot check (it says so in the report): whether YOUR text or art
sits inside the margins - open the PDF and look, or use KDP's online
previewer after upload.
"""

from pypdf import PdfReader

from . import specs
from .cover import cover_dimensions

TOL_PT = 1.5  # tolerance when comparing page sizes, in points


def _page_sizes_in(reader):
    sizes = set()
    for p in reader.pages:
        box = p.mediabox
        sizes.add((round(float(box.width) / 72, 3), round(float(box.height) / 72, 3)))
    return sizes


def _unembedded_fonts(reader):
    bad = set()
    for p in reader.pages:
        res = p.get("/Resources")
        if not res or "/Font" not in res:
            continue
        for ref in res["/Font"].values():
            f = ref.get_object()
            name = str(f.get("/BaseFont", "?"))
            desc = f.get("/FontDescriptor")
            if desc is None:
                bad.add(name)
                continue
            d = desc.get_object()
            if not any(k in d for k in ("/FontFile", "/FontFile2", "/FontFile3")):
                bad.add(name)
    return bad


def validate_interior(pdf_path, trim, ink_paper="bw-white", bleed=False):
    errors, warns, notes = [], [], []
    reader = PdfReader(pdf_path)
    pages = len(reader.pages)
    tw, th, _ = specs.TRIM_SIZES[trim]

    sizes = _page_sizes_in(reader)
    if len(sizes) > 1:
        errors.append(f"pages are not all the same size: {sorted(sizes)}")
    (w, h), = sizes if len(sizes) == 1 else [(tw, th)]

    if bleed:
        ew, eh = round(tw + specs.BLEED_IN, 3), round(th + 2 * specs.BLEED_IN, 3)
        mode = f"trim {tw}x{th} + bleed"
    else:
        ew, eh = tw, th
        mode = f"trim {tw}x{th}"
    if abs(w - ew) > TOL_PT / 72 or abs(h - eh) > TOL_PT / 72:
        errors.append(
            f"page size is {w}x{h} in but {mode} needs {ew}x{eh} in")
    else:
        notes.append(f"page size {w}x{h} in matches {mode}")

    lo, hi = specs.page_limits(trim, ink_paper)
    if not (lo <= pages <= hi):
        errors.append(
            f"{pages} pages is outside the KDP limit for {trim} "
            f"{ink_paper}: {lo}-{hi} pages")
    else:
        notes.append(f"page count {pages} is inside {lo}-{hi}")

    gutter = specs.gutter_min(pages)
    notes.append(f"for {pages} pages the inside (gutter) margin must be at "
                 f"least {gutter} in; outside margins at least "
                 f"{specs.OUTSIDE_MARGIN_MIN['bleed' if bleed else 'no_bleed']} in")

    bad_fonts = _unembedded_fonts(reader)
    if bad_fonts:
        errors.append(f"fonts not embedded (KDP rejects these): "
                      f"{', '.join(sorted(bad_fonts))}")
    else:
        notes.append("all fonts embedded")

    if pages % 2:
        warns.append("odd page count - the last printed page will be backed "
                     "by a blank; usually fine, but check the previewer")

    if not errors:
        notes.append("spine width for the cover: "
                     f"{specs.spine_width_in(pages, ink_paper):.4f} in "
                     f"({ink_paper})")
    return {"file": pdf_path, "kind": "interior", "pages": pages,
            "errors": errors, "warnings": warns, "notes": notes,
            "ok": not errors}


def validate_cover(pdf_path, trim, page_count, ink_paper="bw-white"):
    errors, warns, notes = [], [], []
    reader = PdfReader(pdf_path)
    if len(reader.pages) != 1:
        errors.append(f"a cover PDF must be exactly 1 page, found "
                      f"{len(reader.pages)}")
    sizes = _page_sizes_in(reader)
    if len(sizes) != 1:
        errors.append(f"pages are not all the same size: {sorted(sizes)}")
    (w, h), = sizes if len(sizes) == 1 else [(0, 0)]

    dw, dh, ds = cover_dimensions(trim, page_count, ink_paper)
    ew, eh, spine = round(dw, 4), round(dh, 4), round(ds, 4)
    if abs(w - ew) > TOL_PT / 72 or abs(h - eh) > TOL_PT / 72:
        errors.append(
            f"cover size is {w}x{h} in but for {page_count} pages of "
            f"{ink_paper} at {trim} it must be {ew}x{eh} in "
            f"(spine {spine} in)")
    else:
        notes.append(f"cover size {w}x{h} in matches the KDP formula "
                     f"(spine {spine} in for {page_count} pages)")

    if page_count >= specs.SPINE_TEXT_MIN_PAGES:
        if spine < 2 * specs.SPINE_TEXT_CLEARANCE_IN + 0.1:
            warns.append("spine is narrow - keep spine text small and "
                         "0.0625 in from the edges")
    else:
        notes.append(f"{page_count} pages: KDP will not print spine text "
                     "(needs 80+) - keep the spine blank or decorative")

    bw, bh = specs.BARCODE_ZONE
    notes.append(f"keep the back cover's bottom-right {bw}x{bh} in clear "
                 "for the barcode KDP adds")

    bad_fonts = _unembedded_fonts(reader)
    if bad_fonts:
        errors.append(f"fonts not embedded: {', '.join(sorted(bad_fonts))}")
    else:
        notes.append("all fonts embedded")

    return {"file": pdf_path, "kind": "cover", "errors": errors,
            "warnings": warns, "notes": notes, "ok": not errors}
