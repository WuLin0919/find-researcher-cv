from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("render_cv", SCRIPTS / "render_cv.py")
render_cv = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(render_cv)


def profile() -> dict[str, object]:
    return {
        "identity": {
            "name_original": "Inkyu Park",
            "name_zh": "朴仁圭",
            "institution": "KAIST / Mechanical Engineering",
        }
    }


class DesktopDeliveryTests(unittest.TestCase):
    def test_delivery_basename_uses_original_name_and_sanitizes_institution(self) -> None:
        self.assertEqual(
            render_cv.delivery_basename(profile()),
            "Inkyu Park_KAIST - Mechanical Engineering",
        )

    def test_publish_final_pair_creates_exactly_two_renamed_files(self) -> None:
        with TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            work = tmp_path / "work"
            desktop = tmp_path / "Desktop"
            work.mkdir()
            tex = work / "source.tex"
            pdf = work / "source.pdf"
            tex.write_text("tex", encoding="utf-8")
            pdf.write_bytes(b"pdf")

            delivered_tex, delivered_pdf = render_cv.publish_final_pair(
                profile(), tex, pdf, desktop
            )

            target = desktop / "Inkyu Park_KAIST - Mechanical Engineering"
            self.assertEqual(
                delivered_tex,
                target / "Inkyu Park_KAIST - Mechanical Engineering.tex",
            )
            self.assertEqual(
                delivered_pdf,
                target / "Inkyu Park_KAIST - Mechanical Engineering.pdf",
            )
            self.assertEqual(
                {path.name for path in target.iterdir()},
                {
                    "Inkyu Park_KAIST - Mechanical Engineering.tex",
                    "Inkyu Park_KAIST - Mechanical Engineering.pdf",
                },
            )

    def test_publish_refuses_to_delete_unexpected_desktop_file(self) -> None:
        with TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            work = tmp_path / "work"
            desktop = tmp_path / "Desktop"
            target = desktop / "Inkyu Park_KAIST - Mechanical Engineering"
            work.mkdir()
            target.mkdir(parents=True)
            (target / "notes.txt").write_text("keep", encoding="utf-8")
            tex = work / "source.tex"
            pdf = work / "source.pdf"
            tex.write_text("tex", encoding="utf-8")
            pdf.write_bytes(b"pdf")

            with self.assertRaisesRegex(FileExistsError, "unexpected files"):
                render_cv.publish_final_pair(profile(), tex, pdf, desktop)

            self.assertEqual(
                (target / "notes.txt").read_text(encoding="utf-8"), "keep"
            )

    def test_publish_refuses_expected_name_when_it_is_a_directory(self) -> None:
        with TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            work = tmp_path / "work"
            desktop = tmp_path / "Desktop"
            target = desktop / "Inkyu Park_KAIST - Mechanical Engineering"
            work.mkdir()
            target.mkdir(parents=True)
            expected_tex = target / "Inkyu Park_KAIST - Mechanical Engineering.tex"
            expected_tex.mkdir()
            tex = work / "source.tex"
            pdf = work / "source.pdf"
            tex.write_text("tex", encoding="utf-8")
            pdf.write_bytes(b"pdf")

            with self.assertRaisesRegex(FileExistsError, "not files"):
                render_cv.publish_final_pair(profile(), tex, pdf, desktop)


if __name__ == "__main__":
    unittest.main()
