# HTTP service layer so a UI (or any client) can send requests without a CLI.
#
# Equipment it provides:
#   GET  /health        — liveness probe for the UI / orchestrator
#   POST /parse/upload  — UI uploads PDF files (multipart), they are parsed
#                         and appended into the dataset; returns a summary
#   POST /parse         — parse from filesystem paths (mounted folders or
#                         exact PDF paths); body optional, falls back to
#                         the .env/config selection when omitted
#   GET  /records       — read the current dataset content (limit/offset)
#
# Run modes (Dockerfile entrypoint dispatch):
#   default (or "service")  -> uvicorn server on 0.0.0.0:$QUES_PORT (8000)
#   "cli"                   -> same as the batch CLI (ParsePipeLIne.pipeline)
#
# see config.py for .env variables (save path etc.); the parsing is the
# same code path both modes use (process_pdf + append_records).

import sys
import tempfile
import threading
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

import ParsePipeLIne.pipeline as batch
from ParsePipeLIne.processPDF import process_pdf
from ParsePipeLIne.quesandFig import append_records

app = FastAPI(
    title="QuesScrapper",
    description="Question-paper PDF parser: scrapes raw text + figures and "
    "appends per-page records into the dataset JSON.",
    version="0.1.0",
)

# Dataset appends must be one at a time even when requests come in parallel
# (append_records rewrites the whole file atomically per call).
_append_lock = threading.Lock()


def _dataset_path():
    """Read the save path at request time (filtered env/.env overrides)."""
    import config

    return Path(config.QUESTIONS_JSON_FILE)


def _process_and_append(pdf_path, extraction_dir):
    """Shared worker for both modes: parse one PDF, append its records.

    Returns (records, manifest, total_records).
    """
    records, manifest = process_pdf(pdf_path, extraction_dir)
    with _append_lock:
        total = append_records(records, _dataset_path())
    return records, manifest, total


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/parse/upload")
async def parse_uploads(files: list[UploadFile] = File(...)):
    """Receive PDF files from the UI, parse and append them.

    The uploaded PDFs and all extraction artifacts live in a request-local
    temp folder that is deleted afterwards; only the dataset JSON grows.
    """
    if not files:
        raise HTTPException(status_code=400, detail="no files sent")

    processed = []
    failed = []

    with tempfile.TemporaryDirectory(prefix="ques_upload_") as tmp:
        tmp = Path(tmp)
        for upload in files:
            filename = upload.filename or "unnamed.pdf"
            if not filename.lower().endswith(".pdf"):
                failed.append({"file": filename, "error": "not a .pdf file"})
                continue

            try:
                pdf_path = tmp / Path(filename).name
                pdf_path.write_bytes(await upload.read())
                _, manifest, _ = _process_and_append(
                    pdf_path,
                    tmp / "extraction" / pdf_path.stem,
                )
                processed.append({
                    "pdf_name": pdf_path.name,
                    "pages": manifest["page_count"],
                })
            except Exception as exc:
                failed.append({"file": filename, "error": str(exc)})

    if not processed and not failed:
        raise HTTPException(status_code=400, detail="nothing to parse")

    return {"processed": processed, "failed": failed}


class BatchRequest(BaseModel):
    # None means "use the .env/config values".
    dirs: list[str] | None = None
    pdfs: list[str] | None = None


@app.post("/parse")
def parse_batch(request: BatchRequest | None = None):
    """Parse PDFs by filesystem path (for mounted folders / known paths).

    Body is optional: {"dirs": [...], "pdfs": [...]}; omitted fields fall
    back to the .env/config selection (folder list or exact PDF list).
    """
    import config

    dirs = config.INPUT_DIRS if request is None or request.dirs is None else request.dirs
    pdfs = config.INPUT_PDFS if request is None or request.pdfs is None else request.pdfs

    pdf_files = batch.collect_pdf_files(dirs, pdfs)
    if not pdf_files:
        raise HTTPException(status_code=404, detail="no PDF files found for the given/committed input selection")

    processed = []
    failed = []

    with tempfile.TemporaryDirectory(prefix="ques_batch_") as tmp:
        tmp = Path(tmp)
        for pdf_path in pdf_files:
            try:
                _, manifest, _ = _process_and_append(
                    pdf_path,
                    tmp / pdf_path.stem,
                )
                processed.append({
                    "pdf_name": pdf_path.name,
                    "pages": manifest["page_count"],
                })
            except Exception as exc:
                failed.append({"file": pdf_path.name, "error": str(exc)})

    if not processed:
        raise HTTPException(status_code=500, detail={"failed": failed})

    return {"processed": processed, "failed": failed}


@app.get("/records")
def read_records(limit: int = 0, offset: int = 0):
    """Read the current dataset (the UI's main read endpoint).

    limit=0 returns everything. Records are one per PDF page when set.
    """
    import json

    dataset_path = _dataset_path()
    if not dataset_path.is_file():
        return {"total": 0, "records": []}

    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    window = data[offset:] if limit == 0 else data[offset : offset + limit]
    return {"total": len(data), "records": window}


def main():
    """Entrypoint dispatcher: "cli" runs the batch; everything else serve."""
    if len(sys.argv) > 1 and sys.argv[1] in ("cli", "batch"):
        batch.run()
        return

    import os

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("QUES_PORT", "8000")))


if __name__ == "__main__":
    main()
