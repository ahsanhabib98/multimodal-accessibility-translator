import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# -------------------------------------------------------
# 1. Load .env file from the project root
# -------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]


load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


# -------------------------------------------------------
# 2. Create and return a shared OpenAI client
# -------------------------------------------------------
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing.\n"
            "Make sure you created a .env file at project root:\n\n"
            "  multimodal-accessibility-translator/.env\n\n"
            "And added:\n"
            "  OPENAI_API_KEY=your-key-here\n"
        )

    return OpenAI(api_key=api_key)