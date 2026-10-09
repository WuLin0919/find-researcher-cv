# Researcher profile data contract

The workflow keeps factual records in UTF-8 JSON. Display-language editing may improve
Chinese wording, but it must not change dates, organizations, positions, award scope,
publication metadata, or citation counts.

## `verified_profile.json`

```json
{
  "identity": {
    "name_original": "Ming Zhang",
    "name_zh": "张明",
    "institution": "Example University",
    "title": "Professor"
  },
  "contact": {
    "email": "ming.zhang@example.edu",
    "homepage": "https://example.edu/ming-zhang",
    "orcid": "0000-0000-0000-0001"
  },
  "photo": {
    "local_path": "portrait.jpg",
    "source_url": "https://example.edu/images/ming-zhang.jpg",
    "source_type": "institutional_profile",
    "accessed": "2026-10-07",
    "verified_official": true
  },
  "research_interests": [
    "物理信息机器学习",
    "多尺度计算物理"
  ],
  "education": [
    {
      "start_year": 2004,
      "end_year": 2008,
      "organization": "Example University",
      "role": "物理学学士"
    }
  ],
  "employment": [
    {
      "start_year": 2021,
      "end_year": null,
      "organization": "Example University",
      "role": "教授"
    }
  ],
  "service": [
    {
      "start_year": 2023,
      "end_year": null,
      "organization": "Example Society",
      "role": "专业委员会委员"
    }
  ],
  "major_honors": [
    {
      "start_year": 2024,
      "end_year": 2024,
      "organization": "Awarding organization",
      "role": "重要人才称号或奖项"
    }
  ],
  "field_sources": {
    "identity.name_original": [
      {
        "source_type": "institutional_profile",
        "url": "https://example.edu/ming-zhang",
        "accessed": "2026-10-07"
      }
    ],
    "identity.institution": [
      {
        "source_type": "institutional_profile",
        "url": "https://example.edu/ming-zhang",
        "accessed": "2026-10-07"
      }
    ],
    "identity.title": [
      {
        "source_type": "institutional_profile",
        "url": "https://example.edu/ming-zhang",
        "accessed": "2026-10-07"
      }
    ],
    "contact.email": [
      {
        "source_type": "personal_homepage",
        "url": "https://example.edu/ming-zhang",
        "accessed": "2026-10-07"
      }
    ],
    "contact.homepage": [
      {
        "source_type": "personal_homepage",
        "url": "https://example.edu/ming-zhang",
        "accessed": "2026-10-07"
      }
    ],
    "contact.orcid": [
      {
        "source_type": "orcid",
        "url": "https://orcid.org/0000-0000-0000-0001",
        "accessed": "2026-10-07"
      }
    ],
    "research_interests": [
      {
        "source_type": "institutional_profile",
        "url": "https://example.edu/ming-zhang",
        "accessed": "2026-10-07"
      }
    ],
    "education": [
      {
        "source_type": "institutional_profile",
        "url": "https://example.edu/ming-zhang",
        "accessed": "2026-10-07"
      }
    ],
    "employment": [
      {
        "source_type": "institutional_profile",
        "url": "https://example.edu/ming-zhang",
        "accessed": "2026-10-07"
      }
    ],
    "service": [
      {
        "source_type": "institutional_profile",
        "url": "https://example.edu/ming-zhang",
        "accessed": "2026-10-07"
      }
    ],
    "major_honors": [
      {
        "source_type": "institutional_profile",
        "url": "https://example.edu/ming-zhang",
        "accessed": "2026-10-07"
      }
    ]
  },
  "verification_date": "2026-10-07",
  "identity_resolution": {
    "status": "resolved",
    "matched_institution": "Example University",
    "notes": "Official profile and ORCID refer to the same person."
  }
}
```

Omit an unverified optional field rather than leaving a claim without provenance. The
`photo` object is optional and may be present only when the image comes from the
researcher's official personal page or institutional profile.

## `publications.json`

Candidate and selected publications use the same record shape. Selected records add
`selection_reason`, whose value is `highly_cited`.

```json
{
  "selection_policy": "top_cited_descending",
  "requested_count": 5,
  "selected_count": 1,
  "publications": [
    {
      "id": "W1234567890",
      "title": "Original-language paper title",
      "doi": "10.1000/example",
      "authors": ["Ming Zhang", "Coauthor"],
      "display_authors": "Ming Zhang et al.",
      "venue": "Journal Name",
      "publication_kind": "article",
      "publication_date": "2025-06-01",
      "cited_by_count": 42,
      "citation_query_date": "2026-10-07",
      "verified_author": true,
      "is_preprint": false,
      "openalex_url": "https://openalex.org/W1234567890",
      "crossref_url": "https://api.crossref.org/works/10.1000/example",
      "selection_reason": "highly_cited"
    }
  ]
}
```

OpenAlex supplies the time-sensitive citation count. Crossref verifies title, venue,
year, and DOI whenever a DOI exists. DOI-equivalent records are merged, and a formal
version replaces its duplicate preprint. `publication_kind` must be `article` or
`review` for selection; books, chapters, issue covers, editorials, datasets, and other
non-paper records remain in the audit trail but are excluded from the five-paper CV.
`authors` always preserves the complete verified list. `display_authors` is optional and
may abbreviate a long list for the one-page layout only when the target researcher's
authorship remains explicit.

## Allowed source types

- `personal_homepage`
- `institutional_profile`
- `orcid`
- `openalex`
- `crossref`

Other source families are discovery aids only and must not support claims in the CV.

## Validation output

```json
{
  "errors": [],
  "warnings": [
    "Only 4 verified publications are available; fewer than five will be shown."
  ],
  "valid": true
}
```

Errors block rendering because they indicate an unresolved identity, unsupported
claim, invalid provenance, unofficial portrait, or untraceable publication. Warnings
do not block rendering; they disclose a legitimate limitation such as fewer than five
verified distinct publications.
