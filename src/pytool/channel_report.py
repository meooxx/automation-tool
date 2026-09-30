"""Build the Channel Performance summary workbook."""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from pytool.constants import CATEGORY_HEADER, LEAD_SOURCE_CATEGORIES

GREEN_FONT = Font(color="006100")
RED_FONT = Font(color="9C0006")
GREEN_FILL = PatternFill("solid", fgColor="C6EFCE")
RED_FILL = PatternFill("solid", fgColor="FFC7CE")

QUAD_KEYS = ("direct_ic", "direct_ooc", "non_direct_ic", "non_direct_ooc")


def month_counts(rows: list, buckets: dict) -> list:
    return [
        [],
        len(rows),
        len(buckets["direct_ic"]),
        len(buckets["direct_ooc"]),
        len(buckets["non_direct_ic"]),
        len(buckets["non_direct_ooc"]),
        *[len(buckets[cat["key"]]) for cat in LEAD_SOURCE_CATEGORIES],
    ]


def _mom(current, prior):
    if current is None or prior is None:
        return ''
    if prior == 0:
        return 1.0
    return (current - prior) / prior


def write_channel_performance(
    path: Path,
    current_month: str,
    # original rows
    current_rows: list,
    # filtered_buckets
    current_buckets: dict,
    prior_month: str | None,
    # original rows
    prior_rows: list,
    # filtered_buckets
    prior_buckets: dict,
) -> Path:
    current_vals = month_counts(current_rows, current_buckets)
    prior_vals = month_counts(prior_rows, prior_buckets)

    wb = Workbook()
    ws = wb.active
    ws.title = "Channel Performance"
    ws.append(["Month"] + [c["name"] for c in CATEGORY_HEADER])
    ws.append([prior_month or ""] + prior_vals)
    ws.append([current_month] + current_vals)

    #   pre  [ 10, 12 ]
    #   curr  [ 11, 15 ]
    # zip(10, 11), zip(12, 15)
    mom_vals = [_mom(c, p) for c, p in zip(current_vals, prior_vals)]
    ws.append(["MoM % Change"] + mom_vals)
    # tint the value based on whether it is positive or negative
    for col, val in enumerate(mom_vals, start=2):
        cell = ws.cell(row=4, column=col)
        if val == '':
            continue
        cell.number_format = "0.0%"
        if val > 0:
            cell.font = GREEN_FONT
            cell.fill = GREEN_FILL
        elif val < 0:
            cell.font = RED_FONT
            cell.fill = RED_FILL

    wb.save(path)
