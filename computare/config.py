"""
Configuration for Computare.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGTRACE_API_KEY = os.getenv("LANGTRACE_API_KEY")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Extraction settings
CONFIDENCE_THRESHOLD = 0.85  # Below this, fallback to Claude
MAX_PAGES_PER_STATEMENT = 50
DEFAULT_YEAR = 2024

# Claude settings
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Good balance of cost/accuracy
CLAUDE_MAX_TOKENS = 8192

# OpenAI / LangChain categorization settings
OPENAI_MODEL = "gpt-4o-mini"
CATEGORIZATION_BATCH_SIZE = 30  # Transactions per LLM call
CATEGORIZATION_LLM_TEMPERATURE = 0.0

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Bank detection patterns
BANK_PATTERNS = {
    "scotiabank": ["Scotiabank", "Bank of Nova Scotia", "Scotia"],
    "td": ["TD Canada Trust", "TD Bank", "Toronto-Dominion"],
    "rbc": ["RBC Royal Bank", "Royal Bank of Canada"],
    "bmo": ["BMO", "Bank of Montreal"],
    "cibc": ["CIBC", "Canadian Imperial Bank"],
}
