# Language calibration and one-page layout

## Three-pass language process

### Pass 1: factual calibration

Compare every planned display field with `verified_profile.json`, `publications.json`,
and field-level sources. Resolve or omit conflicts before editing. Freeze dates,
organizations, positions, degree levels, award scope, DOI metadata, and citation counts.

### Pass 2: professional Chinese editing

Use concise academic Chinese and discipline-appropriate technical terminology. Prefer
official Chinese names for institutions, titles, awards, talent programs, societies,
and research areas. If no official Chinese name is verifiable, retain the official
original-language form instead of inventing a translation.

Use noun phrases where possible. Remove repetitive introductions and vague adjectives.
Do not write unsupported promotional claims such as “国际顶尖”“世界领先”“著名科学家”.
Keep publication titles in their original language and do not paraphrase them.

### Pass 3: post-edit verification

Compare polished strings with the frozen record. Confirm that editing did not add,
broaden, strengthen, or merge claims. Re-run `validate_profile.py`. Record the check,
omissions, and unresolved limitations in `verification_report.md`.

## Approved A4 structure

The PDF is portrait A4 and exactly one page.

1. **Header:** name, current institution, title, email, homepage, and ORCID on the left;
   a verified official portrait on the right. With no photo, expand the identity block.
2. **Research directions:** one concise, full-width row below the header.
3. **Middle left column:** education followed by employment.
4. **Middle right column:** academic or institutional service followed by major honors
   and awards.
5. **Bottom full-width section:** the selected representative publications.
6. **Footer:** source families and verification date; keep long URLs in `sources.md`.

In publication entries, render the DOI itself in blue and make it clickable. Link to
the canonical DOI resolver URL `https://doi.org/<DOI>`, not to an API endpoint.

Omit missing optional sections cleanly. Do not print “unknown,” “not found,” blank
frames, or speculative substitutions.

For education, employment, service, and honor entries, separate every record with a
thin horizontal rule. Keep both the date cell and description cell left-aligned, and
vertically center their contents within the row when the description wraps.
Use compact fixed vertical padding so a one-line record remains visibly shorter than a
wrapped multi-line record; let multi-line rows expand only as required by their text.
Give every section heading a visible, consistent vertical gap above it so the heading
cannot be mistaken for part of the preceding ruled row.

## Compression order

When the draft exceeds one page, make changes in this exact order:

1. remove repetitive role descriptions;
2. express research directions as precise professional keywords;
3. reduce education and employment entries to dates, institution, and degree or title;
4. retain only the most important service and honors;
5. abbreviate publication author lists while keeping target authorship evident;
6. tighten vertical spacing within legibility limits.

Do not remove identity/contact information, verified representative publications,
verification date, or source traceability merely to meet the page limit. Do not reduce
body text below a legible print size.

## Visual acceptance checklist

- one portrait A4 page;
- no clipped, overlapping, or overflowing text;
- readable Chinese glyphs, English titles, DOI strings, and contact details;
- every displayed DOI is blue and has a working `https://doi.org/` PDF link annotation;
- aligned top edges for the two middle columns;
- thin row separators, left-aligned cells, and vertically centered row contents;
- a clear vertical gap between each section heading and the content above it;
- education and employment only in the left column;
- service and honors only in the right column;
- publications begin below both columns and span the full text width;
- portrait preserves aspect ratio and belongs to the resolved person;
- footer states source families and verification date.
