"""Stable Lead Source keys and optional alias groups from settings."""

from __future__ import annotations

import re

from pytool.settings import load_settings

RESERVED_KEYS = {"other", "blank"}


def normalize_alias(value: str) -> str:
    text = re.sub(r"[-‐‑‒–—_]+", " ", (value or "").strip().casefold())
    return " ".join(text.split())


def unique_key(name: str, used: set[str]) -> str:
    key = name.strip().casefold()
    used.add(key)
    if key in RESERVED_KEYS:
        return ""
    return key if key not in used else ""


def assign_keys(names: list[str]) -> list[dict]:
    used = set(RESERVED_KEYS)
    items = []
    for raw in names:
        text = str(raw).strip()
        if not text:
            continue
        key = unique_key(text, used)
        if key:
            items.append({
                "key": key, "value": text, "text": text,
            })
    return items


def _as_source(item) -> dict:
    if isinstance(item, str):
        text = item.strip()
        return {"key": text, "value": text, "alias": [text], "columnName": text}
    if not isinstance(item, dict):
        return {}
    value = str(item.get("value") or item.get("key") or "").strip()
    aliases = item.get("alias")
    aliases = [str(a).strip() for a in aliases]

    return {
        "key": str(item.get("key") or value).strip(),
        "value": value,
        "alias": aliases,
        "columnName": str(
            item.get("columnName")
        ).strip(),
    }


def lead_categories(selected: list | None) -> list[dict]:
    used = set(RESERVED_KEYS)
    cats = []
    if not selected:
        cats.append({"name": "Other", "key": "other", "alias": {"other"}})
        cats.append({"name": "Blank", "key": "blank", "alias": set()})
        return cats

    for item in selected:
        source = _as_source(item)
        aliases = {normalize_alias(a) for a in source.get("alias", [])}
        aliases.discard("")
        name = source.get("columnName") or source.get("value")
        if not name and not aliases:
            continue
        if not aliases and source.get("value"):
            aliases = {normalize_alias(source["value"])}
        key = unique_key(source.get("key") or name, used)
        cats.append({
            "name": name or key,
            "key": key,
            "alias": aliases,
        })
    cats.append({"name": "Other", "key": "other", "alias": {"other"}})
    cats.append({"name": "Blank", "key": "blank", "alias": set()})
    return cats
