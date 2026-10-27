during test this error came in
testcode instrcution
uv run python -m ParsePipeLIne.pipeline

Don't run pipeline.py directly.
uv run python -m ParsePipeLIne.pipeline


But this command failed:
python "/home/nsm/Documents/BibhuWorks/QuesScrapper/ParsePipeLIne/pipeline.py"


When you execute a Python file directly, Python puts the script's directory (ParsePipeLIne/) at the front of its import path. The project root isn't necessarily included, so the sibling package ParsethePDF can't be found.
What to do
Use this command from your project root:
uv run python -m ParsePipeLIne.pipeline


Don't run pipeline.py directly.