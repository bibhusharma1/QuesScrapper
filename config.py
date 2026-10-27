# Central configuration for the question-bank scraping pipeline.
# All folder/file paths used by the pipeline live here.
#
# Every path can be overridden with an environment variable — this is how
# a container receives its settings (see Dockerfile and DOCS.md):
#   QUES_INPUT_PDF_FOLDER  -> INPUT_PDF_FOLDER
#   QUES_OUTPUT_DIR        -> OUTPUT_DIR
#   QUES_QUESTIONS_JSON    -> QUESTIONS_JSON_FILE

import os

# Folder scanned recursively for *.pdf question papers to parse.
INPUT_PDF_FOLDER = os.environ.get("QUES_INPUT_PDF_FOLDER", "sampleData/ques_bank")

# Root folder where per-PDF extraction results are written.
# Layout: <OUTPUT_DIR>/<pdf_stem>/{pages, images, images_vector, text, manifest.json}
# Safe to destroy: rendered pages/figures/text files are intermediate
# products; the lasting result is only the dataset file below.
OUTPUT_DIR = os.environ.get("QUES_OUTPUT_DIR", "sampleData/ques_bank/output")

# The one output that matters: the consolidated dataset file. One JSON
# record per PDF page; records from every parsed PDF are appended here
# (deduped per pdf_name + page_number). Must be persisted in containers.
QUESTIONS_JSON_FILE = os.environ.get("QUES_QUESTIONS_JSON", "sampleData/ques_bank/output/questions_data.json")
