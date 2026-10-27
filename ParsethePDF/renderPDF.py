from pathlib import Path

import pymupdf


def render_pdf(pdf_path, output_dir, dpi=250):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rendered_pages = []

    with pymupdf.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            image_path = output_dir / f"page_{page_number:04d}.png"

            pixmap = page.get_pixmap(
                dpi=dpi,
                colorspace=pymupdf.csRGB,
                alpha=False,
                annots=True,
            )
            pixmap.save(image_path)

            rendered_pages.append({
                "page_number": page_number,
                "image_path": str(image_path),
                "width_px": pixmap.width,
                "height_px": pixmap.height,
            })

    return rendered_pages