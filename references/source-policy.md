# Source and identity policy

## Identity resolution

Treat the supplied name and institution as a joint identity key, not as independent
search terms. Begin with a current official institutional profile or official personal
homepage. Confirm the candidate using at least one additional approved source whenever
possible. Strong identity signals include exact or known-variant name, current or
historical affiliation, department or field, ORCID, and overlapping works or coauthors.

Record the reasoning in `identity_resolution`. If two plausible people remain, stop and
ask the user to choose. Never merge profiles to create a more complete-looking CV.

## Approved evidence and precedence

Only these source types may support a CV claim:

1. `personal_homepage`: official page controlled by the researcher;
2. `institutional_profile`: official employing or affiliated institution page;
3. `orcid`: identity, identifiers, affiliations, and works recorded in ORCID;
4. `openalex`: authorship candidates and time-stamped citation counts;
5. `crossref`: canonical DOI metadata such as title, venue, year, and authors.

Search engines may locate these pages, but snippets are not evidence. Wikipedia,
commercial profiles, news reposts, social media, and unsourced CV aggregators are not
approved evidence.

Use current first-party evidence for current title, institution, department, contact
details, service, honors, and research directions. Use Crossref for canonical DOI
metadata and OpenAlex for citation counts. ORCID helps disambiguate identity but does
not override a newer first-party employment statement.

## Field-level provenance

Every populated CV field must have an entry in `field_sources` containing `source_type`,
direct `url`, and `accessed` date in `YYYY-MM-DD` form. Keep access dates even when
several fields share one URL. Omit optional fields with no approved source. Record
conflicts and omissions in `verification_report.md`.

## Conflict handling

- When personal and institutional pages disagree, prefer the clearly newer first-party
  statement and record both URLs and the decision.
- When a first-party page and ORCID disagree on current employment, use the current
  first-party statement and record the discrepancy.
- When Crossref and OpenAlex disagree on DOI metadata, use Crossref for DOI metadata and
  OpenAlex only for the citation count.
- When a source is unavailable, retain its URL and prior access date if already captured,
  lower confidence, and omit claims that can no longer be checked.
- When a conflict cannot be resolved, omit the field.

Do not draft the CV until identity is resolved and every included field has at least one
approved traceable source. When sources conflict, record the conflict and omit the field
unless current first-party evidence resolves it.

## Publication evidence

For each candidate work, verify target authorship; store the OpenAlex work URL, citation
count, and query date; verify DOI metadata with Crossref; deduplicate DOI first and title
second; and prefer a formal publication over its duplicate preprint. Citation counts
are measurements at a specific time and must include their query date.

## Portrait policy

Accept a portrait only from the target researcher's official personal page or official
institutional profile. Save the direct source URL and access date, download a local
copy, and preserve aspect ratio. Reject search thumbnails, social-media images,
conference galleries, news images, and uncertain identities. If no eligible photo is
available, use the no-photo layout.

## Stop conditions

Stop and request user input when name and institution still match more than one person,
the requested institution conflicts with all official profiles, a photo cannot be tied
to the resolved identity, or publication ownership cannot be separated from a namesake.
Absence of an optional field is not a stop condition; omit it cleanly.
