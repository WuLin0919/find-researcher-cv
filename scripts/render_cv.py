from __future__ import annotations

import argparse
import copy
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Iterable

from researcher_cv_common import clean_text, read_json


SOURCE_LABELS = {
    "personal_homepage": "本人官网",
    "institutional_profile": "机构官网",
    "orcid": "ORCID",
    "openalex": "OpenAlex",
    "crossref": "Crossref",
}

WINDOWS_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def latex_escape(value: object) -> str:
    text = clean_text(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in text)


def safe_filename_component(value: object) -> str:
    """Return a readable cross-platform filename component."""
    component = re.sub(r"\s+", " ", clean_text(value)).strip(" .")
    component = WINDOWS_INVALID_FILENAME_CHARS.sub("-", component).strip(" .")
    if not component:
        raise ValueError("Researcher name and institution must not be empty")
    return component


def delivery_basename(profile: dict[str, Any]) -> str:
    identity = profile.get("identity", {})
    if not isinstance(identity, dict):
        raise ValueError("Profile identity must be an object")
    name = identity.get("name_original") or identity.get("name_zh")
    institution = identity.get("institution")
    return (
        safe_filename_component(name)
        + "_"
        + safe_filename_component(institution)
    )


def default_desktop_dir() -> Path:
    """Resolve the user's Desktop, including a Windows redirected Desktop."""
    if os.name == "nt":
        try:
            import ctypes

            buffer = ctypes.create_unicode_buffer(260)
            result = ctypes.windll.shell32.SHGetFolderPathW(
                None, 0x10, None, 0, buffer
            )
            if result == 0 and buffer.value:
                return Path(buffer.value)
        except (AttributeError, OSError):
            pass
    return Path.home() / "Desktop"


def publish_final_pair(
    profile: dict[str, Any],
    tex_path: Path,
    pdf_path: Path,
    desktop_dir: Path,
) -> tuple[Path, Path]:
    """Publish exactly one renamed TeX/PDF pair into a Desktop folder."""
    basename = delivery_basename(profile)
    target_dir = desktop_dir.expanduser() / basename
    expected_names = {f"{basename}.tex", f"{basename}.pdf"}

    if target_dir.exists() and not target_dir.is_dir():
        raise FileExistsError(
            f"Desktop delivery path exists but is not a folder: {target_dir}"
        )
    target_dir.mkdir(parents=True, exist_ok=True)

    existing = {path.name for path in target_dir.iterdir()}
    unexpected = sorted(existing - expected_names)
    if unexpected:
        raise FileExistsError(
            "Refusing to replace Desktop delivery folder because it contains "
            f"unexpected files: {', '.join(unexpected)}"
        )
    non_files = sorted(
        path.name for path in target_dir.iterdir() if not path.is_file()
    )
    if non_files:
        raise FileExistsError(
            "Refusing to replace Desktop delivery folder because expected output "
            f"paths are not files: {', '.join(non_files)}"
        )

    delivered_tex = target_dir / f"{basename}.tex"
    delivered_pdf = target_dir / f"{basename}.pdf"
    shutil.copy2(tex_path, delivered_tex)
    shutil.copy2(pdf_path, delivered_pdf)

    delivered_names = {path.name for path in target_dir.iterdir()}
    if delivered_names != expected_names:
        raise RuntimeError(
            f"Desktop delivery folder must contain exactly: {sorted(expected_names)}"
        )
    return delivered_tex, delivered_pdf


def render_doi_link(value: object) -> str:
    doi = clean_text(value)
    if not doi:
        return ""
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix):].strip()
            break
    escaped_doi = latex_escape(doi)
    return (
        r"\href{https://doi.org/"
        + escaped_doi
        + r"}{\textcolor{DOIBlue}{"
        + escaped_doi
        + "}}"
    )


def format_date_range(record: dict[str, Any]) -> str:
    start = clean_text(record.get("start_year"))
    end_value = record.get("end_year")
    end = "至今" if end_value in (None, "", "present") else clean_text(end_value)
    if start and end and start != end:
        return f"{start}--{end}"
    return start or end


def _section(title: str, body: str) -> str:
    return f"\\CVSection{{{latex_escape(title)}}}\n{body}"


def render_history(title: str, records: list[dict[str, Any]]) -> str:
    if not records:
        return ""
    rows = []
    for record in records:
        date_range = latex_escape(format_date_range(record))
        organization = latex_escape(record.get("organization"))
        role = latex_escape(record.get("role"))
        detail = "，".join(value for value in (organization, role) if value)
        rows.append(f"\\CVEntry{{{date_range}}}{{{detail}}}")
    body = "\n".join(rows)
    return _section(title, body)


