from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from researcher_cv_common import clean_text, read_json, write_json


ALLOWED_SOURCE_TYPES = {
    "personal_homepage",
    "institutional_profile",
    "orcid",
    "openalex",
    "crossref",
}
OFFICIAL_PHOTO_SOURCE_TYPES = {"personal_homepage", "institutional_profile"}
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")


def validate_source(source: dict[str, Any], field: str) -> list[str]:
    errors: list[str] = []
    source_type = source.get("source_type")
    if source_type not in ALLOWED_SOURCE_TYPES:
        errors.append(f"{field}: unapproved source_type {source_type}")
    if not clean_text(source.get("url")).startswith(("http://", "https://")):
        errors.append(f"{field}: source URL is missing or invalid")
    if not DATE_PATTERN.fullmatch(clean_text(source.get("accessed"))):
        errors.append(f"{field}: access date must use YYYY-MM-DD")
    return errors


def _populated_fields(profile: dict[str, Any]) -> list[str]:
    fields: list[str] = []
    for group in ("identity", "contact"):
        values = profile.get(group, {})
        if isinstance(values, dict):
            fields.extend(
                f"{group}.{key}"
                for key, value in values.items()
                if clean_text(value)
            )
    for field in (
        "research_interests",
        "education",
        "employment",
        "service",
        "major_honors",
    ):
        if profile.get(field):
            fields.append(field)
    return fields


def _validate_publications(
    publications: list[dict[str, Any]],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    verified_count = 0

    for index, publication in enumerate(publications, start=1):
        label = f"publications[{index}]"
        if not publication.get("verified_author"):
            errors.append(f"{label}: researcher authorship is not verified")
        else:
            verified_count += 1
        if not clean_text(publication.get("title")):
            errors.append(f"{label}: title is required")
        if not clean_text(publication.get("openalex_url")).startswith(
            ("http://", "https://")
        ):
            errors.append(f"{label}: OpenAlex URL is missing or invalid")
        if not DATE_PATTERN.fullmatch(
            clean_text(publication.get("citation_query_date"))
        ):
            errors.append(f"{label}: citation_query_date must use YYYY-MM-DD")
        if clean_text(publication.get("doi")) and not clean_text(
            publication.get("crossref_url")
        ).startswith(("http://", "https://")):
            errors.append(f"{label}: DOI records require a Crossref URL")

    if verified_count < 5:
        warnings.append(
            f"Only {verified_count} verified publications are available; "
            "fewer than five will be shown."
        )
    return errors, warnings


def validate_profile_report(
    profile: dict[str, Any],
    publications: list[dict[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    identity = profile.get("identity", {})
    if not isinstance(identity, dict):
        identity = {}

    for field in ("name_original", "institution", "title"):
        if not clean_text(identity.get(field)):
            errors.append(f"identity.{field} is required")

    field_sources = profile.get("field_sources", {})
    if not isinstance(field_sources, dict):
        errors.append("field_sources must be an object")
        field_sources = {}

    for field in _populated_fields(profile):
        sources = field_sources.get(field)
        if not isinstance(sources, list) or not sources:
            errors.append(f"{field}: no approved source recorded")
            continue
        for source in sources:
            if not isinstance(source, dict):
                errors.append(f"{field}: source record must be an object")
                continue
            errors.extend(validate_source(source, field))

    photo = profile.get("photo")
    if photo:
        if not isinstance(photo, dict):
            errors.append("photo must be an object")
        else:
            if not photo.get("verified_official"):
                errors.append("photo is not verified as official")
            if photo.get("source_type") not in OFFICIAL_PHOTO_SOURCE_TYPES:
                errors.append(
                    "photo must come from a personal homepage or institutional profile"
                )
            photo_source = {
                "source_type": photo.get("source_type"),
                "url": photo.get("source_url"),
                "accessed": photo.get("accessed"),
            }
            errors.extend(validate_source(photo_source, "photo"))

    publication_errors, publication_warnings = _validate_publications(publications)
    errors.extend(publication_errors)
    warnings.extend(publication_warnings)
    return {"errors": errors, "warnings": warnings, "valid": not errors}


def validate_profile(
    profile: dict[str, Any],
    publications: list[dict[str, Any]],
) -> list[str]:
    return validate_profile_report(profile, publications)["errors"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a verified researcher profile and publications."
    )
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--publications", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    profile = read_json(args.profile)
    publication_payload = read_json(args.publications)
    publications = publication_payload.get("publications", [])
    if not isinstance(publications, list):
        raise ValueError("The publications field must be a list")
    report = validate_profile_report(profile, publications)
    write_json(args.output, report)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
