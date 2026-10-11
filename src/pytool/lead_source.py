"""Build Lead Source report columns from selected sources."""

from __future__ import annotations

RESERVED_KEYS = {"other", "blank"}


def lead_categories(selected: list | None) -> list[dict]:
    """
    Each selected source:
      - columnName -> report header name
      - alias -> exact Lead Source cell values that count in that column
    Other / Blank are not built here.
    """
    cats: list[dict] = []

    for item in selected or []:
        if not isinstance(item, dict):
            continue
        column_name = str(item.get("columnName") or "").strip()
        aliases = item.get("alias") or []
        if not isinstance(aliases, list):
            aliases = []
        aliases = [
            str(a).strip()
            for a in aliases
            if a is not None and str(a).strip()
        ]
        value = str(item.get("value") or "").strip()
        if value and value not in aliases:
            aliases = [value, *aliases]
        if not column_name or not aliases:
            continue

        key = str(item.get("key") or column_name).strip().casefold()
        if key in RESERVED_KEYS:
            continue

        cats.append({
            "name": column_name,
            "key": key,
            "alias": aliases,
        })
    return cats