def _contact_line(contact: dict[str, Any]) -> str:
    parts: list[str] = []
    if contact.get("email"):
        parts.append("邮箱：" + latex_escape(contact["email"]))
    if contact.get("homepage"):
        url = clean_text(contact["homepage"])
        parts.append(r"主页：\href{" + latex_escape(url) + "}{" + latex_escape(url) + "}")
    if contact.get("orcid"):
        orcid = latex_escape(contact["orcid"])
        parts.append(r"ORCID：\href{https://orcid.org/" + orcid + "}{" + orcid + "}")
    return r"\quad ".join(parts)


def render_header(profile: dict[str, Any]) -> str:
    identity = profile.get("identity", {})
    contact = profile.get("contact", {})
    name_zh = clean_text(identity.get("name_zh"))
    name_original = clean_text(identity.get("name_original"))
    primary_name = latex_escape(name_zh or name_original)
    alternate = ""
    if name_zh and name_original and name_zh.casefold() != name_original.casefold():
        alternate = r"\quad{\large " + latex_escape(name_original) + "}"
    headline = "，".join(
        value
        for value in (
            latex_escape(identity.get("title")),
            latex_escape(identity.get("institution")),
        )
        if value
    )
    details = _contact_line(contact)
    text_block = (
        r"{\color{CVGreen}\bfseries\fontsize{22}{25}\selectfont "
        + primary_name
        + "}"
        + alternate
        + r"\\[0.28em]"
        + r"{\bfseries "
        + headline
        + r"}\\[0.28em]"
        + r"{\footnotesize\color{CVGray} "
        + details
        + "}"
    )

    photo = profile.get("photo")
    if isinstance(photo, dict) and clean_text(photo.get("local_path")):
        photo_path = clean_text(photo["local_path"]).replace("\\", "/")
        return (
            r"\begin{minipage}[c]{0.78\textwidth}"
            + text_block
            + r"\end{minipage}\hfill"
            + r"\begin{minipage}[c]{0.18\textwidth}\raggedleft"
            + r"\includegraphics[width=22mm,height=28mm,keepaspectratio]{\detokenize{"
            + photo_path
            + r"}}\end{minipage}"
        )
    return text_block


def render_research_interests(profile: dict[str, Any]) -> str:
    interests = [
        latex_escape(value) for value in profile.get("research_interests", []) if clean_text(value)
    ]
    body = "；".join(interests) if interests else "未列出经核验的研究方向。"
    return _section("研究方向", body)


def render_publications(publications: list[dict[str, Any]]) -> str:
    items: list[str] = []
    for publication in publications:
        if clean_text(publication.get("display_authors")):
            authors = latex_escape(publication["display_authors"])
        else:
            authors = ", ".join(
                latex_escape(name) for name in publication.get("authors", [])
            )
        title = latex_escape(publication.get("title"))
        venue = latex_escape(publication.get("venue"))
        year = clean_text(publication.get("publication_date"))[:4]
        doi = render_doi_link(publication.get("doi"))
        cited = int(publication.get("cited_by_count") or 0)
        query_date = latex_escape(publication.get("citation_query_date"))
        metadata = ", ".join(value for value in (venue, year) if value)
        doi_text = f"；DOI: {doi}" if doi else ""
        citation_text = f"；OpenAlex 引用 {cited} 次（查询于 {query_date}）"
        items.append(
            r"\item "
            + authors
            + r". \textit{"
            + title
            + "}. "
            + metadata
            + doi_text
            + citation_text
            + "."
        )
    if not items:
        body = r"{\color{CVGray}\small 未找到经核验的代表性论文。}"
    else:
        body = (
            r"\begin{enumerate}[leftmargin=1.7em,itemsep=0.13em,topsep=0.1em]"
            + "\n"
            + "\n".join(items)
            + "\n"
            + r"\end{enumerate}"
        )
    return _section("代表性论文", body)


def _iter_sources(profile: dict[str, Any]) -> Iterable[dict[str, Any]]:
    field_sources = profile.get("field_sources", {})
    if isinstance(field_sources, dict):
        for sources in field_sources.values():
            if isinstance(sources, list):
                for source in sources:
                    if isinstance(source, dict):
                        yield source
    photo = profile.get("photo")
    if isinstance(photo, dict):
        yield {
            "source_type": photo.get("source_type"),
            "url": photo.get("source_url"),
            "accessed": photo.get("accessed"),
        }


