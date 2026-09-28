"""Read a master Excel and split rows by the Joined column's calendar month."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string

JOINED_HEADER = ["AN", "joined"]


def to_datetime(value) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def year_month(value) -> tuple[int, int] | None:
    dt = to_datetime(value)
    if dt is None:
        return None
    return dt.year, dt.month


def find_joined_index(headers: list[str], joined_header: list[str] = JOINED_HEADER) -> int:
    col_letter, name = joined_header[0], joined_header[1]
    needle = str(name).strip().lower()
    col_i = column_index_from_string(col_letter) - 1
    if col_i < len(headers) and str(headers[col_i]).strip().lower() == needle:
        return col_i
    for i, header in enumerate(headers):
        if str(header).strip().lower() == needle:
            return i
    raise ValueError("no Joined column in header row")


def read_source_data(path, current_date, prior_date, joined_header=JOINED_HEADER) -> dict:
    """Open `path`, keep rows whose Joined month matches each date."""
    path = Path(path)
    current_ym = year_month(current_date)
    prior_ym = year_month(prior_date)
    if current_ym is None or prior_ym is None:
        raise ValueError(
            "current_date and prior_date must be like 2026-01 or 2026-01-02")

    wb = load_workbook(path, data_only=True, read_only=True)
    ws = wb.active
    rows = ws.iter_rows(values_only=True)
    header_row = next(rows, None)
    if header_row is None:
        wb.close()
        raise ValueError(f"empty workbook: {path}")

    headers = ["" if h is None else str(h) for h in header_row]
    joined_i = find_joined_index(headers, joined_header)
    joined_name = headers[joined_i]

    current = []
    prior = []
    for values in rows:
        if values is None or all(v is None or str(v).strip() == "" for v in values):
            continue
        ym = year_month(values[joined_i] if joined_i < len(values) else None)
        if ym is None:
            continue
        row = list(values)
        if ym == current_ym:
            current.append(row)
        elif ym == prior_ym:
            prior.append(row)
    wb.close()

    return {
        "headers": headers,
        "joined_column": joined_name,
        "current": current,
        "prior": prior,
    }
