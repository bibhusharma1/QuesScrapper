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

For the full step-by-step guide, folder meanings, settings, Docker usage (how to run it in a container), and how the output looks, read **[DOCS.md](./DOCS.md)**.

Sample question papers are in `sampleData/ques_bank/` (from the [BIT Mesra exam portal](https://bitmesra.ac.in/Other-Department-Pages/content/1/258/446)).
