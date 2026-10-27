# test.md — running the pipeline

Run from the **project root**:

```bash
uv run python -m ParsePipeLIne.pipeline
```

**Do NOT** run `python ParsePipeLIne/pipeline.py` directly. Python then can't find the sibling `ParsethePDF` package — imports break.

Fix = run with `-m` from the project root (top command). Also valid: `uv run python main.py`.
