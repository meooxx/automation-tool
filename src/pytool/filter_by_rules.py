"""Split rows into Direct/IC quadrants and Lead Source buckets."""

from collections import Counter
import re

from pytool.constants import (
    APPLICANT_TYPE_HEADER,
    DIRECT_VALUES,
    GEORGIAN_ID_HEADER,
    IC_POSTAL_PREFIXES,
    LEAD_SOURCE_CATEGORIES,
    PROSPECT_ID_HEADER,
    UNSUBSCRIBE_HEADERS,
    ZIP_HEADER,
)
from pytool.read_source_data import find_header_index


def get_cell(row: list, index: int) -> str:
    if index < 0 or index >= len(row) or row[index] is None:
        return ""
    return str(row[index]).strip()


def normalize_value(value: str) -> str:
    text = re.sub(r"[-‐‑‒–—_]+", " ", (value or "").strip().casefold())
    return " ".join(text.split())


def postal_key(zip_code: str) -> str:
    return "".join(zip_code.split()).upper()


def is_ic(zip_code: str) -> bool:
    compact = postal_key(zip_code)
    if not compact or not IC_POSTAL_PREFIXES:
        return False
    if compact in IC_POSTAL_PREFIXES:
        return True
    return compact[:3] in IC_POSTAL_PREFIXES


def is_direct(applicant_type: str) -> bool:
    return normalize_value(applicant_type) in DIRECT_VALUES


def is_unsubscribed(value: str) -> bool:
    return normalize_value(value) in {"yes", "y", "true", "1"}


def is_mailable(
    row: list,
    unsubscribe_indexes: list[int],
    georgian_id_index: int,
) -> bool:
    is_opted_out = any(
        is_unsubscribed(get_cell(row, index))
        for index in unsubscribe_indexes
    )
    has_georgian_id = bool(get_cell(row, georgian_id_index))
    return not is_opted_out and not has_georgian_id


def unique_count(rows: list, id_i: int) -> int:
    if id_i < 0:
        return len(rows)
    seen: set[str] = set()
    for i, row in enumerate(rows):
        pid = get_cell(row, id_i)
        seen.add(pid if pid else f"row-{i}")
    return len(seen)


def mailable_count(rows: list, headers: list, on_error=None) -> int:
    unsubscribe_indexes = []
    for spec in UNSUBSCRIBE_HEADERS:
        index = find_header_index(headers, spec)
        if index != -1:
            unsubscribe_indexes.append(index)

    georgian_id_index = find_header_index(headers, GEORGIAN_ID_HEADER)
    prospect_id_index = find_header_index(headers, PROSPECT_ID_HEADER)
    if not unsubscribe_indexes:
        raise ValueError("no unsubscribe column")
    if georgian_id_index == -1:
        raise ValueError("no Georgian ID column")
    if prospect_id_index == -1:
        raise ValueError("no Prospect Id column")

    mailable_rows = []
    for row_number, row in enumerate(rows, start=1):
        try:
            if is_mailable(
                row,
                unsubscribe_indexes,
                georgian_id_index,
            ):
                mailable_rows.append(row)
        except Exception as e:
            if on_error:
                on_error(
                    "mailable",
                    row_number,
                    row,
                    f"{type(e).__name__}: {e}",
                )
    return unique_count(mailable_rows, prospect_id_index)


def map_lead_source(raw: str) -> str:
    text = normalize_value(raw)
    if not text:
        return "blank"
    for cat in LEAD_SOURCE_CATEGORIES:
        if text in cat.get("aliases", set()):
            return cat["key"]
    return "other"


def _split_lead_sources(
    rows: list,
    leader_i: int,
    on_error=None,
) -> tuple[dict[str, list], dict[str, int]]:
    buckets = {cat["key"]: [] for cat in LEAD_SOURCE_CATEGORIES}
    unmatched: Counter[str] = Counter()
    for i, row in enumerate(rows, start=1):
        try:
            raw = get_cell(row, leader_i)
            key = map_lead_source(raw)
            buckets[key].append(row)
            if key == "other":
                unmatched[raw] += 1
        except Exception as e:
            if on_error:
                on_error("lead_source", i, row, f"{type(e).__name__}: {e}")
    return buckets, dict(unmatched)


def _split_quadrants(rows: list, zip_i: int, type_i: int, on_error=None) -> dict[str, list]:
    buckets = {
        "direct_ic": [],
        "direct_ooc": [],
        "non_direct_ic": [],
        "non_direct_ooc": [],
    }
    for i, row in enumerate(rows, start=1):
        try:
            ic = is_ic(get_cell(row, zip_i))
            direct = is_direct(get_cell(row, type_i))
            if direct and ic:
                buckets["direct_ic"].append(row)
            elif direct:
                buckets["direct_ooc"].append(row)
            elif ic:
                buckets["non_direct_ic"].append(row)
            else:
                buckets["non_direct_ooc"].append(row)
        except Exception as e:
            if on_error:
                on_error("quadrant", i, row, f"{type(e).__name__}: {e}")
    return buckets


def filter_by_rules(source: dict, on_error=None) -> dict:
    headers = source["headers"]
    zip_i = find_header_index(headers, ZIP_HEADER)
    type_i = find_header_index(headers, APPLICANT_TYPE_HEADER)
    leader_i = source.get("leader_index", -1)
    if zip_i == -1:
        raise ValueError("no Zip column")
    if type_i == -1:
        raise ValueError("no OH Applicant Type column")
    if leader_i == -1:
        raise ValueError("no Lead Source column")

    def split(rows: list) -> tuple[dict, dict[str, int]]:
        lead_buckets, unmatched = _split_lead_sources(
            rows, leader_i, on_error)
        return {
            **_split_quadrants(rows, zip_i, type_i, on_error),
            **lead_buckets,
        }, unmatched

    current, current_unmatched = split(source["current"])
    prior, prior_unmatched = split(source["prior"])
    return {
        "current": current,
        "prior": prior,
        "current_mailable": mailable_count(
            source["current"], headers, on_error),
        "prior_mailable": mailable_count(
            source["prior"], headers, on_error),
        "new_this_month": unique_count(
            source["current"],
            find_header_index(headers, PROSPECT_ID_HEADER),
        ),
        "new_prior_month": unique_count(
            source["prior"],
            find_header_index(headers, PROSPECT_ID_HEADER),
        ),
        "unmatched_lead_sources": {
            "current": current_unmatched,
            "prior": prior_unmatched,
        },
    }
