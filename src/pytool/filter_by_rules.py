"""Split rows into Direct/IC quadrants and Lead Source buckets."""

import re

from pytool.constants import (
    APPLICANT_TYPE_HEADER,
    DIRECT_VALUES,
    IC_POSTAL_PREFIXES,
    NON_EMPTY_VALUE,
    PROSPECT_ID_HEADER,
    ZIP_HEADER,
)
from pytool.lead_source import lead_categories
from pytool.read_source_data import find_configured_header_index
from pytool.settings import (
    get_classification_rules,
    get_field_mapping,
    get_mailable_conditions,
    get_nurture_config,
)
from pytool.nurture import load_nurture_values
def get_cell(row: list, index: int) -> str:
    if index < 0 or index >= len(row) or row[index] is None:
        return ""
    return str(row[index]).strip()


def normalize_value(value: str) -> str:
    text = re.sub(r"[-‐‑‒–—_]+", " ", (value or "").strip().casefold())
    return " ".join(text.split())


def postal_key(zip_code: str) -> str:
    return "".join(zip_code.split()).upper()


def is_ic(zip_code: str, ic_postal_prefixes=IC_POSTAL_PREFIXES) -> bool:
    compact = postal_key(zip_code)
    if not compact or not ic_postal_prefixes:
        return False
    if compact in ic_postal_prefixes:
        return True
    return compact[:3] in ic_postal_prefixes


def is_direct(
    applicant_type: str,
    direct_values=DIRECT_VALUES,
) -> bool:
    return normalize_value(applicant_type) in {
        normalize_value(value) for value in direct_values
    }


def is_flag_true(value: str, true_values=None) -> bool:
    values = true_values or ("Yes", "Y", "True", "1")
    if NON_EMPTY_VALUE in values:
        return bool((value or "").strip())
    normalized = {normalize_value(item) for item in values}
    return normalize_value(value) in normalized


def is_mailable(
    row: list,
    mailable_conditions=None,
    condition_indices=None,
) -> bool:
    """Apply configured mailable_conditions only (rules/values are settings legacy)."""
    for condition in mailable_conditions or []:
        if not condition.get("enabled", True):
            continue
        index = (condition_indices or {}).get(condition["key"], -1)
        if index == -1:
            continue
        value = get_cell(row, index)
        mode = condition["mode"]
        values = condition.get("values", [])
        matches_value = is_flag_true(value, values)
        non_empty = bool(value)
        if mode == "exclude_if_value" and matches_value:
            return False
        if mode == "require_value" and not matches_value:
            return False
        if mode == "exclude_if_non_empty" and non_empty:
            return False
        if mode == "require_non_empty" and not non_empty:
            return False
        if mode == "exclude_if_empty" and not non_empty:
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


def mailable_count(
    rows: list,
    headers: list,
    on_error=None,
    mailable_conditions=None,
    nurture_values=None,
) -> int:
    """Count unique mailable rows in the supplied month slice."""
    mapping = get_field_mapping()
    prospect_id_index = find_configured_header_index(
        headers, mapping["prospect_id"], PROSPECT_ID_HEADER
    )
    condition_indices = {
        condition["key"]: find_configured_header_index(
            headers,
            mapping.get(condition["field"], [condition["field"]]),
            [condition["field"]],
        )
        for condition in (mailable_conditions or [])
    }

    mailable_rows = []
    nurture_field = get_nurture_config()["report_field"]
    nurture_index = find_configured_header_index(
        headers, mapping.get(nurture_field, [nurture_field]), [nurture_field]
    )
    for row_number, row in enumerate(rows, start=1):
        try:
            if nurture_values and nurture_index != -1 and get_cell(row, nurture_index) in nurture_values:
                continue
            if is_mailable(row, mailable_conditions, condition_indices):
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


def _split_quadrants(
    rows: list,
    zip_i: int,
    type_i: int,
    on_error=None,
    classification_rules=None,
) -> dict[str, list]:
    buckets = {
        "direct_ic": [],
        "direct_ooc": [],
        "non_direct_ic": [],
        "non_direct_ooc": [],
    }
    for i, row in enumerate(rows, start=1):
        try:
            ic = is_ic(
                get_cell(row, zip_i),
                classification_rules["ic_postal_prefixes"],
            )
            direct = is_direct(
                get_cell(row, type_i),
                classification_rules["direct_applicant_types"],
            )
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
    mapping = get_field_mapping()
    zip_i = find_configured_header_index(headers, mapping["zip"], ZIP_HEADER)
    type_i = find_configured_header_index(headers, mapping["applicant_type"], APPLICANT_TYPE_HEADER)
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
    classification_rules = get_classification_rules()
    mailable_conditions = get_mailable_conditions()
    nurture_values = load_nurture_values()
    prospect_id_index = find_configured_header_index(
        headers, mapping["prospect_id"], PROSPECT_ID_HEADER
    )

    def split(rows: list) -> dict:
        return {
            **_split_quadrants(
                rows, zip_i, type_i, on_error, classification_rules
            ),
            **_split_lead_sources(rows, leader_i, categories, on_error),
        }

    current = split(source["current"])
    prior = split(source["prior"])
    return {
        "current": current,
        "prior": prior,
        "lead_categories": categories,
        # Total mailable = mailable among prospects who Joined that month only.
        "current_mailable": mailable_count(
            source["current"],
            headers,
            on_error,
            mailable_conditions,
            nurture_values,
        ),
        "prior_mailable": mailable_count(
            source["prior"],
            headers,
            on_error,
            mailable_conditions,
            nurture_values,
        ),
        "new_this_month": unique_count(source["current"], prospect_id_index),
        "new_prior_month": unique_count(source["prior"], prospect_id_index),
        "prospect_id_index": prospect_id_index,
    }
