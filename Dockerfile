# Container image for the QuesScrapper pipeline.
# The extraction artifacts (pages/images/text) are written to /tmp and
# treated as disposable; only questions_data.json is meant to be persisted
# by mounting a save path over /data/save.

FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# uid/gid 1000 matches the typical first user on Linux hosts, so files
# written to mounted save folders stay accessible to the host owner.
# Append -1000 to user with usermod if you need a different uid.
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Install dependencies first so code changes don't bust the layer cache.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

# Container defaults: PDFs in, dataset JSON out (mount and set these).
# Compose additionally loads .env via env_file (see docker-compose.yml).
ENV QUES_INPUT_DIRS=/data/input \
    QUES_OUTPUT_DIR=/tmp/qa_extraction \
    QUES_QUESTIONS_JSON=/data/save/questions_data.json

RUN chown -R app:app /app && chmod -R u+rwX,go+rX /app

USER app

ENTRYPOINT ["/app/.venv/bin/python", "-m", "ParsePipeLIne.pipeline"]
