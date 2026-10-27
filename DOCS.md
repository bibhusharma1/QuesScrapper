# QuesScrapper — Full Guide

Simple, step-by-step documentation. Read this top to bottom and you will know what the tool does, how to run it, and what it gives you.

---

## 1. What is this tool for?

You have exam **question papers as PDF files**. This tool:

1. Opens each PDF.
2. **Scrapes** every page: all the **raw text** and all the **figures** (pictures inside the PDF, and diagrams drawn with lines/boxes).
3. **Appends** the result into **one JSON file** named `questions_data.json`.

That's it. This is the only job it has right now:

- It does **NOT** sort text into individual questions yet.
- It does **NOT** do OCR on scanned pages yet (that comes in a later phase).
- Everything it collects is **raw** — plain text as-is and figure images as-is.

---

## 2. How does it work? (step by step)

For every PDF in the input folder, the pipeline does 5 steps:

| Step | What happens | Where it is saved |
|---|---|---|
| 1 | Reads the text of each page (the text that is already inside the PDF) | `text/page_0001.txt` + inside the JSON |
| 2 | Makes a normal photo of each page (a PNG, 250 DPI) | `pages/page_0001.png` |
| 3 | Pulls out every **picture** embedded in the page (an image stored inside the PDF) | `images/page_0001_image_1.jpeg` |
| 4 | Pulls out every **drawn figure** (line/box diagrams that are not pictures — the tool photographs just that area) | `images_vector/page_0001_drawing_1.png` |
| 5 | Writes **one line (record) per page** into the shared JSON file | `<save path>/questions_data.json` |

Steps 1–4 are per page and saved in a folder named after the PDF, so two PDFs never overwrite each other's files.

### What one record in the JSON looks like

```json
{
  "pdf_name": "AI363 INTRODUCTION TO MACHINE LEARNING_MID.pdf",
  "page_number": 1,
  "raw_text": "BIRLA INSTITUTE OF TECHNOLOGY, MESRA, RANCHI ...",
  "text_character_count": 1596,
  "figure_paths": ["...images/page_0001_image_1.jpeg", "...images_vector/page_0001_drawing_1.png"],
  "page_image": ".../pages/page_0001.png",
  "needs_ocr_review": false
}
```

- `raw_text`: the whole page text, exactly as scraped.
- `figure_paths`: the figure image files for this page (only listed here — not inside the JSON, they stay as image files next to it).
- `needs_ocr_review`: `true` when a page has almost no text (< 20 chars) — a hint that the page might be scanned and may need OCR later.

### Why JSON (and not CSV)?

The figures are image files and a page can have many of them. In JSON, a page = one record with a list of figure paths — clean and simple. In CSV you would have to squash that list into one cell. If CSV is ever needed, it can be exported from this JSON later.

### Re-running is safe

Records are keyed by (**pdf name + page number**). Run the tool again on the same PDFs:

- No duplicates. A re-run **replaces** the pages of that PDF.
- New PDFs just get **added** at the end.
- If the save file is ever unreadable/corrupt, a `.bak` backup is made and a fresh file starts.

---

## 3. How to use it (normal, on your computer)

