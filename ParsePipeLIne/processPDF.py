# Per-PDF processing orchestrator.
# One call = full extraction of a single PDF:
#   native text -> rendered pages -> embedded images -> vector figures
# and returns flat page records + a manifest.

from pathlib import Path

from ParsethePDF.pdf_read import extract_pdf_text
from ParsethePDF.renderPDF import render_pdf
from ParsethePDF.image_extract import extract_embedded_images
from ParsethePDF.vector_figures import extract_vector_figures
from ParsethePDF.manifest import save_manifest

from ParsePipeLIne.quesandFig import build_page_records


def process_pdf(pdf_path, output_dir, dpi=250):
    """Extract everything from one PDF into its own output folder.

    Args:
        pdf_path: Path to the PDF file.
        output_dir: Folder for this PDF's pages/, images/, images_vector/,
            text/ and manifest.json. Use a distinct folder per PDF to
            avoid filename collisions (pipeline.py passes <stem>/).
        dpi: Rendering resolution for page images and figure clips.

    Returns:
        Tuple (records, manifest) — see ParsePipeLIne.quesandFig
        .build_page_records for the exact shapes.

    Raises:
        FileNotFoundError: If the PDF does not exist.
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)

    # 1. Native text layer.
    pages = extract_pdf_text(pdf_path)

    # 2. Full-page rasters (later OCR fallback + visual reference).
    rendered_pages = render_pdf(
        pdf_path,
        output_dir / "pages",
        dpi=dpi,
    )

    # 3. Embedded raster figures (diagrams stored as images).
    images = extract_embedded_images(
        pdf_path,
        output_dir / "images",
    )

    # 4. Vector-drawn figures (diagrams stored as PDF drawings).
    vector_figures = extract_vector_figures(
        pdf_path,
        output_dir / "images_vector",
    )

    # 5. Merge everything into flat records + manifest; save the manifest.
    records, manifest = build_page_records(
        pdf_path,
        pages,
        rendered_pages,
        images,
        vector_figures,
        output_dir,
        dpi=dpi,
    )

    save_manifest(manifest, output_dir / "manifest.json")

    return records, manifest
