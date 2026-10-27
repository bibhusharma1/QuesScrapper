from pathlib import Path

from ParsethePDF.pdf_read import extract_pdf_text
from ParsethePDF.renderPDF import render_pdf
from ParsethePDF.image_extract import extract_embedded_images
from ParsethePDF.manifest import save_manifest



def process_pdf(pdf_path, output_dir, dpi=250):
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)

    pages = extract_pdf_text(pdf_path)

    rendered_pages = render_pdf(
        pdf_path,
        output_dir / "pages",
        dpi=dpi,
    )

    images = extract_embedded_images(
        pdf_path,
        output_dir / "images",
    )

    manifest = {
        "source_pdf": pdf_path.name,
        "page_count": len(pages),
        "render_dpi": dpi,
        "pages": [],
        "embedded_images": images,
    }

    for page, rendered in zip(pages, rendered_pages):
        text_path = output_dir / "text" / (
            f"page_{page['page_number']:04d}.txt"
        )
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text(page["text"], encoding="utf-8")

        manifest["pages"].append({
            **{key: value for key, value in page.items() if key != "text"},
            "text_path": str(text_path),
            "native_text_characters": len(page["text"]),
            "needs_ocr_review": len(page["text"]) < 20,
            "page_image": rendered["image_path"],
            "render_width_px": rendered["width_px"],
            "render_height_px": rendered["height_px"],
        })

    save_manifest(manifest, output_dir / "manifest.json")

    return manifest