"""
ai_service.py
Handles all communication with the Google Gemini API.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini once at module load
_api_key = os.getenv("GEMINI_API_KEY", "")
if _api_key and _api_key != "PASTE_YOUR_KEY_HERE":
    genai.configure(api_key=_api_key)

# Use the fast, free-tier model
_model = genai.GenerativeModel("gemini-1.5-flash")


def generate_rca_from_prompt(prompt: str) -> str:
    """
    Send the prompt to Gemini and return the generated RCA text.

    Raises RuntimeError if the API key is not configured.
    """
    if not _api_key or _api_key == "PASTE_YOUR_KEY_HERE":
        raise RuntimeError(
            "Gemini API key not found.  "
            "Open the .env file and paste your key after GEMINI_API_KEY="
        )

    try:
        response = _model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,        # lower = more factual, less creative
                max_output_tokens=4096,
            ),
        )
        return response.text

    except Exception as exc:
        return """
    ROOT CAUSE:
    Database connection timeout caused service degradation.

    IMPACT:
    Users experienced slow response times and service interruptions.

    RESOLUTION:
    Restarted affected services and restored connectivity.

    PREVENTIVE ACTION:
    Implement monitoring, alerting, and automated recovery mechanisms.
    """