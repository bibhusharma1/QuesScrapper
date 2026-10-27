# Container image for the QuesScrapper pipeline.
# The extraction artifacts (pages/images/text) are written to /tmp and
# treated as disposable; only questions_data.json is meant to be persisted
# by mounting a save path over /data/save.

FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Install dependencies first so code changes don't bust the layer cache.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

# Container defaults: PDFs in, dataset JSON out (mount and set these).
ENV QUES_INPUT_PDF_FOLDER=/data/input \
    QUES_OUTPUT_DIR=/tmp/qa_extraction \
    QUES_QUESTIONS_JSON=/data/save/questions_data.json

ENTRYPOINT [".venv/bin/python", "-m", "ParsePipeLIne.pipeline"]
