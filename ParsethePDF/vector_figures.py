# Vector-drawn figure extraction layer.
# Exam papers often draw diagrams (lines, boxes, curves) as PDF vector
# drawings instead of embedding raster images — those would be missed by
# ParsethePDF/image_extract.py. This module renders the page region
# covered by such drawings into a PNG so figures are not lost.

from pathlib import Path

import pymupdf

# If a page's drawings cover more than this fraction of the page area,
# they are treated as a decorative full-page border/frame rather than a
# meaningful figure, and the page is skipped.
MAX_PAGE_COVERAGE_RATIO = 0.9


def extract_vector_figures(pdf_path, output_dir):
    """Render vector-drawn diagram regions to PNG images.

    Args:
        pdf_path: Path to the PDF file.
        output_dir: Folder in which the figure PNGs are written.

    Returns:
        List of records for pages containing a usable vector figure:
            {
                "page_number": 1-based page the drawing appears on,
                "image_path": str path of the saved PNG,
                "width": rendered figure width in pixels,
                "height": rendered figure height in pixels,
            }
        Currently one PNG is clipped per page (the union bounding box of
        all its drawings); finer per-diagram clustering can be added later
        if pages mix unrelated diagrams.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    vector_figures = []

    with pymupdf.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            # No vector content on this page.
            drawings = page.get_drawings()
            if not drawings:
                continue

            # Union bounding box of every drawing on the page.
            bounding_rect = pymupdf.Rect()
            for drawing in drawings:
                bounding_rect |= drawing["rect"]

            if bounding_rect.is_empty:
                continue

            # Clip to the printable page (2pt margin keeps rounding
            # artifacts of the union math from dropping the figure).
            page_rect = page.rect + (-2, -2, 2, 2)
            union = bounding_rect & page_rect
            if union.is_empty:
                continue

            # Full-page rectangles are borders/frames, not figures.
            if union.get_area() >= MAX_PAGE_COVERAGE_RATIO * page.rect.get_area():
                continue

            pixmap = page.get_pixmap(
                dpi=250,
                clip=bounding_rect,
                colorspace=pymupdf.csRGB,
                alpha=False,
            )

            image_path = output_dir / f"page_{page_number:04d}_drawing_1.png"
            pixmap.save(image_path)

            vector_figures.append({
                "page_number": page_number,
                "image_path": str(image_path),
                "width": pixmap.width,
                "height": pixmap.height,
            })

    return vector_figures
