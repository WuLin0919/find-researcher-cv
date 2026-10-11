# Find Researcher CV

A Codex Skill that verifies a researcher from their name and institution, selects their five highest-cited distinct publications in descending OpenAlex citation order, and creates a professionally edited one-page Chinese A4 LaTeX CV with traceable sources.

## Highlights

- Resolves identity before collecting biography and never merges namesakes.
- Uses only official personal or institutional pages, ORCID, OpenAlex, and Crossref as evidence.
- Maps every populated CV field to direct source URLs and access dates.
- Selects five verified formal publications by time-stamped OpenAlex citation count.
- Uses an official portrait when available and otherwise renders a no-photo layout.
- Generates a one-page PDF with blue clickable DOI links.
- Delivers a Desktop folder named `<researcher name>_<institution>` containing only the
  equivalently named `.tex` and `.pdf` files.

## Requirements

- Python 3.10 or later
- [PyMuPDF](https://pymupdf.readthedocs.io/) (`pip install pymupdf`)
- XeLaTeX
- Internet access to the approved public sources

## Install

Replace `YOUR_USERNAME` with your GitHub username.

### Windows PowerShell

```powershell
git clone https://github.com/YOUR_USERNAME/find-researcher-cv.git "$env:USERPROFILE\.codex\skills\find-researcher-cv"
```

### macOS or Linux

```bash
git clone https://github.com/YOUR_USERNAME/find-researcher-cv.git ~/.codex/skills/find-researcher-cv
```

Start a new Codex conversation after installation.

## Output

The renderer keeps evidence, verification, compilation logs, and other support files in
its working output directory. After a successful one-page build, it creates this clean
delivery on the user's Desktop:

```text
<researcher name>_<institution>/
├── <researcher name>_<institution>.tex
└── <researcher name>_<institution>.pdf
```

Windows-illegal filename characters are replaced with `-`. The delivery folder never
contains logs, portraits, source notes, or LaTeX auxiliary files. For tests or a custom
Desktop root, pass `--desktop-dir PATH` to `scripts/render_cv.py`.

## Example request

> Use `find-researcher-cv` to research Lee Pooi See at Nanyang Technological University and produce a one-page Chinese A4 CV.

## Evidence policy

Search engines may locate candidate pages, but search snippets, social media, commercial biography sites, and Wikipedia are not accepted as evidence. Optional information is omitted when it cannot be verified.

OpenAlex citation counts are time-sensitive and are always reported with their query date.

## License

MIT License. See [LICENSE](LICENSE).
