"""Amazon Ads quick-start plan for a book launch.

This writes a plan and a keyword CSV you upload yourself in the Amazon Ads
console. It does not touch your ads account - there is nothing to connect.
"""

import csv

PLAN = """Amazon Ads quick-start for "{title}"
======================================

Week 1-2: let Amazon find buyers
  - Create ONE Sponsored Products campaign, Automatic targeting
  - Daily budget: ${budget}/day
  - Default bid: ${bid:.2f}
  - Do not touch it for 7 days. Amazon needs data.

Week 3: harvest what worked
  - Download the Search Term report (Reports tab)
  - Any customer search term with a sale -> add it to a new MANUAL
    campaign as an Exact match keyword (start bid ${bid_up:.2f})
  - Any term with 8+ clicks and no sale -> add as a Negative keyword
    in the auto campaign, or drop its bid to $0.02

Week 4+: scale slowly
  - Raise bids ~20% on keywords whose ACoS is under your target
  - Target ACoS: your royalty per sale / price x 100 is break-even;
    for a ${price:.2f} book with ~${royalty:.2f} royalty that is about {acos:.0f}%
  - Pause anything that spends 3x your royalty with no sale

Files: the CSV next to this plan is ready for the manual campaign's
keyword upload (Amazon Ads console > campaign > Keywords > bulk upload).
"""


def make_ads_plan(title, price, royalty, keywords, out_prefix,
                  budget=5.0, bid=0.35):
    acos = (royalty / price * 100) if price else 0
    plan = PLAN.format(title=title, budget=int(budget), bid=bid,
                       bid_up=round(bid + 0.10, 2), price=price,
                       royalty=royalty, acos=acos)
    plan_path = f"{out_prefix}-ads-plan.txt"
    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(plan)
    csv_path = f"{out_prefix}-ads-keywords.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Keyword", "Match Type", "Suggested Bid"])
        for kw in keywords:
            w.writerow([kw, "exact", f"{bid + 0.10:.2f}"])
            w.writerow([kw, "phrase", f"{bid:.2f}"])
    return plan_path, csv_path
