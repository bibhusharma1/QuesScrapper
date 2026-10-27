# Embedded raster image (figure/diagram) extraction layer.
# Only images physically embedded in the PDF are collected here;
# vector-drawn diagrams are handled by ParsethePDF/vector_figures.py.

from pathlib import Path

import pymupdf


def extract_embedded_images(pdf_path, output_dir):
    """Extract all embedded raster images from a PDF, per page.

    Args:
        pdf_path: Path to the PDF file.
        output_dir: Folder in which extracted images are written.

    Returns:
        List of records for every successfully extracted image:
            {
                "page_number": 1-based page the image appears on,
                "image_path": str path of the saved image file,
                "width": image width in pixels,
                "height": image height in pixels,
            }
        An image the PDF stores but which cannot be extracted is skipped
        with a printed warning rather than aborting the whole run.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted_images = []

    with pymupdf.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            # full=True also exposes image transformations/channels we
            # only need the xref (info[0]) from.
            for image_number, info in enumerate(
                page.get_images(full=True), start=1
            ):
                xref = info[0]

                try:
                    image = pdf.extract_image(xref)
                    if not image:
                        continue

                    image_path = output_dir / (
                        f"page_{page_number:04d}_"
                        f"image_{image_number}.{image['ext']}"
                    )
                    image_path.write_bytes(image["image"])

                    extracted_images.append({
                        "page_number": page_number,
                        "image_path": str(image_path),
                        "width": image["width"],
                        "height": image["height"],
                    })
                except Exception as exc:
                    # One broken image should not abort the whole PDF run.
                    print(f"Could not extract image {xref}: {exc}")

    return extracted_images
