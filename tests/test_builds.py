import subprocess

import pytest
from pypdf import PdfReader

from kdp_toolkit import specs
from kdp_toolkit.cover import build_cover, cover_dimensions
from kdp_toolkit.interior import build_interior
from kdp_toolkit.validate import validate_cover, validate_interior

MANUSCRIPT = """# One

First paragraph with *italics* and **bold** and enough words to make a line or two wrap around the page so layout is real.

Second paragraph.

# Two

Another chapter begins here.
"""


@pytest.fixture
def sample(tmp_path):
    ms = tmp_path / "book.md"
    ms.write_text(MANUSCRIPT * 8)
    pdf = str(tmp_path / "interior.pdf")
    info = build_interior(str(ms), pdf, title="T", author="A")
    return pdf, info


def test_interior_page_size_and_fonts(sample):
    pdf, info = sample
    r = PdfReader(pdf)
    box = r.pages[0].mediabox
    assert float(box.width) / 72 == pytest.approx(6.0)
    assert float(box.height) / 72 == pytest.approx(9.0)
    for p in r.pages:
        for ref in p["/Resources"]["/Font"].values():
            d = ref.get_object().get("/FontDescriptor")
            assert d is not None
            assert any(k in d.get_object() for k in
                       ("/FontFile", "/FontFile2", "/FontFile3"))


def test_interior_passes_own_validator(sample):
    pdf, info = sample
    rep = validate_interior(pdf, "6x9", "bw-white")
    # tiny sample is under the 24-page minimum; that must be the ONLY error
    assert any("outside the KDP limit" in e for e in rep["errors"])
    assert not any("font" in e.lower() for e in rep["errors"])
    assert not any("page size" in e for e in rep["errors"])


def test_bleed_page_size(tmp_path):
    ms = tmp_path / "b.md"
    ms.write_text(MANUSCRIPT)
    pdf = str(tmp_path / "b.pdf")
    info = build_interior(str(ms), pdf, bleed=True)
    assert info["page_size_in"] == (6.125, 9.25)
    rep = validate_interior(pdf, "6x9", bleed=True)
    assert not any("page size" in e for e in rep["errors"])


def test_cover_dimensions_formula():
    w, h, spine = cover_dimensions("8.5x8.5", 28, "color-premium")
    assert w == pytest.approx(0.125 + 8.5 + 0.065716 + 8.5 + 0.125)
    assert h == pytest.approx(8.75)
    assert spine == pytest.approx(28 * 0.002347)


def test_cover_matches_validator(tmp_path):
    pdf = str(tmp_path / "cover.pdf")
    info = build_cover(pdf, "My Book", page_count=120)
    rep = validate_cover(pdf, "6x9", 120, "bw-white")
    assert rep["ok"], rep["errors"]


def test_spine_text_rules(tmp_path):
    info = build_cover(str(tmp_path / "c1.pdf"), "T", page_count=40)
    assert "79" in info["spine_note"]
    info = build_cover(str(tmp_path / "c2.pdf"), "T", page_count=200)
    assert info["spine_note"] is None


def test_validator_catches_bad_pdf(tmp_path):
    # a Letter-size PDF with base-14 fonts must fail for trim 6x9
    from reportlab.pdfgen.canvas import Canvas
    bad = str(tmp_path / "bad.pdf")
    c = Canvas(bad)
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, "not embedded")
    c.save()
    rep = validate_interior(bad, "6x9")
    assert not rep["ok"]
    assert any("page size" in e for e in rep["errors"])
    assert any("not embedded" in e for e in rep["errors"])
