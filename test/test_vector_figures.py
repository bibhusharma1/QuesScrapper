from pathlib import Path

from ParsethePDF.vector_figures import extract_vector_figures

from helpers import make_pdf


def test_extract_vector_figures_picks_up_drawing(tmp_path):
    pdf = make_pdf(
        tmp_path / "sample.pdf",
        ["text page one", "text page two"],
        with_drawing_on_page=0,
    )

    figures = extract_vector_figures(pdf, tmp_path / "images_vector")

    assert len(figures) == 1
    assert figures[0]["page_number"] == 1
    assert figures[0]["width"] > 0
    assert figures[0]["height"] > 0

    figure_path = Path(figures[0]["image_path"])
    assert figure_path.is_file()
    assert figure_path.suffix == ".png"


def test_extract_vector_figures_skips_text_only_pdf(tmp_path):
    pdf = make_pdf(tmp_path / "sample.pdf", ["plain text"])

    figures = extract_vector_figures(pdf, tmp_path / "images_vector")

    assert figures == []
