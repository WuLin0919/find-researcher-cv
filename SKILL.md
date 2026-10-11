---
name: find-researcher-cv
description: Verify a researcher from their name and institution, select the five highest-cited distinct publications in descending citation order, and produce a professionally edited Chinese one-page A4 LaTeX CV with traceable sources. Use for public academic-profile research; do not use unapproved biography sources or merge ambiguous namesakes.
---

# Find Researcher CV

Produce an evidence-grounded, professionally written Chinese academic CV that fits
exactly one portrait A4 page. Treat the researcher's name and current or primary
institution as mandatory inputs.

## Required inputs

- Researcher name, in the spelling supplied by the user.
- Current or primary research institution.

If either input is missing, ask for it before browsing. Do not choose a demonstration
researcher on the user's behalf.

## Workflow

### 1. Resolve identity before collecting biography

Read [source-policy.md](references/source-policy.md). Search the official personal or
institutional profile first. Cross-check the person against ORCID and OpenAlex using
name, affiliation, topic, and publication overlap. If more than one candidate remains,
stop and ask the user to identify the correct person.

Do not combine records from namesakes.

### 2. Collect approved evidence

Use only these source families as evidence:

- official personal homepage;
- official institutional profile;
- ORCID;
- OpenAlex;
- Crossref.

Save direct URLs and access dates. Map every populated CV field to one or more evidence
records in `field_sources`. Use the contracts in
[profile-schema.md](references/profile-schema.md).

Omit an optional field that cannot be verified. Never infer private contact details,
education, employment, honors, or service.

### 3. Build and normalize the profile

Create `verified_profile.json` using the schema. Include only high-signal service and
major honors or talent titles. Then run:

```powershell
python scripts/normalize_profile.py --input verified_profile.json --output normalized_profile.json
```

The normalizer may clean display whitespace and order histories. It must not modify
provenance or factual values.

### 4. Select representative publications

Create a candidate `publications.json` with verified authorship, original-language
title, venue, formal publication date, DOI, OpenAlex citation count and query date,
OpenAlex URL, and Crossref URL when a DOI exists.

Run:

```powershell
python scripts/select_publications.py --input publications.json --output selected_publications.json
```

The deterministic policy is:

1. deduplicate by DOI, then normalized title;
2. prefer the formal version over a duplicate preprint;
3. sort all eligible works by OpenAlex citation count from highest to lowest;
4. select the first five works in that order.

If fewer than five verified works exist, use only those works and disclose the shortage
outside the CV.

### 5. Validate before drafting

Run:

```powershell
python scripts/validate_profile.py --profile normalized_profile.json --publications selected_publications.json --output profile_validation.json
```

Do not render when validation reports errors. Resolve conflicts using the source policy
or omit the affected optional field.

### 6. Calibrate and polish Chinese

Read [language-and-layout.md](references/language-and-layout.md) and use the required
three-pass process:

1. factual calibration against evidence;
2. concise professional Chinese editing with discipline-appropriate terminology;
3. post-edit comparison against the verified JSON.

Do not translate an official name without evidence. Keep publication titles in their
original language. Avoid promotional claims.

### 7. Use an official portrait or the fallback

Use a photo only when it comes from the same researcher's official personal or
institutional page. Record the source and access date, download a local copy, and set
`verified_official` to `true`. Otherwise omit the `photo` object entirely; the renderer
will use the no-photo header.

### 8. Render, compile, and enforce one page

Run from the Skill directory or use absolute paths:

```powershell
python scripts/render_cv.py --profile normalized_profile.json --publications selected_publications.json --template assets/researcher-cv-template.tex --output-dir output
```

The command must use `identity.name_original` (falling back to `identity.name_zh`) and
`identity.institution` to build the filename `<researcher name>_<institution>`. Characters
that are illegal in Windows filenames are replaced with `-`.

The working output directory must preserve:

- `<researcher name>_<institution>.tex`;
- `<researcher name>_<institution>.pdf`;
- `sources.md`;
- `verification_report.md`;
- `compilation.log`;
- a local `portrait.*` only when an official portrait is available.

After compilation and the one-page check succeed, publish a same-named folder on the
user's Desktop:

```text
Desktop/
└── <researcher name>_<institution>/
    ├── <researcher name>_<institution>.tex
    └── <researcher name>_<institution>.pdf
```

That Desktop folder must contain exactly those two files and no auxiliary files. Never
copy `sources.md`, `verification_report.md`, `compilation.log`, portrait files, or LaTeX
auxiliary files into it. Existing same-named TeX/PDF files may be overwritten. If the
same-named Desktop folder contains any other file, stop and report the conflict rather
than deleting user data. Use `--desktop-dir PATH` only when the user explicitly requests
another Desktop root or when testing the delivery step.

The renderer exits nonzero if XeLaTeX fails or the PDF is not exactly one page. If it
overflows, apply the documented compression order and rerun. Do not shrink text below a
legible print size.

Render every verified DOI as blue clickable text. The link target must be the canonical
`https://doi.org/<DOI>` resolver URL so it opens the corresponding article landing page.

### 9. Visually inspect the result

Render the PDF page to an image and inspect it for:

- exactly one portrait A4 page;
- no overflow, clipping, or overlapping blocks;
- readable Chinese glyphs and URLs;
- undistorted portrait;
- education and employment in the left column;
- service and major honors in the right column;
- thin horizontal separators between history rows, with both cells left-aligned and vertically centered;
- a clear, consistent vertical gap above every section heading;
- five representative publications in a full-width section below;
- blue DOI text whose PDF link target resolves through `https://doi.org/`;
- source families and verification date in the footer.

Report the exact two Desktop delivery paths and all remaining limitations.

## Non-negotiable rules

- Stop on ambiguous identity.
- Never use Wikipedia, commercial biography aggregators, social media, or search-result
  snippets as evidence.
- Never fill a missing field with a guess.
- Never use a non-official portrait.
- Never mix citation counts from different dates without recording their query dates.
- Never alter factual scope during language polishing.
- Preserve the LaTeX source and logs even when compilation fails.
