import json

import pytest

from kdp_toolkit.ads import make_ads_plan
from kdp_toolkit.keywords import offline_expansions, research_keywords
from kdp_toolkit.metadata import check_metadata, fit_keywords
from kdp_toolkit.report import parse_report
from kdp_toolkit.royalty import compare_ebook, compare_paperback
from kdp_toolkit.scaffold import new_project


def test_metadata_rules():
    errors, warns, _ = check_metadata({
        "title": "T", "author": "A", "description": "x" * 500,
        "keywords": ["dogs"] * 7})
    assert not errors
    errors, warns, _ = check_metadata({
        "title": "", "description": "", "keywords": ["best seller book"]})
    assert any("title" in e for e in errors)
    assert any("description" in e for e in errors)
    assert any("best seller" in e for e in errors)
    # over-length keyword
    errors, _, _ = check_metadata({
        "title": "T", "description": "d", "keywords": ["x" * 51]})
    assert any("51" in e for e in errors)


def test_fit_keywords_slots():
    slots = fit_keywords(["alpha beta gamma"] * 20)
    assert 1 <= len(slots) <= 7
    assert all(len(s) <= 50 for s in slots)


def test_offline_expansions_dedupe():
    out = offline_expansions(["cat care", "cat care"])
    assert len(out) == len({o.lower() for o in out})
    assert out[0] == "cat care"
    assert any(o.endswith("guide") for o in out)


def test_royalty_compare_order():
    rows = compare_ebook(9.99)
    assert rows[0]["store"] == "Your own website"  # highest royalty first
    assert rows[-1]["store"].startswith("Amazon KDP")
    rows, extra = compare_paperback(14.99, 300)
    assert extra["min_price"] < 14.99
    assert rows[0]["royalty"] > 0


def test_report_xlsx(tmp_path):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.append(["Title", "Author", "Marketplace", "Royalty Type",
               "Units Sold", "Royalty"])
    ws.append(["Book A", "A", "Amazon.com", "eBook", 5, 25.0])
    ws.append(["Book A", "A", "Amazon.de", "eBook", 1, 2.0])
    p = tmp_path / "r.xlsx"
    wb.save(p)
    res = parse_report(str(p))
    assert res["total"] == pytest.approx(27.0)
    assert res["by_title"]["Book A"] == pytest.approx(27.0)
    assert res["by_market"]["Amazon.de"] == pytest.approx(2.0)


def test_report_csv(tmp_path):
    p = tmp_path / "r.csv"
    p.write_text("Title,Marketplace,Royalty\nBook B,Amazon.com,10.50\n")
    res = parse_report(str(p))
    assert res["total"] == pytest.approx(10.5)


def test_ads_plan(tmp_path):
    plan, csvp = make_ads_plan("T", 9.99, 6.89, ["kw one"],
                               str(tmp_path / "x"))
    assert "Automatic" in open(plan).read()
    assert "exact" in open(csvp).read()


def test_scaffold(tmp_path):
    files = new_project(str(tmp_path / "b"), "T", "A")
    assert "manuscript.md" in files
    meta = json.load(open(tmp_path / "b" / "metadata.json"))
    assert meta["keywords"] == [""] * 7
