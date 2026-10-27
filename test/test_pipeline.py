import json
from pathlib import Path

import pytest

import ParsePipeLIne.pipeline as pipeline

from helpers import make_pdf


@pytest.fixture()
def batch_env(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    monkeypatch.setattr(pipeline, "INPUT_PDF_FOLDER", str(input_dir))
    monkeypatch.setattr(pipeline, "OUTPUT_DIR", str(tmp_path / "out"))
    monkeypatch.setattr(
        pipeline, "QUESTIONS_JSON_FILE", str(tmp_path / "questions_data.json")
    )

    return input_dir, tmp_path / "out", tmp_path / "questions_data.json"


def test_processes_all_pdfs_without_collisions(batch_env):
    input_dir, output_dir, json_file = batch_env
    make_pdf(input_dir / "bookA.pdf", ["alpha one", "alpha two"], with_image_on_page=0)
    make_pdf(input_dir / "bookB.pdf", ["beta one", "beta two"], with_drawing_on_page=1)

    pipeline.run()

    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert len(data) == 4

    pdf_names = {record["pdf_name"] for record in data}
    assert pdf_names == {"bookA.pdf", "bookB.pdf"}

    for record in data:
        stem = Path(record["pdf_name"]).stem
        for figure_path in record["figure_paths"]:
            assert figure_path.startswith(str(output_dir / stem))
        assert record["page_image"].startswith(str(output_dir / stem))
    assert (output_dir / "bookA" / "manifest.json").is_file()
    assert (output_dir / "bookB" / "manifest.json").is_file()


def test_rerun_replaces_records_not_duplicates(batch_env):
    input_dir, output_dir, json_file = batch_env
    make_pdf(input_dir / "bookA.pdf", ["alpha one", "alpha two"])

    pipeline.run()
    pipeline.run()

    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert len(data) == 2


def test_broken_pdf_does_not_abort_batch(batch_env):
    input_dir, output_dir, json_file = batch_env
    make_pdf(input_dir / "bookA.pdf", ["alpha one"])
    (input_dir / "broken.pdf").write_bytes(b"%PDF-1.4 not a real pdf")

    with pytest.raises(SystemExit):
        pipeline.run()

    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert [record["pdf_name"] for record in data] == ["bookA.pdf"]


def test_empty_input_folder_exits(batch_env):
    with pytest.raises(SystemExit) as excinfo:
        pipeline.run()
    assert excinfo.value.code == 1
