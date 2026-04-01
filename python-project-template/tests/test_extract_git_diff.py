import importlib.util
from pathlib import Path
import sys
import zipfile

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "extract_git_diff.py"
SPEC = importlib.util.spec_from_file_location("extract_git_diff", MODULE_PATH)
assert SPEC is not None
assert SPEC.loader is not None
EXTRACT_GIT_DIFF = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = EXTRACT_GIT_DIFF
SPEC.loader.exec_module(EXTRACT_GIT_DIFF)
archive_diff_dir = EXTRACT_GIT_DIFF.archive_diff_dir
prepare_output_dir = EXTRACT_GIT_DIFF.prepare_output_dir


def test_prepare_output_dir_removes_only_diff_report_and_zip(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    diff_dir = output_dir / "diff"
    diff_zip_path = output_dir / "diff.zip"
    report_path = output_dir / "report.md"
    keep_path = output_dir / "meta.md"
    nested_keep_path = output_dir / "review" / "notes.md"

    nested_keep_path.parent.mkdir(parents=True, exist_ok=True)
    diff_dir.mkdir(parents=True, exist_ok=True)

    report_path.write_text("old report", encoding="utf-8")
    diff_zip_path.write_text("old zip", encoding="utf-8")
    keep_path.write_text("keep", encoding="utf-8")
    nested_keep_path.write_text("keep nested", encoding="utf-8")
    (diff_dir / "obsolete.diff").write_text("diff", encoding="utf-8")

    prepare_output_dir(output_dir)

    assert output_dir.exists()
    assert not diff_dir.exists()
    assert not diff_zip_path.exists()
    assert not report_path.exists()
    assert keep_path.read_text(encoding="utf-8") == "keep"
    assert nested_keep_path.read_text(encoding="utf-8") == "keep nested"


def test_archive_diff_dir_creates_zip_and_removes_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    diff_dir = output_dir / "diff"
    nested_diff_path = diff_dir / "src" / "sample.py.diff"

    nested_diff_path.parent.mkdir(parents=True, exist_ok=True)
    nested_diff_path.write_text("sample diff", encoding="utf-8")

    archive_diff_dir(output_dir)

    diff_zip_path = output_dir / "diff.zip"
    assert diff_zip_path.exists()
    assert not diff_dir.exists()

    with zipfile.ZipFile(diff_zip_path) as archive:
        assert "diff/src/sample.py.diff" in archive.namelist()
