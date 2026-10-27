# test.md — running the pipeline

## The command

Always run from the **project root**:

```bash
uv run python -m ParsePipeLIne.pipeline
```

## Do NOT run pipeline.py directly

This fails:

```bash
python ParsePipeLIne/pipeline.py
```

**Why it fails:** when a Python file is executed directly, Python puts that file's directory (`ParsePipeLIne/`) at the front of the import path. The project root is not on the path, so the sibling package `ParsethePDF` cannot be found.

**Fix:** run it as a module with `-m` from the project root (command at the top). Same is valid: `uv run python main.py`.
