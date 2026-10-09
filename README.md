# Find Researcher CV

A Codex Skill that verifies a researcher from their name and institution, selects their five highest-cited distinct publications in descending OpenAlex citation order, and creates a professionally edited one-page Chinese A4 LaTeX CV with traceable sources.

## Highlights

- Resolves identity before collecting biography and never merges namesakes.
- Uses only official personal or institutional pages, ORCID, OpenAlex, and Crossref as evidence.
- Maps every populated CV field to direct source URLs and access dates.
- Selects five verified formal publications by time-stamped OpenAlex citation count.
- Uses an official portrait when available and otherwise renders a no-photo layout.
- Generates a one-page PDF with blue clickable DOI links.

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

## Example request

> Use `find-researcher-cv` to research Lee Pooi See at Nanyang Technological University and produce a one-page Chinese A4 CV.

## Evidence policy

Search engines may locate candidate pages, but search snippets, social media, commercial biography sites, and Wikipedia are not accepted as evidence. Optional information is omitted when it cannot be verified.

OpenAlex citation counts are time-sensitive and are always reported with their query date.

## License

MIT License. See [LICENSE](LICENSE).
