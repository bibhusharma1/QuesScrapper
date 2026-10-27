import pymupdf


def extract_pdf_text(pdf_path):
    pages = []

    with pymupdf.open(pdf_path) as pdf:
        if pdf.is_encrypted:
            raise ValueError("PDF is encrypted.")

        for page_number, page in enumerate(pdf, start=1):
            pages.append({
                "page_number": page_number,
                "width_pt": page.rect.width,
                "height_pt": page.rect.height,
                "text": page.get_text("text", sort=True).strip(),
            })

    return pages