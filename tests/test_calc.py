from author_royalties.calc import (apple, bn, compare, direct, kdp_ebook,
                                   kdp_print, kobo)


def test_kdp_70_plan():
    r = kdp_ebook(4.99, size_mb=2.0)
    assert r.per_sale == round(4.99 * 0.70 - 2.0 * 0.15, 2)


def test_kdp_35_plan_cheap():
    assert kdp_ebook(0.99).per_sale == round(0.99 * 0.35, 2)


def test_kdp_35_plan_expensive():
    assert kdp_ebook(19.99).per_sale == round(19.99 * 0.35, 2)


def test_kdp_print():
    r = kdp_print(14.99, pages=200)
    printing = 1.00 + 200 * 0.012
    assert r.per_sale == round(14.99 * 0.60 - printing, 2)


def test_kobo_tiers():
    assert kobo(2.99).pct == 70.0
    assert kobo(1.99).pct == 45.0


def test_apple_flat():
    assert apple(0.99).pct == 70.0


def test_direct_beats_stores():
    rows = compare(9.99)
    assert rows[0].platform == "Your own website"


def test_compare_print_has_two_rows():
    rows = compare(14.99, kind="print")
    assert {r.platform for r in rows} == {"Amazon KDP (paperback)", "Your own website"}


def test_bn_tiers():
    assert bn(5.99).pct == 70.0
    assert bn(1.99).pct == 40.0