You need Python 3.11+ and [uv](https://docs.astral.sh/uv/) installed.

**Step 1 — put your PDFs in the input folder.**
Default folder: `sampleData/ques_bank/`. Drop any number of PDFs there.

**Step 2 — install:**

```bash
uv sync
```

**Step 3 — run:**

```bash
uv run python -m ParsePipeLIne.pipeline
```

**Step 4 — check results:**
Open `sampleData/ques_bank/output/questions_data.json`. Done.

Important:
- Always run from the **project root folder**.
- Do NOT run `python ParsePipeLIne/pipeline.py` directly (it breaks imports — see `test.md`).

### Changing the paths

All paths live in `config.py`. Each one can also be set as an environment variable (env var wins):

| Config name | Env var | Default | Meaning |
|---|---|---|---|
| `INPUT_PDF_FOLDER` | `QUES_INPUT_PDF_FOLDER` | `sampleData/ques_bank` | where your PDFs are |
| `OUTPUT_DIR` | `QUES_OUTPUT_DIR` | `sampleData/ques_bank/output` | temp output (pages, images, text) |
| `QUESTIONS_JSON_FILE` | `QUES_QUESTIONS_JSON` | `.../output/questions_data.json` | **the save file — the one that matters** |

---

## 4. How to use it (Docker container)

The tool ships as a container. Inside the container:

- **Input:** mount your folder with PDFs at `/data/input`.
- **Save path:** mount a folder at `/data/save` — the **only thing you need to keep** (`questions_data.json`) is written there.
- **Everything else is temporary:** page images, figures, text files go to `/tmp/qa_extraction`. The container can destroy that folder at any time — it is disposable. **Do not try to keep those files; keep the JSON file.**

Build the image once:

```bash
docker build -t quesscrapper .
```

Run it for a batch of PDFs:

```bash
docker run --rm \
  -v /path/to/your/pdfs:/data/input \
  -v /path/to/where/you/want/the/json:/data/save \
  quesscrapper
```

What each line does:

- `--rm` — throw the container away after it finishes (temp outputs are thrown away with it, which is fine).
- Volume 1 — your PDFs go **in**.
- Volume 2 — your save folder. After the run it contains `questions_data.json` **and nothing else needs to survive**.

The container picks paths from these env defaults (already set in the Dockerfile, overridable with `docker run -e ...`): `QUES_INPUT_PDF_FOLDER=/data/input`, `QUES_QUESTIONS_JSON=/data/save/questions_data.json`, `QUES_OUTPUT_DIR=/tmp/qa_extraction`.

FAQ you may be thinking about:

- **"The images and text files are lost after each run — is that okay?"** Yes. They are generic/duplicate copies of what's already in the JSON record (the JSON lists the figure paths). Keep the JSON; re-run a PDF any time to regenerate the files.
- **"Many PDFs at once?"** Yes — put all of them in the input folder. One broken PDF gets skipped with a printed error; the rest still run.

---

## 5. Tests

```bash
uv run pytest test/ -v
```

The tests make their own tiny PDFs (with text, an image, and a drawn diagram) — they don't need any sample files. They check all 5 steps, the safe re-run behavior, and that one bad PDF doesn't stop the batch. Also runs automatically on GitHub via `.github/workflows/tests.yml`.

---

## 6. What is coming in later phases (not yet)

1. **OCR** — scanned pages (`needs_ocr_review: true`) will be read by [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR). It needs an NVIDIA GPU (CUDA). It is already prepared — install with `uv sync --extra ocr` — but not wired into the pipeline yet.
2. **Question splitting** — arranging raw pages into individual questions and their figures.
3. **Word export** — making the final document from the arranged questions.

---

## 7. Folder map (what every file is)

```
├── config.py                  # all paths (can override with env vars)
├── main.py                    # same as the pipeline command, e.g. `uv run python main.py`
├── Dockerfile                 # makes the container (see section 4)
├── ParsethePDF/               # the extraction library (each file = one job)
│   ├── pdf_read.py            #   step 1: read page text
│   ├── renderPDF.py           #   step 2: photo each page
│   ├── image_extract.py       #   step 3: pull out embedded images
│   ├── vector_figures.py      #   step 4: pull out drawn diagrams
│   ├── manifest.py            #   saves a per-PDF report (manifest.json)
│   └── ocr.py                 #   (later step: OCR — not connected yet)
├── ParsePipeLIne/             # the manager layer
│   ├── processPDF.py          #   runs steps 1–5 + manifest for ONE pdf
│   ├── quesandFig.py          #   builds records + appends into the JSON
│   └── pipeline.py            #   loops over ALL pdfs in the input folder
├── test/                      # the tests (see section 5)
│   ├── helpers.py             #   makes tiny test PDFs
│   ├── test_pdf_read.py, test_image_extract.py, test_vector_figures.py,
│   ├── test_quesandFig.py, test_pipeline.py
│   └── PDFingestion.py        #   old hand-written prototype (kept for history)
└── sampleData/ques_bank/      # sample question papers (your PDFs go here too)
```

The small working notes `ques.md` (PDF sources) and `test.md` (the run-command gotcha) are kept on purpose.
