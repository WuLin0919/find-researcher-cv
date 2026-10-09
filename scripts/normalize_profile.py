from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from researcher_cv_common import clean_text, read_json, write_json


def _year(value: object, default: int) -> int:
    if value in (None, ""):
        return default
    try:
        return int(str(value))
    except ValueError:
        return default


def _clean_record(record: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in record.items():
        if isinstance(value, str):
            text = clean_text(value)
            if text:
                cleaned[key] = text
        else:
            cleaned[key] = value
    return cleaned


def sort_history(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned = [_clean_record(record) for record in records]
    return sorted(
        cleaned,
        key=lambda item: (
            _year(item.get("end_year"), 9999),
            _year(item.get("start_year"), 0),
        ),
        reverse=True,
    )


def _clean_mapping(mapping: dict[str, Any]) -> dict[str, str]:
    return {
        key: clean_text(value)
        for key, value in mapping.items()
        if clean_text(value)
    }


def normalize_profile(profile: dict[str, Any]) -> dict[str, Any]:
    result = dict(profile)
    result["identity"] = _clean_mapping(profile.get("identity", {}))
    result["contact"] = _clean_mapping(profile.get("contact", {}))
    result["research_interests"] = [
        clean_text(value)
        for value in profile.get("research_interests", [])
        if clean_text(value)
    ]
    for field in ("education", "employment", "service", "major_honors"):
        result[field] = sort_history(profile.get(field, []))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize verified researcher profile display fields."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    write_json(args.output, normalize_profile(read_json(args.input)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
