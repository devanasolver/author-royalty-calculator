"""Build a print-ready KDP interior PDF from a simple manuscript file.

Manuscript format (plain text, easy to write):
    # Chapter title          -> starts a new chapter (on a right-hand page)
    ## Smaller heading       -> section heading inside a chapter
    ***                      -> scene break
    <pagebreak>              -> force a new page
    *italic*  **bold**       -> inline styles
    everything else          -> body paragraphs (blank line between them)
"""

import os
import re
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, PageBreak,
                                PageTemplate, Paragraph, Spacer)

from . import specs

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_fonts_registered = False


def register_fonts():
    """Embed the bundled Gentium Book Plus (SIL Open Font License)."""
    global _fonts_registered
    if _fonts_registered:
        return
    pdfmetrics.registerFont(TTFont("Book", os.path.join(FONT_DIR, "GentiumBookPlus-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Book-Bold", os.path.join(FONT_DIR, "GentiumBookPlus-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Book-Italic", os.path.join(FONT_DIR, "GentiumBookPlus-Italic.ttf")))
    pdfmetrics.registerFont(TTFont("Book-BoldItalic", os.path.join(FONT_DIR, "GentiumBookPlus-BoldItalic.ttf")))
    pdfmetrics.registerFontFamily("Book", normal="Book", bold="Book-Bold",
                                  italic="Book-Italic", boldItalic="Book-BoldItalic")
    _fonts_registered = True


def inline_markup(text):
    """Escape text, then restore *italic* and **bold* as real tags."""
    t = escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
    return t


def parse_manuscript(text):
    """Yield (kind, text) blocks: chapter, heading, scene, pagebreak, para."""
    blocks = []
    for chunk in re.split(r"\n\s*\n", text):
        chunk = chunk.strip()
        if not chunk:
            continue
        if chunk.startswith("# "):
            blocks.append(("chapter", chunk[2:].strip()))
        elif chunk.startswith("## "):
            blocks.append(("heading", chunk[3:].strip()))
        elif chunk in ("***", "---", "* * *"):
            blocks.append(("scene", ""))
        elif chunk.lower() in ("<pagebreak>", "\\pagebreak", "[pagebreak]"):
            blocks.append(("pagebreak", ""))
        else:
            blocks.append(("para", " ".join(chunk.split())))
    return blocks


class RectoChapterStart(Flowable):
    """Marker: chapter must begin on an odd (right-hand) page."""
    def wrap(self, w, h):
        return (0, 0)
    def draw(self):
        pass


class BookDoc(BaseDocTemplate):
    def __init__(self, filename, page_w, page_h, m_in, m_out, m_top, m_bot,
                 number_from=3, **kw):
        # initialFontName keeps base-14 Helvetica out of the PDF: reportlab
        # writes the initial font into every page's resources, and a
        # non-embedded base font trips strict preflight tools.
        super().__init__(filename, pagesize=(page_w, page_h),
                         leftMargin=0, rightMargin=0, topMargin=0,
                         bottomMargin=0, initialFontName="Book", **kw)
        self.page_w, self.page_h = page_w, page_h
        self.m_bot = m_bot
        self.number_from = number_from
        frame_r = Frame(m_in, m_bot, page_w - m_in - m_out,
                        page_h - m_top - m_bot, id="odd")
        frame_l = Frame(m_out, m_bot, page_w - m_out - m_in,
                        page_h - m_top - m_bot, id="even")
        # page 1 is a right-hand (odd) page; onPage alternates the next one
        self.addPageTemplates([
            PageTemplate(id="odd", frames=[frame_r], onPage=self._decorate,
                         onPageEnd=self._to_even),
            PageTemplate(id="even", frames=[frame_l], onPage=self._decorate,
                         onPageEnd=self._to_odd),
        ])

    def _to_even(self, canv, doc):
        doc.handle_nextPageTemplate("even")

    def _to_odd(self, canv, doc):
        doc.handle_nextPageTemplate("odd")

    def handle_pageBegin(self):
        self._page_has_content = False
        super().handle_pageBegin()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            self._page_has_content = True

    def handle_flowable(self, flowables):
        if flowables and isinstance(flowables[0], RectoChapterStart):
            if not getattr(self, "_page_has_content", False):
                # current page is still empty: use it when it is right-hand
                flowables[0] = Spacer(0, 0) if self.page % 2 == 1 else PageBreak()
            else:
                flowables[0] = PageBreak()
                if (self.page + 1) % 2 == 0:
                    # next page would be left-hand: add a blank page first
                    flowables.insert(1, Spacer(1, 12))
                    flowables.insert(2, PageBreak())
        super().handle_flowable(flowables)

    def _decorate(self, canv, doc):
        pno = canv.getPageNumber()
        if pno >= self.number_from:
            canv.saveState()
            canv.setFont("Book", 9)
            canv.drawCentredString(self.page_w / 2.0, self.m_bot / 2.0, str(pno))
            canv.restoreState()


def _styles(body_size, leading):
    base = {"bulletFontName": "Book"}
    return {
        "chapter": ParagraphStyle("chapter", **dict(base), fontName="Book-Bold",
                                  fontSize=body_size + 8, leading=(body_size + 8) * 1.3,
                                  alignment=TA_CENTER, spaceBefore=0.9 * inch,
                                  spaceAfter=0.4 * inch),
        "heading": ParagraphStyle("heading", **dict(base), fontName="Book-Bold",
                                  fontSize=body_size + 2, leading=(body_size + 2) * 1.3,
                                  spaceBefore=14, spaceAfter=8),
        "para": ParagraphStyle("para", **dict(base), fontName="Book", fontSize=body_size,
                               leading=leading, alignment=TA_JUSTIFY,
                               firstLineIndent=18),
        "first": ParagraphStyle("first", **dict(base), fontName="Book", fontSize=body_size,
                                leading=leading, alignment=TA_JUSTIFY,
                                firstLineIndent=0),
        "scene": ParagraphStyle("scene", **dict(base), fontName="Book", fontSize=body_size,
                                leading=leading, alignment=TA_CENTER,
                                spaceBefore=10, spaceAfter=10),
        "title": ParagraphStyle("title", **dict(base), fontName="Book-Bold", fontSize=26,
                                leading=34, alignment=TA_CENTER),
        "author": ParagraphStyle("author", **dict(base), fontName="Book", fontSize=14,
                                 leading=20, alignment=TA_CENTER),
        "copyright": ParagraphStyle("copyright", **dict(base), fontName="Book", fontSize=9,
                                    leading=13, alignment=TA_LEFT),
    }


def build_interior(manuscript_path, output_path, title="Untitled", author="",
                   trim="6x9", ink_paper="bw-white", bleed=False,
                   body_size=11, leading=None, copyright_text=None,
                   chapter_starts_recto=True):
    """Build the PDF. Returns a dict of facts about the build."""
    register_fonts()
    tw, th, _ = specs.TRIM_SIZES[trim]
    leading = leading or body_size * 1.4
    page_w, page_h = tw * inch, th * inch
    if bleed:
        page_w += specs.BLEED_IN * inch      # outside edge only
        page_h += specs.BLEED_IN * inch * 2  # top + bottom

    text = open(manuscript_path, encoding="utf-8").read()
    blocks = parse_manuscript(text)
    if not blocks:
        raise ValueError("manuscript is empty - nothing to build")
    st = _styles(body_size, leading)

    def make_story():
        story = [
            Spacer(1, 1.6 * inch),
            Paragraph(inline_markup(title), st["title"]),
        ]
        if author:
            story += [Spacer(1, 0.35 * inch),
                      Paragraph(inline_markup(author), st["author"])]
        story.append(PageBreak())
        cpr = copyright_text or (
            f"Copyright &copy; {author or 'the author'}. All rights reserved."
            "<br/><br/>No part of this book may be reproduced in any form "
            "without written permission from the author.")
        story += [Spacer(1, 4.5 * inch), Paragraph(cpr, st["copyright"])]
        story.append(RectoChapterStart() if chapter_starts_recto else PageBreak())
        first_para = True
        for kind, txt in blocks:
            if kind == "chapter":
                story.append(RectoChapterStart() if chapter_starts_recto
                             else PageBreak())
                story.append(Paragraph(inline_markup(txt), st["chapter"]))
                first_para = True
            elif kind == "heading":
                story.append(Paragraph(inline_markup(txt), st["heading"]))
                first_para = True
            elif kind == "scene":
                story.append(Paragraph("*&nbsp;&nbsp;&nbsp;*&nbsp;&nbsp;&nbsp;*",
                                       st["scene"]))
                first_para = True
            elif kind == "pagebreak":
                story.append(PageBreak())
                first_para = True
            else:
                story.append(Paragraph(inline_markup(txt),
                                       st["first"] if first_para else st["para"]))
                first_para = False
        return story

    # Two passes: page count changes the required gutter, which changes the
    # page count. Iterate until it settles (3 passes is always enough).
    pages = 24
    for _ in range(3):
        gutter = specs.gutter_min(pages)
        outside = specs.OUTSIDE_MARGIN_MIN["bleed" if bleed else "no_bleed"]
        doc = BookDoc(output_path, page_w, page_h,
                      gutter * inch, outside * inch,
                      max(outside, 0.6) * inch, max(outside, 0.7) * inch,
                      number_from=3)
        doc.title, doc.author = title, author
        doc.build(make_story())
        if doc.page == pages:
            break
        pages = doc.page

    lo, hi = specs.page_limits(trim, ink_paper)
    return {
        "pages": pages, "trim": trim, "bleed": bleed,
        "page_size_in": (round(page_w / inch, 3), round(page_h / inch, 3)),
        "gutter_in": specs.gutter_min(pages),
        "spine_width_in": round(specs.spine_width_in(pages, ink_paper), 4),
        "page_limit": (lo, hi), "within_limits": lo <= pages <= hi,
        "ink_paper": ink_paper,
    }
