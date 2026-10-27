def run_ocr(image_paths):
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