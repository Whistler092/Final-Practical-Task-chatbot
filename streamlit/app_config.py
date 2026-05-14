"""Application constants, environment checks, and logging setup for the Streamlit agent."""

from __future__ import annotations

import logging
import os
from typing import Tuple

# Azure OpenAI API version used for chat completions.
API_VERSION = "2024-08-01-preview"

SYSTEM_PROMPT = (
    "You are a helpful assistant specialized in historical natural disaster data (1900-2021). "
    "You have access to the query_disasters tool that searches a comprehensive disaster database. "
    "The tool accepts optional filters: country (e.g. 'Japan'), year (e.g. 2011), "
    "disaster_type (e.g. 'Earthquake', 'Flood', 'Storm'), and limit (default 10). "
    "Always use the query_disasters tool to answer questions about disasters rather than guessing. "
    "Summarize results highlighting key details like location, dates, deaths, and affected populations."
)


def configure_logging() -> None:
    """Configure root logging once so INFO lines appear in the terminal (e.g. when running `streamlit run`)."""
    if logging.root.handlers:
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def validate_env() -> Tuple[bool, str]:
    """
    Verify required environment variables for Azure OpenAI are present.

    Returns:
        (True, "") if all required variables are set; otherwise (False, error message).
    """
    required_vars = ["OPENAI_API_KEY", "MODEL", "AZURE_ENDPOINT"]
    missing = [name for name in required_vars if not os.getenv(name)]
    if missing:
        return False, f"Missing environment variables: {', '.join(missing)}"
    return True, ""