def source_types(profile: dict[str, Any], publications: list[dict[str, Any]]) -> list[str]:
    types = {
        clean_text(source.get("source_type"))
        for source in _iter_sources(profile)
        if clean_text(source.get("source_type"))
    }
    if any(publication.get("openalex_url") for publication in publications):
        types.add("openalex")
    if any(publication.get("crossref_url") for publication in publications):
        types.add("crossref")
    order = [
        "personal_homepage",
        "institutional_profile",
        "orcid",
        "openalex",
        "crossref",
    ]
    return [source_type for source_type in order if source_type in types]


def render_footer(profile: dict[str, Any], publications: list[dict[str, Any]]) -> str:
    labels = [SOURCE_LABELS[source_type] for source_type in source_types(profile, publications)]
    sources = "、".join(labels) if labels else "未记录"
    verified = latex_escape(profile.get("verification_date")) or "未记录"
    return (
        r"\vfill{\color{CVLine}\rule{\linewidth}{0.4pt}}\vspace{0.15em}"
        + "\n"
        + r"{\scriptsize\color{CVGray}资料来源："
        + latex_escape(sources)
        + r"\hfill 核验日期："
        + verified
        + "}"
    )


def render_cv(
    profile: dict[str, Any],
    publications: list[dict[str, Any]],
    template_path: Path,
) -> str:
    template = template_path.read_text(encoding="utf-8")
    left = "\n".join(
        (
            render_history("教育经历", profile.get("education", [])),
            render_history("工作经历", profile.get("employment", [])),
        )
    )
    right = "\n".join(
        (
            render_history("学术与机构兼职", profile.get("service", [])),
            render_history("重要荣誉与奖项", profile.get("major_honors", [])),
        )
    )
    replacements = {
        "@@HEADER@@": render_header(profile),
        "@@RESEARCH_INTERESTS@@": render_research_interests(profile),
        "@@LEFT_COLUMN@@": left,
        "@@RIGHT_COLUMN@@": right,
        "@@PUBLICATIONS@@": render_publications(publications),
        "@@FOOTER@@": render_footer(profile, publications),
    }
    rendered = template
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)
    unresolved = [token for token in replacements if token in rendered]
    if unresolved:
        raise ValueError(f"Unresolved template tokens: {', '.join(unresolved)}")
    return rendered


def pdf_page_count(path: Path) -> int:
    import pymupdf

    with pymupdf.open(path) as document:
        return document.page_count


