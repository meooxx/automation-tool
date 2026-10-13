"""20-row Master validation file.

- Jan–Aug: 10 random rows
- Sep: 5 rows — Direct IC×2, Direct OOC×1, Non-direct IC×1, Non-direct OOC×1
         Lead Source: 4 non-empty + 1 blank
- Oct: same shape as Sep (5 rows)
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "templates" / "Master report sample.xlsx"
OUT = ROOT / "data" / "master_edge_10.xlsx"

LEADS = [
    "Career Match",
    "Connect W Recr",
    "FOH",
    "AppDay",
    "JOML",
    "GC Website",
    "SOH",
    "Tell Us More",
]
DIRECT = ["Direct", "Direct from High School", "Direct from Secondary School"]
NON_DIRECT = ["Mature Student", "College Transfer", "University Transfer", "Non-Direct"]
IC_ZIPS = ["L4N 1A1", "L3V 2B2", "L9Z 1A1", "L4M 3C3"]
OOC_ZIPS = ["M5V 1J1", "K1A 0B1", "M4W 1A1", "H2X 1Y4"]


def flags() -> dict:
    return {
        "Deceased": "No",
        "Email Bounced": "No",
        "Email Opt In": "Yes",
        "Updates for future students": "Yes",
        "Opted Out": "No",
        "Opted Out of List": "No",
        "Do Not Email": "No",
        "Georgian ID": "",
    }


def month_block(
    year: int,
    month: int,
    leads_4: list[str],
    rng: random.Random,
) -> list[dict]:
    """5 rows: DirectIC×2, DirectOOC, NonDirectIC, NonDirectOOC; 4 leads + blank."""
    day = [3, 8, 12, 18, 24]
    specs = [
        ("Direct IC", True, True, leads_4[0]),
        ("Direct IC", True, True, leads_4[1]),
        ("Direct OOC", True, False, leads_4[2]),
        ("Non-direct IC", False, True, leads_4[3]),
        ("Non-direct OOC", False, False, ""),  # blank lead
    ]
    rows = []
    for i, (tag, is_direct, is_ic, lead) in enumerate(specs):
        apps = DIRECT if is_direct else NON_DIRECT
        zips = IC_ZIPS if is_ic else OOC_ZIPS
        rows.append({
            "Joined": date(year, month, day[i]),
            "Lead Source - Most Recent": lead,
            "Zip": rng.choice(zips),
            "OH Applicant Type": rng.choice(apps),
            "_tag": f"{year}-{month:02d} {tag} lead={lead!r}",
            **flags(),
        })
    return rows


def random_jan_aug(n: int, rng: random.Random) -> list[dict]:
    rows = []
    for _ in range(n):
        month = rng.randint(1, 8)
        day = rng.randint(1, 28)
        is_direct = rng.random() < 0.5
        is_ic = rng.random() < 0.5
        rows.append({
            "Joined": date(2026, month, day),
            "Lead Source - Most Recent": rng.choice(LEADS),
            "Zip": rng.choice(IC_ZIPS if is_ic else OOC_ZIPS),
            "OH Applicant Type": rng.choice(DIRECT if is_direct else NON_DIRECT),
            "_tag": f"2026-{month:02d} random",
            **flags(),
        })
    return rows


def build_rows() -> list[dict]:
    rng = random.Random(42)
    # Sep / Oct each get 4 distinct leads (order shuffled)
    sep_leads = rng.sample(LEADS, 4)
    oct_leads = rng.sample(LEADS, 4)
    rows = []
    rows.extend(random_jan_aug(10, rng))
    rows.extend(month_block(2026, 9, sep_leads, rng))
    rows.extend(month_block(2026, 10, oct_leads, rng))
    # assign ids after shuffle of jan-aug only already fixed order
    for i, row in enumerate(rows, start=1):
        pid = f"R{i:02d}"
        row["Prospect Id"] = pid
        row["First Name"] = pid
        row["Last Name"] = "Edge"
        row["Email"] = f"{pid.lower()}@test.com"
    return rows


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb = load_workbook(TEMPLATE)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    by_name = {str(h): i + 1 for i, h in enumerate(headers) if h is not None}

    if ws.max_row > 1:
        ws.delete_rows(2, ws.max_row - 1)

    rows = build_rows()
    skip = {"_tag"}
    for r, row in enumerate(rows, start=2):
        for name, value in row.items():
            if name in skip:
                continue
            col = by_name.get(name)
            if col is None:
                raise KeyError(name)
            ws.cell(r, col, value)

    wb.save(OUT)

    from collections import Counter
    months = Counter(f"{r['Joined']:%Y-%m}" for r in rows)
    print(f"wrote {len(rows)} rows -> {OUT}")
    print("by month:", dict(sorted(months.items())))
    for row in rows:
        if row["Joined"].month in (9, 10):
            print(f"  {row['Prospect Id']} {row['_tag']}")


if __name__ == "__main__":
    main()
