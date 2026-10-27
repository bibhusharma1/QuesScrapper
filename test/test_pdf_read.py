from ParsethePDF.pdf_read import extract_pdf_text

from helpers import make_pdf


def test_extract_pdf_text_roundtrip(tmp_path):
    pdf = make_pdf(
        tmp_path / "sample.pdf",
        ["first page text", "second page text"],
    )

    pages = extract_pdf_text(pdf)

    assert len(pages) == 2
    assert pages[0]["page_number"] == 1
    assert pages[1]["page_number"] == 2
    assert "first page text" in pages[0]["text"]
    assert "second page text" in pages[1]["text"]
    assert pages[0]["width_pt"] > 0
    assert pages[0]["height_pt"] > 0


def test_extract_pdf_text_missing_file(tmp_path):
    try:
        extract_pdf_text(tmp_path / "missing.pdf")
    except Exception as exc:
        assert type(exc).__name__ in ("FileNotFoundError", "ValueError", "RuntimeError")
    else:
        raise AssertionError("expected extraction to fail for missing file")
