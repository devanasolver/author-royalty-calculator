"""Spec math checked against the worked examples on KDP's own help pages."""
import pytest
from kdp_toolkit import specs


def test_spine_formulas():
    # kdp.amazon.com/help/topic/G201953020
    assert specs.spine_width_in(100, "bw-white") == pytest.approx(0.2252)
    assert specs.spine_width_in(100, "bw-cream") == pytest.approx(0.25)
    assert specs.spine_width_in(28, "color-premium") == pytest.approx(0.065716)
    assert specs.spine_width_in(100, "color-standard") == pytest.approx(0.2252)


def test_gutter_tiers():
    assert specs.gutter_min(24) == 0.375
    assert specs.gutter_min(150) == 0.375
    assert specs.gutter_min(151) == 0.5
    assert specs.gutter_min(300) == 0.5
    assert specs.gutter_min(301) == 0.625
    assert specs.gutter_min(828) == 0.875


def test_printing_cost_kdp_examples():
    # KDP example: 300-page black ink regular trim, US = 1.00 + 300*0.012
    assert specs.printing_cost(300, "bw-white", "6x9", "com")[0] == \
        pytest.approx(4.60)
    # KDP example: 55-page black ink regular trim, UK = fixed only 1.93
    assert specs.printing_cost(55, "bw-white", "6x9", "co.uk")[0] == \
        pytest.approx(1.93)
    # KDP example: 150-page standard color regular trim, DE = 0.75 + 150*0.024
    assert specs.printing_cost(150, "color-standard", "6x9", "eu")[0] == \
        pytest.approx(4.35)
    # KDP example: 50-page premium color LARGE trim, AU = 2.42 + 50*0.10
    assert specs.printing_cost(50, "color-premium", "8.5x11", "com.au")[0] == \
        pytest.approx(7.42)


def test_paperback_royalty_kdp_example():
    # KDP example: (0.60 x $15) - $5.00 = $4.00 for a 333-page US paperback
    royalty, rate, cost, _ = specs.paperback_royalty(15, 333, "bw-white",
                                                     "6x9", "com")
    assert rate == 0.60
    assert round(cost, 2) == 5.00
    assert round(royalty, 2) == 4.00


def test_paperback_50_percent_tier():
    # since 2025 paperbacks below the threshold get 50%, not 60%
    _, rate, _, _ = specs.paperback_royalty(9.98, 200, "bw-white", "6x9", "com")
    assert rate == 0.50
    _, rate, _, _ = specs.paperback_royalty(9.99, 200, "bw-white", "6x9", "com")
    assert rate == 0.60
    _, rate, _, _ = specs.paperback_royalty(7.98, 200, "bw-white", "6x9",
                                            "co.uk")
    assert rate == 0.50


def test_min_price_covers_printing():
    price, currency = specs.min_paperback_price(300, "bw-white", "6x9", "com")
    royalty, _, _, _ = specs.paperback_royalty(price, 300, "bw-white",
                                               "6x9", "com")
    assert royalty >= -0.005  # min price means roughly zero royalty


def test_ebook_70_band_expanded_2026():
    # KDP widened the 70% band to $12.99 in July 2026
    assert specs.ebook_royalty(12.99, 1.0, "com")["plan"] == "70%"
    assert specs.ebook_royalty(13.99, 1.0, "com")["plan"] == "35%"
    assert specs.ebook_royalty(2.98, 1.0, "com")["plan"] == "35%"
    r = specs.ebook_royalty(9.99, 2.0, "com")
    assert r["royalty"] == pytest.approx(0.70 * (9.99 - 0.30))


def test_page_limits():
    assert specs.page_limits("6x9", "bw-cream") == (24, 776)
    assert specs.page_limits("8.5x11", "bw-white") == (24, 590)
    assert specs.page_limits("6x9", "color-standard") == (72, 600)
