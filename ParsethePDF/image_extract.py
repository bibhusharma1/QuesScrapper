from pathlib import Path

import pymupdf


def extract_embedded_images(pdf_path, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted_images = []

    with pymupdf.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
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
                    print(f"Could not extract image {xref}: {exc}")

    return extracted_images