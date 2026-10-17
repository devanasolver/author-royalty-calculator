"""Build a KDP paperback cover wrap PDF (back + spine + front, with bleed).

Dimensions follow the KDP cover help page (G201953020):
    cover width  = bleed + back width + spine width + front width + bleed
    cover height = bleed + trim height + bleed
Spine width = page count x paper factor (see specs.SPINE_PER_PAGE).
"""

import os

from reportlab.lib.colors import HexColor, Color
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from . import specs
from .interior import register_fonts


def cover_dimensions(trim, page_count, ink_paper):
    """Expected cover PDF size in inches: (width, height, spine_width)."""
    tw, th, _ = specs.TRIM_SIZES[trim]
    spine = specs.spine_width_in(page_count, ink_paper)
    b = specs.BLEED_IN
    return (b + tw + spine + tw + b, th + 2 * b, spine)


def build_cover(output_path, title, author="", trim="6x9", page_count=100,
                ink_paper="bw-white", front_image=None, back_image=None,
                background="#1d3557", text_color="#ffffff",
                back_text="", spine_text=None, spine_color=None,
                guides=False):
    """Build the wrap PDF. Returns a dict of facts about the build."""
    register_fonts()
    tw, th, _ = specs.TRIM_SIZES[trim]
    b = specs.BLEED_IN
    spine = specs.spine_width_in(page_count, ink_paper)
    total_w = b + tw + spine + tw + b
    total_h = th + 2 * b
    W, H = total_w * inch, total_h * inch
    bg = HexColor(background)
    fg = HexColor(text_color)
    spine_bg = HexColor(spine_color) if spine_color else bg

    c = Canvas(output_path, pagesize=(W, H), initialFontName="Book")
    c.setTitle(f"Cover - {title}")

    # ---- background
    c.setFillColor(bg)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # x positions (in points) of back / spine / front regions, excluding bleed
    back_x0 = b * inch
    spine_x0 = back_x0 + tw * inch
    front_x0 = spine_x0 + spine * inch

    # ---- images (full region + bleed on the outer edges)
    if back_image:
        c.drawImage(ImageReader(back_image), 0, 0,
                    width=(tw + b) * inch, height=H,
                    preserveAspectRatio=False, mask=None)
    if front_image:
        c.drawImage(ImageReader(front_image), front_x0, 0,
                    width=(tw + b) * inch, height=H,
                    preserveAspectRatio=False, mask=None)

    # spine band above any background image edges
    c.setFillColor(spine_bg)
    c.rect(spine_x0, 0, spine * inch, H, stroke=0, fill=1)

    safe_top = H - (b + 0.375) * inch  # stay clear of trim edge

    # ---- front cover text
    cx = front_x0 + (tw * inch) / 2.0
    c.setFillColor(fg)
    title_size = 30
    while title_size > 12 and c.stringWidth(title, "Book-Bold", title_size) > (tw - 1.0) * inch:
        title_size -= 2
    c.setFont("Book-Bold", title_size)
    c.drawCentredString(cx, safe_top - title_size, title)
    if author:
        c.setFont("Book", 14)
        c.drawCentredString(cx, b * inch + 0.6 * inch, author)

    # ---- spine text (KDP only prints it above 79 pages)
    spine_note = None
    st = spine_text if spine_text is not None else title
    if st:
        if page_count >= specs.SPINE_TEXT_MIN_PAGES:
            clear = specs.SPINE_TEXT_CLEARANCE_IN * inch
            avail = spine * inch - 2 * clear
            size = 12
            while size > 6 and c.stringWidth(st, "Book", size) > (th - 1.0) * inch:
                size -= 1
            if size * 1.0 <= avail:
                c.saveState()
                c.translate(spine_x0 + spine * inch / 2.0 + size * 0.35, H / 2.0)
                c.rotate(90)
                c.setFont("Book", size)
                c.setFillColor(fg)
                c.drawCentredString(0, -size * 0.35, st)
                c.restoreState()
            else:
                spine_note = ("spine too narrow for text at the required "
                              "0.0625 in clearance - spine text skipped")
        else:
            spine_note = (f"KDP prints spine text only above 79 pages "
                          f"({page_count} pages) - spine text skipped")

    # ---- back cover text (wrapped), kept clear of the barcode zone
    if back_text:
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import Paragraph
        bw, bh = specs.BARCODE_ZONE
        max_w = (tw - 0.75) * inch
        style = ParagraphStyle("back", fontName="Book", fontSize=11,
                               leading=16, textColor=fg)
        p = Paragraph(back_text.replace("&", "&amp;").replace("<", "&lt;"), style)
        _, ph = p.wrap(max_w, 10000)
        top = safe_top - 12
        bottom_limit = (b + bh + 0.1) * inch
        if top - ph < bottom_limit:
            top = bottom_limit + ph
        p.drawOn(c, back_x0 + 0.375 * inch, top - ph)

    # ---- optional template guides (for checking only - never upload)
    if guides:
        c.saveState()
        c.setStrokeColor(HexColor("#ff00ff"))
        c.setLineWidth(0.5)
        c.setDash(3, 3)
        for x in (b * inch, spine_x0, spine_x0 + spine * inch, W - b * inch):
            c.line(x, 0, x, H)
        for y in (b * inch, H - b * inch):
            c.line(0, y, W, y)
        # barcode zone on the back cover, bottom right
        bw, bh = specs.BARCODE_ZONE
        c.rect(back_x0 + (tw - bw - 0.25) * inch, b * inch + 0.2 * inch,
               bw * inch, bh * inch, stroke=1, fill=0)
        c.setDash()
        c.setFillColor(HexColor("#ff00ff"))
        c.setFont("Book-Bold", 10)
        c.drawString(b * inch + 6, H - b * inch - 14,
                     "GUIDES - trim / spine / barcode - do not upload this file")
        c.restoreState()

    c.showPage()
    c.save()

    return {
        "width_in": round(total_w, 4), "height_in": round(total_h, 4),
        "spine_in": round(spine, 4), "trim": trim, "pages": page_count,
        "ink_paper": ink_paper, "guides": guides, "spine_note": spine_note,
    }
