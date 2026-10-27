# Batch entry point: parse EVERY PDF in config.INPUT_PDF_FOLDER, write
# each PDF's extraction into output/<pdf_stem>/, and append all page
# records into config.QUESTIONS_JSON_FILE.
#
# Run from the project root (NOT this file directly, see test.md):
#   uv run python -m ParsePipeLIne.pipeline
# or equivalently:
#   uv run python main.py

import sys
from pathlib import Path

from config import INPUT_PDF_FOLDER, OUTPUT_DIR, QUESTIONS_JSON_FILE

from ParsePipeLIne.processPDF import process_pdf
from ParsePipeLIne.quesandFig import append_records


def run():
    """Run the full multi-PDF scrape and append the dataset.

    Behaviour:
        - Recursively finds *.pdf in INPUT_PDF_FOLDER (de-duplicated by
          resolved absolute path).
        - Each PDF is isolated: one failing PDF prints an error and the
          batch continues with the rest.
        - Dataset file is upserted per (pdf_name, page_number), so repeated
          runs never duplicate records.

    Exits non-zero if the input folder is empty/missing or any PDF failed.
    """
    input_folder = Path(INPUT_PDF_FOLDER)

    if not input_folder.is_dir():
        print(f"Input folder not found: {input_folder}", file=sys.stderr)
        raise SystemExit(1)

    # rglob so PDFs in subfolders count too; set() dedupes overlaps.
    pdf_files = sorted(
        {pdf.resolve() for pdf in input_folder.rglob("*.pdf") if pdf.is_file()}
    )

    if not pdf_files:
        print(f"No PDF files found in: {input_folder}", file=sys.stderr)
        raise SystemExit(1)

    print(f"Found {len(pdf_files)} PDF file(s) in {input_folder}")

    output_dir = Path(OUTPUT_DIR)
    json_file = Path(QUESTIONS_JSON_FILE)

    succeeded = 0
    failed = 0
    total_records = 0

    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path.name}")
        try:
            records, manifest = process_pdf(
                pdf_path,
                # Per-PDF subfolder avoids page_NNNN.* name collisions.
                output_dir / pdf_path.stem,
            )
        except Exception as exc:
            failed += 1
            print(f"FAILED: {pdf_path.name} -> {exc}", file=sys.stderr)
            continue

        total_records = append_records(records, json_file)
        succeeded += 1
        print(
            f"Done: {manifest['page_count']} page(s) -> "
            f"{output_dir / pdf_path.stem}"
        )

    print("\nSummary:")
    print(f"  PDFs processed: {succeeded}")
    print(f"  PDFs failed:    {failed}")
    print(f"  Records in {json_file}: {total_records}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
