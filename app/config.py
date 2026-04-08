import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
TRANSCRIPTS_DIR = os.path.join(RESULTS_DIR, "transcripts")

DEFAULT_MODEL = "gpt-4o-mini"

# Max tool invocation cycles
MAX_STEPS = 10
