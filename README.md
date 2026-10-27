# QuesScrapper

This tool reads question-paper PDFs and saves each page's **text** and **pictures (figures)** into one big JSON file.

- Give it a folder of PDFs. It reads every page.
- It saves the raw text and extracts the figures (both picture-type and drawn-line-type diagrams).
- It **appends** everything into one JSON dataset file: `questions_data.json`.
- Run it again on the same PDFs? Nothing gets duplicated — the data is just updated.
- Today it does **only parsing**. It does not yet split questions or use OCR.

Quick start:

```bash
uv sync
uv run python -m ParsePipeLIne.pipeline
```

## How to use it

You need Python 3.11+ and [uv](https://docs.astral.sh/uv/).

**On your computer:**

1. Copy `.env.example` to `.env` and edit it: which **PDF folder(s) to read** (`QUES_INPUT_DIRS`), optional **specific PDFs** (`QUES_INPUT_PDFS`), and **which JSON file to save into** (`QUES_QUESTIONS_JSON`). All paths are relative.
2. Drop your PDFs into the configured folder (default: `sampleData/ques_bank/`).
3. Install once: `uv sync`
4. Run: `uv run python -m ParsePipeLIne.pipeline`
5. Open `sampleData/ques_bank/output/questions_data.json` — that's your data.

**As a Docker container — one-shot batch (CLI):**

1. Build once: `docker build -t quesscrapper .` (or `docker compose build`)
2. Put PDFs in a folder, then run:

```bash
docker run --rm \
  -v /path/to/your/pdfs:/data/input:ro \
  -v /path/to/save:/data/save \
  quesscrapper cli
```

3. Find `questions_data.json` in your save folder. That JSON file is the **only** thing the container keeps — page images, figures and text are temporary and don't need to survive the run.

**As a Docker microservice (HTTP — for a UI to send requests to):**

```bash
docker run -d -p 8000:8000 \
  -v /path/to/save:/data/save \
  --name quesscrapper quesscrapper
```

No CLI needed by the UI — the container serves a small FastAPI HTTP API on port 8000:

- `GET /health` — is the service up
- `POST /parse/upload` — UI sends PDF files; they are parsed and appended
- `POST /parse` — parse from mounted paths (optional body; defaults from config)
- `GET /records` — UI reads the parsed data back
- auto-generated try-it docs at `http://localhost:8000/docs`

Full details + a mermaid sequence diagram in [DOCS.md](./DOCS.md#5-how-to-use-it-http-service--for-the-ui).

**What the UI sends, what happens:**

- **A list of files** `[file1, file2, file3]` → send them all in **one** `POST /parse/upload` request (the field is repeatable). Every file is parsed and appended in that single call, and the response tells you per file what happened:

```json
{"processed": [{"pdf_name": "file1.pdf", "pages": 2},
               {"pdf_name": "file2.pdf", "pages": 1},
               {"pdf_name": "file3.pdf", "pages": 4}],
 "failed":   [{"file": "not_a_pdf.txt", "error": "not a .pdf file"}]}
```

Send the same file twice (or again later) — nothing is duplicated; its records are replaced. Non-PDF entries are reported under `failed`, the good files still get processed.

- **A list of folders** → send them in a `POST /parse` request (`{"dirs": ["folder/one", "folder/two"]}` — comma-separated in `.env` for the default). The service scans each folder for PDFs and appends everything it finds. Supplying `"pdfs": [...]` instead reads *only* those exact files.
- **Anything else** stays the same: the dataset JSON keeps growing at `QUES_QUESTIONS_JSON` (default `/data/save/questions_data.json` in the container).

Settings (which folders/PDFs to read and where to save the JSON) live in the **`.env`** file — copy `.env.example` to `.env` and edit. In the container, the mount points `/data/input` → `/data/save` already cover this; a `.env` passed via compose only overrides them. See the variable table in [DOCS.md](./DOCS.md#3-how-to-use-it-normal-on-your-computer).

To understand how the tool works inside (endpoints, data flow), DOCS.md has a [mermaid diagram of the whole flow](./DOCS.md#the-whole-flow-as-a-picture-mermaid) — from `.env` config through the extractors down to the appended JSON.

## GPU (CUDA)?

**Not needed for now.** Everything the tool does today — PDF text, page photos, figure extraction — runs on the CPU with the `pymupdf` library. No NVIDIA card, no CUDA.

- **Non-CUDA users:** you lose nothing right now — the full current pipeline works CPU-only, and the Docker image is built this way too.
- **When CUDA DOES become required:** in the later **OCR phase** (scanned pages, `needs_ocr_review: true`), the plan uses [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR), which needs an NVIDIA GPU with CUDA. That dependency is kept optional (install with `uv sync --extra ocr`) and is not wired into the pipeline yet.
- **No-GPU OCR alternatives (later decision):** run PaddleOCR in CPU mode (much slower), use a cloud OCR service, or split OCR into a separate service on GPU hardware. To be decided when the OCR phase starts.

For the full step-by-step guide, folder meanings, settings, Docker usage details, and how the output looks, read **[DOCS.md](./DOCS.md)**.

Sample question papers are in `sampleData/ques_bank/` (from the [BIT Mesra exam portal](https://bitmesra.ac.in/Other-Department-Pages/content/1/258/446)).
