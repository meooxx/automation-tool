"""Read a master Excel and split rows by the Joined column's calendar month.

Import and call `read_source_data`. Joined is found by header name, not column AN.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils.datetime import from_excel

JOINED_HEADER = "joined"


def parse_date(value) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return from_excel(value).date()
        except Exception:
            return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%Y-%m", "%Y/%m"):
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.date()
        except ValueError:
            continue
    return None


def year_month(value) -> tuple[int, int]:
    day = parse_date(value)
    if day is None:
        raise ValueError(f"cannot parse date: {value!r}")
    return day.year, day.month


def find_joined_index(headers: list[str]) -> int:
    for i, name in enumerate(headers):
        if name is None:
            continue
        if str(name).strip().lower() == JOINED_HEADER:
            return i
    raise ValueError("no Joined column in header row")


def _row_to_dict(headers: list[str], values: tuple) -> dict:
    record = {}
    for i, header in enumerate(headers):
        if header is None:
            continue
        key = str(header)
        if key not in record:
            record[key] = values[i] if i < len(values) else None
    return record




def read_source_data(path, current_date, prior_date, joined_header = JOINED_HEADER) -> dict:
    """Open `path`, keep rows whose Joined month matches each date."""
    path = Path(path)
    current_ym = year_month(current_date)
    prior_ym = year_month(prior_date)

    wb = load_workbook(path, data_only=True, read_only=True)
    ws = wb.active
    rows = ws.iter_rows(values_only=True)
    header_row = next(rows, None)
    if header_row is None:
        wb.close()
        raise ValueError(f"empty workbook: {path}")

    headers = ["" if h is None else str(h) for h in header_row]
    joined_i = find_joined_index(headers)
    joined_name = headers[joined_i]

    current = []
    prior = []
    for values in rows:
        if values is None or all(v is None or str(v).strip() == "" for v in values):
            continue
        joined = parse_date(values[joined_i] if joined_i < len(values) else None)
        if joined is None:
            continue
        ym = (joined.year, joined.month)
        record = _row_to_dict(headers, values)
        if ym == current_ym:
            current.append(record)
        elif ym == prior_ym:
            prior.append(record)
    wb.close()

    return {
        "headers": headers,
        "joined_column": joined_name,
        "current": current,
        "prior": prior,
    }
