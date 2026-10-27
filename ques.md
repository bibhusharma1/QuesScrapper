# ques.md — working notes (PDF sources & plan)

These are working notes kept on purpose: where the sample question papers came from and what the original plan was. For the up-to-date tool documentation, see `README.md` and `DOCS.md`.

## Where the source PDFs came from

Main portal page: <https://bitmesra.ac.in/Other-Department-Pages/content/1/258/446>

Sample mid-semester question papers (2025 session):

- <https://bitmesra.ac.in/UploadedDocuments/adminexam/files/MO2025%20QP/AI363%20INTRODUCTION%20TO%20MACHINE%20LEARNING_MID.pdf>
- <https://bitmesra.ac.in/UploadedDocuments/adminexam/files/MO2025%20QP/CS231%20DATA%20STRUCTURES_MID.pdf>
- <https://bitmesra.ac.in/UploadedDocuments/adminexam/files/MO2025%20QP/AI24201%20MATHEMATICS%20FOR%20AIML_MID.pdf>
- <https://bitmesra.ac.in/UploadedDocuments/adminexam/files/MO2025%20QP/CS237%20DATABASE%20MANAGEMENT%20SYSTEM_MID.pdf>

Original idea behind these samples:

1. The PDFs above were downloaded from the same portal students would upload from.
2. We converted PDFs to page images as a test case.
3. Those page images are used to check the OCR step later — does it parse questions from plain images?
4. In short: a full simulation of "someone uploads a PDF or image — can our system extract the data or not?" (Word, PPT and other formats are deliberately ignored for now.)

## Output plan notes

- The important output (the thing to keep) is the consolidated dataset: `sampleData/ques_bank/output/questions_data.json` — one record per page with `raw_text` + `figure_paths`.
- Figures ("scraped images") = extracted diagrams: embedded raster ones under `output/<pdf_stem>/images/` and vector-drawn ones under `output/<pdf_stem>/images_vector/`.
- Per-page raw text: `output/<pdf_stem>/text/`.
- Everything under `output/` is regenerable by re-running the pipeline; only the dataset file matters.
- The exact record shape is documented in `DOCS.md` (section "What one record in the JSON looks like") and the per-PDF report file is `output/<pdf_stem>/manifest.json`.
