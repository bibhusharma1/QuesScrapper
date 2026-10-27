# OCR layer (PaddleOCR PPStructureV3) — NOT wired into the pipeline yet.
# Pages flagged needs_ocr_review=True (sparse native text) are the
# candidates that would be routed through this module in a later phase.
# Requires a CUDA-enabled GPU (see README.md).

def run_ocr(image_paths):
    """Run PaddleOCR document parsing on rendered page images.

    Args:
        image_paths: Iterable of image paths (usually rendered pages).

    Returns:
        List of dicts:
            {
                "image_path": str path of the OCR'd image,
                "results": raw PaddleOCR prediction output,
            }
    """
    from paddleocr import PPStructureV3

    parser = PPStructureV3()
    results = []

    for image_path in image_paths:
        page_results = parser.predict(input=str(image_path))
        results.append({
            "image_path": str(image_path),
            "results": page_results,
        })

    return results
