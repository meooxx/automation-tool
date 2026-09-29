"""Approximate filters. Swap value sets in constants.py after MCR confirms."""

from pytool.constants import (
    APPLICANT_TYPE_HEADER,
    DIRECT_MATCH,
    IC_MATCH,
    NON_DIRECT_MATCH,
    OOC_MATCH,
    RESD_HEADER,
    LEAD_SOURCE_CATEGORIES
)
from pytool.read_source_data import find_header_index


def get_cell(row: list, index: int) -> str:
    if index < 0 or index >= len(row) or row[index] is None:
        return ""
    return str(row[index]).strip()


def is_ic(resd: str) -> bool:
    if not resd or OOC_MATCH.search(resd):
        return False
    return bool(IC_MATCH.search(resd))


def is_direct(applicant_type: str) -> bool:
    if not applicant_type or NON_DIRECT_MATCH.search(applicant_type):
        return False
    return bool(DIRECT_MATCH.search(applicant_type))


def map_lead_source(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return "blank"
    for cat in LEAD_SOURCE_CATEGORIES:
        pattern = cat.get("match")
        if pattern and pattern.search(text):
            return cat["key"]
    return "not_listed"


def _split_lead_sources(rows: list, leader_i: int) -> dict[str, list]:
    buckets = {cat["key"]: [] for cat in LEAD_SOURCE_CATEGORIES}
    buckets["not_listed"] = []
    for row in rows:
        buckets[map_lead_source(get_cell(row, leader_i))].append(row)
    return buckets


def _split_quadrants(rows: list, resd_i: int, type_i: int) -> dict[str, list]:
    buckets = {
        "direct_ic": [],
        "direct_ooc": [],
        "non_direct_ic": [],
        "non_direct_ooc": [],
    }
    for row in rows:
        ic = is_ic(get_cell(row, resd_i))
        direct = is_direct(get_cell(row, type_i))
        if direct and ic:
            buckets["direct_ic"].append(row)
        elif direct:
            buckets["direct_ooc"].append(row)
        elif ic:
            buckets["non_direct_ic"].append(row)
        else:
            buckets["non_direct_ooc"].append(row)
    return buckets


def filter_by_rules(source: dict) -> dict:
    """Resd x Applicant Type quadrants, plus Lead Source buckets."""
    headers = source["headers"]
    resd_i = find_header_index(headers, RESD_HEADER)
    type_i = find_header_index(headers, APPLICANT_TYPE_HEADER)
    leader_i = source.get("leader_index", -1)
    if resd_i == -1:
        raise ValueError("no Resd Code IRx column")
    if type_i == -1:
        raise ValueError("no OH Applicant Type column")
    if leader_i == -1:
        raise ValueError("no Lead Source column")

    def split(rows: list) -> dict:
        return {
            **_split_quadrants(rows, resd_i, type_i),
            **_split_lead_sources(rows, leader_i),
        }

    return {
        "current": split(source["current"]),
        "prior": split(source["prior"]),
    }
