"""Master edge-case file for Channel Performance.

- Jan–Aug: each month × 8 lead sources × 2 rows
- Sep / Oct (each month):
    Direct/Non-direct × IC/OOC → 1 each (4)
    blank → 1, Other → 1
    each of 8 lead sources → 1
  = 14 rows / month
- After Oct: one row per mailable exclusion (names show which rule fired)
"""

from __future__ import annotations

import random
from datetime import date
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
OTHER_LEAD = "Unknown Campaign XYZ"
DIRECT = ["Direct", "Direct from High School", "Direct from Secondary School"]
NON_DIRECT = ["Mature Student", "College Transfer", "University Transfer", "Non-Direct"]
IC_ZIPS = ["L4N 1A1", "L3V 2B2", "L9Z 1A1", "L4M 3C3"]
OOC_ZIPS = ["M5V 1J1", "K1A 0B1", "M4W 1A1", "H2X 1Y4"]
QUADRANTS = [
    (True, True, "Direct IC"),
    (True, False, "Direct OOC"),
    (False, True, "Non-direct IC"),
    (False, False, "Non-direct OOC"),
]


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


def make_row(
    year: int,
    month: int,
    day: int,
    lead: str,
    is_direct: bool,
    is_ic: bool,
    tag: str,
    rng: random.Random,
    flag_overrides: dict | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
) -> dict:
    apps = DIRECT if is_direct else NON_DIRECT
    zips = IC_ZIPS if is_ic else OOC_ZIPS
    row_flags = flags()
    if flag_overrides:
        row_flags.update(flag_overrides)
    row = {
        "Joined": date(year, month, day),
        "Lead Source - Most Recent": lead,
        "Zip": rng.choice(zips),
        "OH Applicant Type": rng.choice(apps),
        "_tag": tag,
        **row_flags,
    }
    if first_name is not None:
        row["_first_name"] = first_name
    if last_name is not None:
        row["_last_name"] = last_name
    return row


def jan_aug(year: int, rng: random.Random) -> list[dict]:
    """Months 1–8: each of 8 lead sources × 2 rows per month."""
    rows = []
    for month in range(1, 9):
        day = 1
        for lead in LEADS:
            for copy in (1, 2):
                is_direct, is_ic, qtag = QUADRANTS[(month + copy) % 4]
                rows.append(
                    make_row(
                        year,
                        month,
                        min(day, 28),
                        lead,
                        is_direct,
                        is_ic,
                        f"{year}-{month:02d} {lead} #{copy} {qtag}",
                        rng,
                    )
                )
                day += 1
    return rows


def sep_oct_month(year: int, month: int, rng: random.Random) -> list[dict]:
    """14 rows: 4 quadrants + blank + other + 8 lead sources."""
    rows = []
    day = 1
    for is_direct, is_ic, qtag in QUADRANTS:
        # quadrant rows use a cycling lead so they stay mailable/classifiable
        lead = LEADS[(day - 1) % len(LEADS)]
        rows.append(
            make_row(
                year,
                month,
                day,
                lead,
                is_direct,
                is_ic,
                f"{year}-{month:02d} {qtag}",
                rng,
            )
        )
        day += 1
    rows.append(
        make_row(
            year, month, day, "", True, True, f"{year}-{month:02d} blank", rng
        )
    )
    day += 1
    rows.append(
        make_row(
            year,
            month,
            day,
            OTHER_LEAD,
            False,
            False,
            f"{year}-{month:02d} other={OTHER_LEAD!r}",
            rng,
        )
    )
    day += 1
    for i, lead in enumerate(LEADS):
        is_direct, is_ic, qtag = QUADRANTS[i % 4]
        rows.append(
            make_row(
                year,
                month,
                day,
                lead,
                is_direct,
                is_ic,
                f"{year}-{month:02d} lead={lead!r}",
                rng,
            )
        )
        day += 1
    return rows


def mailable_exclusion_rows(year: int, month: int, start_day: int, rng: random.Random) -> list[dict]:
    """Not mailable: one row per configured exclusion/requirement miss."""
    cases = [
        (
            "mailable exclude deceased",
            "Deceased",
            "Yes",
            {"Deceased": "Yes"},
        ),
        (
            "mailable exclude bounced",
            "Email",
            "Bounced",
            {"Email Bounced": "Yes"},
        ),
        (
            "mailable exclude georgian id",
            "Has",
            "GeorgianID",
            {"Georgian ID": "G-99999"},
        ),
        (
            "mailable require opt in fail",
            "No",
            "EmailOptIn",
            {"Email Opt In": "No"},
        ),
        (
            "mailable exclude opted out",
            "Opted",
            "Out Yes",
            {"Opted Out": "Yes"},
        ),
        (
            "mailable require future updates fail",
            "No",
            "FutureUpdates",
            {"Updates for future students": "No"},
        ),
    ]
    rows = []
    day = start_day
    for tag, first, last, overrides in cases:
        rows.append(
            make_row(
                year,
                month,
                day,
                LEADS[0],
                True,
                True,
                tag,
                rng,
                flag_overrides=overrides,
                first_name=first,
                last_name=last,
            )
        )
        day += 1
    return rows


def build_rows() -> list[dict]:
    rng = random.Random(42)
    year = 2026
    rows = []
    rows.extend(jan_aug(year, rng))
    rows.extend(sep_oct_month(year, 9, rng))
    rows.extend(sep_oct_month(year, 10, rng))
    rows.extend(mailable_exclusion_rows(year, 10, start_day=15, rng=rng))
    for i, row in enumerate(rows, start=1):
        pid = f"R{i:03d}"
        row["Prospect Id"] = pid
        row["First Name"] = row.pop("_first_name", pid)
        row["Last Name"] = row.pop("_last_name", "Edge")
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
            name = f"{row['First Name']} {row['Last Name']}"
            print(f"  {row['Prospect Id']} {name} {row['_tag']}")


if __name__ == "__main__":
    main()
