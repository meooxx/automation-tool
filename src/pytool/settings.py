import json
import logging
from pathlib import Path

from pytool.paths import app_root
from pytool.constants import (
    DEFAULT_FIELD_MAPPING,

    DEFAULT_MAILABLE_CONDITIONS,
    DEFAULT_NURTURE_CONFIG,
    DEFAULT_IC_POSTAL_PREFIXES,
    DIRECT_VALUES,
    NON_EMPTY_VALUE,
)

logger = logging.getLogger("pytool")


def settings_file() -> Path:
    return app_root() / "config" / "settings.json"


def load_settings() -> dict:
    path = settings_file()
    if not path.is_file():
        Path(path.parent).mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            logger.error("Settings file is not a JSON object: %s", path)
            return {}
        return data
    except (OSError, json.JSONDecodeError):
        logger.exception("Unable to read settings file: %s", path)
        return {}


def save_settings(data: dict) -> None:
    path = settings_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return True


def get_configuration() -> dict:
    data = load_settings()
    data["settings_path"] = str(settings_file())
    data["settings_dir"] = str(settings_file().parent)
    data["classification_rules"] = get_classification_rules()

    data["mailable_conditions"] = get_mailable_conditions()
    data["nurture"] = get_nurture_config()
    data["field_mapping"] = get_field_mapping()
    return data


def update_configuration(changes: dict) -> dict:
    if not isinstance(changes, dict):
        raise ValueError("configuration changes must be an object")
    data = load_settings()
    data.update(changes)
    if "classification_rules" in changes:
        rules = changes["classification_rules"]
        if not isinstance(rules, dict):
            raise ValueError("classification_rules must be an object")
        data["classification_rules"] = {
            "direct_applicant_types": _clean_values(
                rules.get("direct_applicant_types"),
                DIRECT_VALUES,
            ),
            "ic_postal_prefixes": _clean_values(
                rules.get("ic_postal_prefixes"),
                DEFAULT_IC_POSTAL_PREFIXES,
            ),
        }

    if "mailable_conditions" in changes:
        data["mailable_conditions"] = get_mailable_conditions(
            changes["mailable_conditions"]
        )
    if "nurture" in changes:
        data["nurture"] = get_nurture_config(changes["nurture"])
    if "field_mapping" in changes:
        data["field_mapping"] = get_field_mapping(changes["field_mapping"])
    save_settings(data)
    return get_configuration()


def get_log_path() -> Path:
    log_path = app_root() / "errors.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch(exist_ok=True)
    return log_path


def get_classification_rules() -> dict[str, list[str]]:
    configured = load_settings().get("classification_rules", {})
    if not isinstance(configured, dict):
        configured = {}
    direct = _clean_values(
        configured.get("direct_applicant_types"),
        DIRECT_VALUES,
    )
    prefixes = _clean_values(
        configured.get("ic_postal_prefixes"),
        DEFAULT_IC_POSTAL_PREFIXES,
    )
    return {
        "direct_applicant_types": direct,
        "ic_postal_prefixes": prefixes,
    }


def get_mailable_conditions(overrides=None) -> list[dict]:
    configured = overrides
    if configured is None:
        settings = load_settings()
        configured = settings.get("mailable_conditions")
        if configured is None:

            configured = [dict(condition)
                          for condition in DEFAULT_MAILABLE_CONDITIONS]

    result = []
    seen = set()
    for item in configured:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key", "")).strip()
        field = str(item.get("field", "")).strip()
        label = str(item.get("label", key)).strip() or key
        mode = str(item.get("mode", "")).strip()
        if not key or not field or not mode or key in seen:
            continue
        if mode not in {
            "exclude_if_value",
            "require_value",
            "exclude_if_non_empty",
            "require_non_empty",
            "exclude_if_empty",
        }:
            continue
        seen.add(key)
        result.append({
            "key": key,
            "label": label,
            "field": field,
            "mode": mode,
            "enabled": item.get("enabled", True) is True,
            "values": _clean_values(item.get("values"), []),
        })
    return result


def get_field_mapping(overrides=None) -> dict[str, list[str]]:
    configured = overrides
    if configured is None:
        configured = load_settings().get("field_mapping", {})
    if not isinstance(configured, dict):
        configured = {}
    result = {
        key: _clean_values(configured.get(key), defaults)
        for key, defaults in DEFAULT_FIELD_MAPPING.items()
    }
    for key, values in configured.items():
        if key not in result and isinstance(key, str):
            cleaned = _clean_values(values, [])
            if cleaned:
                result[key.strip()] = cleaned
    return result


def get_nurture_config(overrides=None) -> dict[str, str]:
    configured = overrides
    if configured is None:
        configured = load_settings().get("nurture", {})
    if not isinstance(configured, dict):
        configured = {}
    report_field = configured.get(
        "report_field",
        DEFAULT_NURTURE_CONFIG["report_field"],
    )
    return {
        "file_path": str(configured.get("file_path", "")).strip(),
        "report_field": str(report_field).strip() or DEFAULT_NURTURE_CONFIG["report_field"],
        "nurture_header": str(
            configured.get("nurture_header",
                           DEFAULT_NURTURE_CONFIG["report_field"])
        ).strip(),
        "enable": bool(configured.get("enable", False)),
    }


def save_classification_rules(rules: dict) -> dict[str, list[str]]:
    if not isinstance(rules, dict):
        raise ValueError("classification rules must be an object")
    direct = _clean_values(rules.get("direct_applicant_types"), ())
    prefixes = _clean_values(rules.get("ic_postal_prefixes"), ())
    if not direct:
        raise ValueError("at least one Direct applicant type is required")
    if not prefixes:
        raise ValueError("at least one IC ZIP prefix is required")
    normalized = {
        "direct_applicant_types": direct,
        "ic_postal_prefixes": prefixes,
    }
    data = load_settings()
    data["classification_rules"] = normalized
    save_settings(data)
    return normalized


def reset_classification_rule(section: str) -> dict[str, list[str]]:
    if section not in {"direct_applicant_types", "ic_postal_prefixes"}:
        raise ValueError(f"unknown classification rule: {section}")
    current = get_classification_rules()
    defaults = {
        "direct_applicant_types": list(DIRECT_VALUES),
        "ic_postal_prefixes": list(DEFAULT_IC_POSTAL_PREFIXES),
    }
    current[section] = defaults[section]
    return save_classification_rules(current)


def _clean_values(value, fallback) -> list[str]:
    values = value if isinstance(value, list) else fallback
    result = []
    seen = set()
    for item in values:
        text = str(item).strip()
        if text.casefold() in {"non-empty", "non_empty", NON_EMPTY_VALUE.casefold()}:
            text = NON_EMPTY_VALUE
        if text and text.casefold() not in seen:
            seen.add(text.casefold())
            result.append(text)
    return result or list(fallback)
