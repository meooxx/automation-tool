"""Read a master Excel and split rows by the Joined column's calendar month."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string
from pytool.constants import JOINED_HEADER, LEADER_HEADER

DATE_FORMATS = (
    "%m/%d/%Y",
    "%Y-%m-%d",
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m",
)


def to_datetime(value) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    text = str(value).strip()
    for fmt in DATE_FORMATS:
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


def header_matches(cell, spec: list) -> bool:
    text = "" if cell is None else str(cell).strip()
    if not text:
        return False
    name = spec[1]
    if str(name).strip().lower() == text.lower():
        return True
    pattern = spec[2] if len(spec) > 2 else None
    if pattern is None:
        return False
    return bool(pattern.search(text))


def find_header_index(headers: list, spec: list) -> int:
    col_letter = spec[0]
    col_i = column_index_from_string(col_letter) - 1
    if col_i < len(headers) and header_matches(headers[col_i], spec):
        return col_i
    for i, header in enumerate(headers):
        if header_matches(header, spec):
            return i
    return -1


def read_source_data(
    path,
    current_date,
    prior_date,
    joined_header=JOINED_HEADER,
    leader_header=LEADER_HEADER,
    on_error=None,
) -> dict:
    """Open `path`, keep rows whose Joined month matches each date."""
    path = Path(path)
    current_ym = year_month(current_date)
    prior_ym = year_month(prior_date)
    if current_ym is None:
        raise ValueError(
            "current_date must be a date or datetime, or a string in YYYY-MM-DD format")
    if prior_ym is None:
        raise ValueError(
            "prior_date must be a date or datetime, or a supported date string")
    wb = load_workbook(path, data_only=True, read_only=True)
    ws = wb.active
    rows = ws.iter_rows(values_only=True)
    header_row = next(rows, None)
    if header_row is None:
        wb.close()
        raise ValueError(f"empty workbook: {path}")

    headers = ["" if h is None else str(h) for h in header_row]
    joined_i = find_header_index(headers, joined_header)
    leader_i = find_header_index(headers, leader_header)
    if joined_i == -1:
        wb.close()
        raise ValueError("no Joined column in header row")
    if leader_i == -1:
        wb.close()
        raise ValueError("no Lead Source column in header row")

    current = []
    prior = []
    for excel_row, values in enumerate(rows, start=2):
        try:
            if values is None or all(v is None or str(v).strip() == "" for v in values):
                continue
            row = list(values)
            joined = values[joined_i] if joined_i < len(values) else None
            ym = year_month(joined)
            if ym is None:
                if on_error:
                    on_error("joined", excel_row, row, f"cannot parse Joined: {joined!r}")
                continue
            if ym == current_ym:
                current.append(row)
            elif ym == prior_ym:
                prior.append(row)
        except Exception as e:
            if on_error:
                on_error(
                    "read",
                    excel_row,
                    list(values) if values else None,
                    f"{type(e).__name__}: {e}",
                )
            continue
    wb.close()

    return {
        "headers": headers,
        "joined_index": joined_i,
        "leader_index": leader_i,
        "current": current,
        "prior": prior,
    }
