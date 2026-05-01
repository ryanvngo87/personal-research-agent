import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chroma")
NOTES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "notes")
TRACES_DIR = os.path.join(os.path.dirname(__file__), "..", "traces", "runs")

CHROMA_COLLECTION = "notes"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5
