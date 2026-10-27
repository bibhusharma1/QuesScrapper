from pathlib import Path

from ParsethePDF.image_extract import extract_embedded_images

from helpers import make_pdf


def test_extract_embedded_images_finds_inserted_image(tmp_path):
    pdf = make_pdf(
        tmp_path / "sample.pdf",
        ["page one", "page two"],
        with_image_on_page=0,
    )
    output_dir = tmp_path / "images"

    images = extract_embedded_images(pdf, output_dir)

    assert len(images) == 1
    assert images[0]["page_number"] == 1
    assert images[0]["width"] == 8
    assert images[0]["height"] == 8
    assert Path(images[0]["image_path"]).is_file()


def test_extract_embedded_images_empty_pdf(tmp_path):
    pdf = make_pdf(tmp_path / "sample.pdf", ["just text"])

    images = extract_embedded_images(pdf, tmp_path / "images")

    assert images == []
