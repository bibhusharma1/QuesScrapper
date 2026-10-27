# Native text extraction layer of the PDF library.

import pymupdf


def extract_pdf_text(pdf_path):
    """Extract native text from every page of a PDF.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        List of dicts, one per page (1-indexed):
            {
                "page_number": 1-based page index,
                "width_pt": page width in PDF points,
                "height_pt": page height in PDF points,
                "text": full page text, reading order sorted and stripped,
            }

    Raises:
        ValueError: If the PDF is encrypted.
    """
    pages = []

    with pymupdf.open(pdf_path) as pdf:
        # Encrypted PDFs cannot be read without a password — fail fast.
        if pdf.is_encrypted:
            raise ValueError("PDF is encrypted.")

        for page_number, page in enumerate(pdf, start=1):
            pages.append({
                "page_number": page_number,
                "width_pt": page.rect.width,
                "height_pt": page.rect.height,
                # sort=True orders text blocks as they visually appear,
                # avoiding jumbled output from table-style layouts.
                "text": page.get_text("text", sort=True).strip(),
            })

    return pages
