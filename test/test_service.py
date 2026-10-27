import json

import pytest
from fastapi.testclient import TestClient

import ParsePipeLIne.service as service

from helpers import make_pdf


@pytest.fixture()
def client(tmp_path, monkeypatch):
    save_dir = tmp_path / "save"
    save_dir.mkdir()
    monkeypatch.setattr("config.QUESTIONS_JSON_FILE", str(save_dir / "questions_data.json"))
    monkeypatch.setattr("config.OUTPUT_DIR", str(tmp_path / "out"))
    monkeypatch.setattr("config.INPUT_DIRS", [str(tmp_path / "input")])
    monkeypatch.setattr("config.INPUT_PDFS", [])

    return TestClient(service.app), save_dir / "questions_data.json"


def test_health(client):
    http, _ = client
    response = http.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_parse_upload_appends_records(client, tmp_path):
    http, json_file = client
    pdf_path = make_pdf(tmp_path / "test_pdf.pdf", ["question one about python"])
    pdf_bytes = pdf_path.read_bytes()

    response = http.post(
        "/parse/upload",
        files=[("files", ("test_pdf.pdf", pdf_bytes, "application/pdf"))],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["processed"] == [{"pdf_name": "test_pdf.pdf", "pages": 1}]
    assert body["failed"] == []

    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert [record["pdf_name"] for record in data] == ["test_pdf.pdf"]
    assert "python" in data[0]["raw_text"]


def test_parse_upload_takes_a_list_of_files(client, tmp_path):
    """The UI sends [file1, file2, file3] in one request — all get parsed."""
    http, json_file = client
    pdf_one = make_pdf(tmp_path / "one.pdf", ["alpha"])
    pdf_two = make_pdf(tmp_path / "two.pdf", ["beta"])
    pdf_three = make_pdf(tmp_path / "three.pdf", ["gamma"])
    pdf_one_bytes = pdf_one.read_bytes()

    response = http.post(
        "/parse/upload",
        files=[
            ("files", ("one.pdf", pdf_one_bytes, "application/pdf")),
            ("files", ("two.pdf", pdf_two.read_bytes(), "application/pdf")),
            ("files", ("three.pdf", pdf_three.read_bytes(), "application/pdf")),
            # Sending the same file twice is fine: dedupe replaces its records.
            ("files", ("one.pdf", pdf_one_bytes, "application/pdf")),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["failed"] == []
    assert [p["pdf_name"] for p in body["processed"]] == ["one.pdf", "two.pdf", "three.pdf", "one.pdf"]

    # Dataset holds each file once (upsert by pdf_name + page_number).
    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert {record["pdf_name"] for record in data} == {"one.pdf", "two.pdf", "three.pdf"}


def test_parse_upload_skips_non_pdf_files(client, tmp_path):
    http, json_file = client
    pdf_path = make_pdf(tmp_path / "test_pdf.pdf", ["question one"])
    pdf_bytes = pdf_path.read_bytes()
    text_payload = b"just some text, not a pdf"

    response = http.post(
        "/parse/upload",
        files=[
            ("files", ("test_pdf.pdf", pdf_bytes, "application/pdf")),
            ("files", ("notes.txt", text_payload, "text/plain")),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["processed"] == [{"pdf_name": "test_pdf.pdf", "pages": 1}]
    assert body["failed"] == [{"file": "notes.txt", "error": "not a .pdf file"}]


def test_parse_batch_reads_configured_and_body_selections(client, tmp_path):
    http, json_file = client
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    make_pdf(input_dir / "bookA.pdf", ["alpha page"])
    make_pdf(input_dir / "bookB.pdf", ["beta page"])

    # No body: falls back to config selection (INPUT_DIRS set in fixture).
    response = http.post("/parse")
    assert response.status_code == 200
    assert {p["pdf_name"] for p in response.json()["processed"]} == {"bookA.pdf", "bookB.pdf"}

    # Body with explicit pdfs must take precedence (empty save dir first).
    json_file.write_text("[]", encoding="utf-8")
    response = http.post("/parse", json={"pdfs": [str(input_dir / "bookB.pdf")]})
    assert response.status_code == 200
    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert [record["pdf_name"] for record in data] == ["bookB.pdf"]


def test_records_endpoint_reads_dataset(client, tmp_path):
    http, json_file = client
    pdf_path = make_pdf(tmp_path / "two_pages.pdf", ["page one text", "page two text"])

    http.post("/parse/upload", files=[("files", ("two_pages.pdf", pdf_path.read_bytes(), "application/pdf"))])

    response = http.get("/records")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [record["page_number"] for record in body["records"]] == [1, 2]

    limited = http.get("/records?limit=1&offset=1").json()
    assert limited["total"] == 2
    assert [record["page_number"] for record in limited["records"]] == [2]


def test_records_empty_dataset(client):
    http, _ = client
    response = http.get("/records")
    assert response.json() == {"total": 0, "records": []}
