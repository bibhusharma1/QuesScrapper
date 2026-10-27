# Central configuration for the question-bank scraping pipeline.
#
# Settings load from a .env file in the project root (= the sample
# .env.example, copy it and edit). Real environment variables win over
# .env values. All supported variables:
#
#   QUES_INPUT_DIRS       comma-separated list of folders scanned for *.pdf
#   QUES_INPUT_PDFS       comma-separated list of specific PDF file paths
#                         (optional; parsed in addition to the folders)
#   QUES_OUTPUT_DIR       temp extraction folder (pages/images/text) — may
#                         be deleted freely; nothing here needs to survive
#   QUES_QUESTIONS_JSON   the dataset file to append results into — the
#                         one output that must be kept

import os

from dotenv import load_dotenv

# Loads values from ./.env into the environment, without overwriting
# variables that were already set (shell env / container env wins).
load_dotenv()


def _split_env(name):
    """Split a comma-separated env var into a clean list of strings."""
    raw = os.environ.get(name, "")
    return [part.strip() for part in raw.split(",") if part.strip()]


# Comma-separated folders scanned recursively for PDFs.
INPUT_DIRS = _split_env("QUES_INPUT_DIRS") or [
    os.environ.get("QUES_INPUT_PDF_FOLDER", "sampleData/ques_bank")
]

# Comma-separated explicit PDF paths, parsed in addition to INPUT_DIRS.
# Lets you read specific papers only. Leave empty to scan whole folders.
INPUT_PDFS = _split_env("QUES_INPUT_PDFS")

# Temp folder for extraction artifacts (docs say: disposable).
OUTPUT_DIR = os.environ.get("QUES_OUTPUT_DIR", "sampleData/ques_bank/output")

# The dataset file every run appends into — the one output that matters.
QUESTIONS_JSON_FILE = os.environ.get(
    "QUES_QUESTIONS_JSON", "sampleData/ques_bank/output/questions_data.json"
)
