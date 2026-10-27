# Puts the project root on sys.path so tests can import project
# packages (config, ParsethePDF, ParsePipeLIne) without installation.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