def _write_sources(
    path: Path,
    profile: dict[str, Any],
    publications: list[dict[str, Any]],
) -> None:
    lines = ["# Sources", "", "## Field provenance", ""]
    field_sources = profile.get("field_sources", {})
    if isinstance(field_sources, dict):
        for field, sources in field_sources.items():
            if not isinstance(sources, list):
                continue
            for source in sources:
                if not isinstance(source, dict):
                    continue
                source_type = clean_text(source.get("source_type"))
                label = SOURCE_LABELS.get(source_type, source_type or "Other")
                url = clean_text(source.get("url"))
                accessed = clean_text(source.get("accessed"))
                lines.append(
                    f"- `{field}` — {label}: {url} (accessed {accessed})"
                )

    photo = profile.get("photo")
    if isinstance(photo, dict):
        lines.extend(
            [
                "",
                "## Official portrait",
                "",
                "- institutional profile: "
                + clean_text(photo.get("source_url"))
                + " (accessed "
                + clean_text(photo.get("accessed"))
                + ")",
            ]
        )

    lines.extend(["", "## Selected publications", ""])
    for index, publication in enumerate(publications, start=1):
        title = clean_text(publication.get("title"))
        openalex_url = clean_text(publication.get("openalex_url"))
        crossref_url = clean_text(publication.get("crossref_url"))
        query_date = clean_text(publication.get("citation_query_date"))
        cited = int(publication.get("cited_by_count") or 0)
        lines.append(f"- {index}. {title}")
        if openalex_url:
            lines.append(
                f"  - OpenAlex: {openalex_url} "
                f"({cited} citations; queried {query_date})"
            )
        if crossref_url:
            lines.append(f"  - Crossref: {crossref_url}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_verification_report(
    path: Path,
    profile: dict[str, Any],
    publications: list[dict[str, Any]],
    page_count: int | None = None,
) -> None:
    resolution = profile.get("identity_resolution", {})
    status = clean_text(resolution.get("status")) if isinstance(resolution, dict) else ""
    notes = clean_text(resolution.get("notes")) if isinstance(resolution, dict) else ""
    conflicts = resolution.get("conflicts", []) if isinstance(resolution, dict) else []
    if not isinstance(conflicts, list):
        conflicts = []
    query_dates = sorted(
        {
            clean_text(publication.get("citation_query_date"))
            for publication in publications
            if clean_text(publication.get("citation_query_date"))
        }
    )
    omitted = [
        field
        for field in ("email", "homepage", "orcid")
        if not clean_text(profile.get("contact", {}).get(field))
    ]
    if not profile.get("photo"):
        omitted.append("photo")
    lines = [
        "# Verification report",
        "",
        f"- Identity resolution: {status or 'not recorded'}",
        f"- Identity notes: {notes or 'none'}",
        f"- Verification date: {clean_text(profile.get('verification_date')) or 'not recorded'}",
        f"- Selected publications: {len(publications)}",
        f"- Citation-count query date(s): {', '.join(query_dates) or 'not recorded'}",
        f"- Page count: {page_count if page_count is not None else 'pending compilation'}",
        f"- Omitted optional fields: {', '.join(omitted) if omitted else 'none'}",
        "- Factual calibration: completed against approved field-level sources.",
        "- Professional Chinese editing: completed using discipline-appropriate terminology.",
        "- Post-edit verification: completed against the normalized JSON record.",
        "",
        "## Identity conflicts and decisions",
        "",
    ]
    if conflicts:
        lines.extend(f"- {clean_text(conflict)}" for conflict in conflicts)
    else:
        lines.append("- No unresolved identity conflict recorded.")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- OpenAlex citation counts are time-sensitive and apply only on the recorded query date.",
            "- Optional information without approved traceable evidence is omitted rather than inferred.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def compile_tex(tex_path: Path, log_path: Path) -> int:
    outputs: list[str] = []
    for run_number in (1, 2):
        result = subprocess.run(
            [
                "xelatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                tex_path.name,
            ],
            cwd=tex_path.parent,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        outputs.append(
            f"===== XeLaTeX run {run_number} =====\n{result.stdout}\n{result.stderr}"
        )
        if result.returncode != 0:
            log_path.write_text("\n".join(outputs), encoding="utf-8")
            return result.returncode
    log_path.write_text("\n".join(outputs), encoding="utf-8")
    return 0


def stage_portrait(
    profile_path: Path,
    output_dir: Path,
    profile: dict[str, Any],
) -> None:
    photo = profile.get("photo")
    if not isinstance(photo, dict) or not clean_text(photo.get("local_path")):
        return
    source = Path(clean_text(photo["local_path"]))
    if not source.is_absolute():
        source = profile_path.parent / source
    if not source.is_file():
        raise FileNotFoundError(f"Verified portrait not found: {source}")
    destination = output_dir / ("portrait" + source.suffix.lower())
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)
    photo["local_path"] = destination.name


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render and compile an exactly one-page Chinese academic CV."
    )
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--publications", required=True, type=Path)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--desktop-dir",
        type=Path,
        default=None,
        help="Desktop root for the final two-file delivery folder.",
    )
    args = parser.parse_args()

    profile = read_json(args.profile)
    publication_payload = read_json(args.publications)
    publications = publication_payload.get("publications", [])
    if not isinstance(publications, list):
        raise ValueError("The publications field must be a list")

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    render_profile = copy.deepcopy(profile)
    stage_portrait(args.profile, output_dir, render_profile)

    basename = delivery_basename(profile)
    tex_path = output_dir / f"{basename}.tex"
    tex_path.write_text(
        render_cv(render_profile, publications, args.template),
        encoding="utf-8",
    )
    _write_sources(output_dir / "sources.md", profile, publications)
    _write_verification_report(
        output_dir / "verification_report.md", profile, publications
    )
    log_path = output_dir / "compilation.log"
    return_code = compile_tex(tex_path, log_path)
    if return_code != 0:
        return return_code
    pdf_path = output_dir / f"{basename}.pdf"
    pages = pdf_page_count(pdf_path)
    if pages != 1:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"\nERROR: expected exactly one page, found {pages}.\n")
        return 2
    _write_verification_report(
        output_dir / "verification_report.md",
        profile,
        publications,
        page_count=pages,
    )
    desktop_dir = args.desktop_dir or default_desktop_dir()
    delivered_tex, delivered_pdf = publish_final_pair(
        profile, tex_path, pdf_path, desktop_dir
    )
    print(f"Delivered TeX: {delivered_tex}")
    print(f"Delivered PDF: {delivered_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
