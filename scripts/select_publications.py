from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from researcher_cv_common import clean_text, read_json, write_json


def canonical_key(publication: dict[str, Any]) -> str:
    doi = clean_text(publication.get("doi")).lower()
    if doi:
        doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)
        return "doi:" + doi
    title = re.sub(
        r"[^a-z0-9]+",
        "",
        clean_text(publication.get("title")).casefold(),
    )
    return "title:" + title


def deduplicate_publications(
    publications: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    chosen: dict[str, dict[str, Any]] = {}
    for publication in publications:
        if not publication.get("verified_author"):
            continue
        publication_kind = clean_text(
            publication.get("publication_kind") or "article"
        ).lower()
        if publication_kind not in {"article", "review"}:
            continue
        key = canonical_key(publication)
        current = chosen.get(key)
        if current is None or (
            current.get("is_preprint") and not publication.get("is_preprint")
        ):
            chosen[key] = dict(publication)
    return list(chosen.values())


def select_publications(
    publications: list[dict[str, Any]],
    count: int = 5,
) -> list[dict[str, Any]]:
    if count < 1:
        raise ValueError("count must be at least 1")

    canonical = deduplicate_publications(publications)
    top_cited = sorted(
        canonical,
        key=lambda item: (
            -int(item.get("cited_by_count") or 0),
            item.get("publication_date") or "",
        ),
    )[:count]

    selected: list[dict[str, Any]] = []
    for publication in top_cited:
        item = dict(publication)
        item["selection_reason"] = "highly_cited"
        selected.append(item)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Select the most highly cited verified publications."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()

    payload = read_json(args.input)
    candidates = payload.get("publications", [])
    if not isinstance(candidates, list):
        raise ValueError("The input publications field must be a list")
    selected = select_publications(candidates, count=args.count)
    write_json(
        args.output,
        {
            "selection_policy": "top_cited_descending",
            "requested_count": args.count,
            "selected_count": len(selected),
            "publications": selected,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
