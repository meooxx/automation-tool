"""Split rows into Direct/IC quadrants and Lead Source buckets."""

import re

from pytool.constants import (
    APPLICANT_TYPE_HEADER,
    DECEASED_HEADER,
    DIRECT_VALUES,
    EMAIL_BOUNCED_HEADER,
    EMAIL_OPT_IN_HEADER,
    EMAIL_OPT_OUT_HEADER,
    FUTURE_STUDENTS_HEADER,
    GEORGIAN_ID_HEADER,
    IC_POSTAL_PREFIXES,
    PROSPECT_ID_HEADER,
    ZIP_HEADER,
)
from pytool.lead_source import lead_categories
from pytool.read_source_data import find_header_index, year_month


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


def is_flag_true(value: str) -> bool:
    return normalize_value(value) in {"yes", "y", "true", "1"}


def is_mailable(
    row: list,
    georgian_id_index: int,
    deceased_index: int,
    bounced_index: int,
    opt_in_index: int,
    email_opt_out_index: int,
    future_students_index: int,
) -> bool:
    if deceased_index != -1 and is_flag_true(get_cell(row, deceased_index)):
        return False
    if bounced_index != -1 and is_flag_true(get_cell(row, bounced_index)):
        return False
    if georgian_id_index != -1 and get_cell(row, georgian_id_index):
        return False
    if opt_in_index != -1 and not is_flag_true(get_cell(row, opt_in_index)):
        return False
    if email_opt_out_index != -1 and is_flag_true(
        get_cell(row, email_opt_out_index)
    ):
        return False
    if future_students_index != -1 and not is_flag_true(
        get_cell(row, future_students_index)
    ):
        return False
    return True


def unique_count(rows: list, id_i: int) -> int:
    if id_i < 0:
        return len(rows)
    seen: set[str] = set()
    blank_count = 0
    for row in rows:
        pid = get_cell(row, id_i)
        if pid:
            seen.add(pid)
        else:
            blank_count += 1
    return len(seen) + blank_count


def mailable_count(rows: list, headers: list, on_error=None) -> int:
    """Count unique rows that are mailable in the supplied cumulative range."""
    georgian_id_index = find_header_index(headers, GEORGIAN_ID_HEADER)
    deceased_index = find_header_index(headers, DECEASED_HEADER)
    bounced_index = find_header_index(headers, EMAIL_BOUNCED_HEADER)
    opt_in_index = find_header_index(headers, EMAIL_OPT_IN_HEADER)
    future_students_index = find_header_index(headers, FUTURE_STUDENTS_HEADER)
    email_opt_out_index = find_header_index(headers, EMAIL_OPT_OUT_HEADER)
    prospect_id_index = find_header_index(headers, PROSPECT_ID_HEADER)

    mailable_rows = []
    for row_number, row in enumerate(rows, start=1):
        try:
            if is_mailable(
                row,
                georgian_id_index,
                deceased_index,
                bounced_index,
                opt_in_index,
                email_opt_out_index,
                future_students_index,
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


def classify_lead_source(
    raw: str,
    categories: list[dict] | None = None,
) -> str:
    cats = categories if categories is not None else lead_categories([])
    text = (raw or "").strip()
    if not text:
        return "blank"
    key = text.casefold()
    if key in {"blank", "other"}:
        return key
    for cat in cats:
        if cat["key"] in {"other", "blank"}:
            continue
        aliases = cat.get("alias") or []
        if text in aliases:
            return cat["key"]
    return "other"


def map_lead_source(raw: str) -> str:
    return classify_lead_source(raw)


def _split_lead_sources(
    rows: list,
    leader_i: int,
    categories: list[dict],
    on_error=None,
) -> dict[str, list]:
    buckets = {cat["key"]: [] for cat in categories}
    buckets.setdefault("other", [])
    buckets.setdefault("blank", [])
    for i, row in enumerate(rows, start=1):
        try:
            raw = get_cell(row, leader_i)
            buckets[classify_lead_source(raw, categories)].append(row)
        except Exception as e:
            if on_error:
                on_error("lead_source", i, row, f"{type(e).__name__}: {e}")
    return buckets


def rows_through_month(rows: list, joined_i: int, through_ym: tuple[int, int]) -> list:
    kept = []
    for row in rows:
        joined = row[joined_i] if joined_i < len(row) else None
        ym = year_month(joined)
        if ym is not None and ym <= through_ym:
            kept.append(row)
    return kept


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


def filter_by_rules(source: dict, on_error=None, selected_sources=None) -> dict:
    headers = source["headers"]
    zip_i = find_header_index(headers, ZIP_HEADER)
    type_i = find_header_index(headers, APPLICANT_TYPE_HEADER)
    leader_i = source.get("leader_index", -1)
    joined_i = source.get("joined_index", -1)
    if zip_i == -1:
        raise ValueError("no Zip column")
    if type_i == -1:
        raise ValueError("no OH Applicant Type column")
    if leader_i == -1:
        raise ValueError("no Lead Source column")
    if joined_i == -1:
        raise ValueError("no Joined column")

    categories = lead_categories(selected_sources)
    prospect_id_index = find_header_index(headers, PROSPECT_ID_HEADER)

    def split(rows: list) -> dict:
        return {
            **_split_quadrants(rows, zip_i, type_i, on_error),
            **_split_lead_sources(rows, leader_i, categories, on_error),
        }

    current = split(source["current"])
    prior = split(source["prior"])
    dated = source.get("all", source["current"] + source["prior"])
    current_ym = source["current_ym"]
    prior_ym = source["prior_ym"]
    return {
        "current": current,
        "prior": prior,
        "lead_categories": categories,
        # Salesforce may already apply these rules; applying them again is
        # intentionally retained as a defensive, idempotent check.
        "current_mailable": mailable_count(
            rows_through_month(dated, joined_i, current_ym),
            headers,
            on_error,
        ),
        "prior_mailable": mailable_count(
            rows_through_month(dated, joined_i, prior_ym),
            headers,
            on_error,
        ),
        "new_this_month": unique_count(source["current"], prospect_id_index),
        "new_prior_month": unique_count(source["prior"], prospect_id_index),
        "prospect_id_index": prospect_id_index,
    }
