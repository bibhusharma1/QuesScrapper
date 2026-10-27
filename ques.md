# ques.md — working notes

Kept on purpose: where the sample PDFs came from. Full docs: `README.md`, `DOCS.md`.

## PDF sources

Portal: <https://bitmesra.ac.in/Other-Department-Pages/content/1/258/446>

- <https://bitmesra.ac.in/UploadedDocuments/adminexam/files/MO2025%20QP/AI363%20INTRODUCTION%20TO%20MACHINE%20LEARNING_MID.pdf>
- <https://bitmesra.ac.in/UploadedDocuments/adminexam/files/MO2025%20QP/CS231%20DATA%20STRUCTURES_MID.pdf>
- <https://bitmesra.ac.in/UploadedDocuments/adminexam/files/MO2025%20QP/AI24201%20MATHEMATICS%20FOR%20AIML_MID.pdf>
- <https://bitmesra.ac.in/UploadedDocuments/adminexam/files/MO2025%20QP/CS237%20DATABASE%20MANAGEMENT%20SYSTEM_MID.pdf>

Same portal students upload from — so the tool later works for real uploads too. Word/PPT ignored for now.

## Output plan

- Keep: `questions_data.json` (one record per page, `raw_text` + `figure_paths`).
- Regenerate anytime by re-running the pipeline: text in `output/<pdf_stem>/text/`, pictures in `images/`, drawn figures in `images_vector/`, report in `manifest.json`.
- Later the OCR phase uses the page images to check it can parse questions from plain images.
