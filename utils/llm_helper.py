"""
LLM Helper Module for Multi-Agent BI Requirement Analysis Application.

This module provides a singleton instance of ChatGoogleGenerativeAI (Gemini)
for reuse across all agents in the application. It handles configuration,
validation, and initialization of the LLM with proper logging and error handling.

Typical usage:
    from utils.llm_helper import get_llm
    
    llm = get_llm()
    response = llm.invoke("Your prompt here")
    
    # With custom parameters
    llm_custom = get_llm(temperature=0.7, max_tokens=1000)
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler with formatting
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class LLMConfigurationError(Exception):
    """Raised when LLM configuration is invalid or incomplete."""

    pass


def _validate_environment() -> None:
    """
    Validate that all required environment variables are set.

    Raises:
        LLMConfigurationError: If required environment variables are missing.
    """
    required_vars = ["GOOGLE_API_KEY"]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        error_msg = (
            f"Missing required environment variables: {', '.join(missing_vars)}. "
            "Please ensure these variables are set in your .env file or system environment."
        )
        logger.error(error_msg)
        raise LLMConfigurationError(error_msg)

    logger.info("Environment variables validated successfully.")


def _get_llm_provider() -> str:
    """
    Get the LLM provider from environment variables.

    Returns:
        str: The LLM provider name (default: "gemini").
    """
    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    logger.debug(f"Using LLM provider: {provider}")
    return provider


# Module-level singleton instance
_llm_instance: Optional[ChatGoogleGenerativeAI] = None


def get_llm(
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> ChatGoogleGenerativeAI:
    """
    Get or create a singleton instance of ChatGoogleGenerativeAI (Gemini).

    This function ensures that all agents share the same LLM instance for
    efficient resource usage. When called with custom parameters, those
    parameters override the base configuration for that call only.

    Args:
        temperature (Optional[float]): Controls randomness of responses (0.0-2.0).
            If not provided, uses default Gemini configuration.
        max_tokens (Optional[int]): Maximum tokens in the response.
            If not provided, uses default Gemini configuration.

    Returns:
        ChatGoogleGenerativeAI: A configured Gemini LLM instance.

    Raises:
        LLMConfigurationError: If required environment variables are missing.

    Example:
        >>> llm = get_llm()
        >>> response = llm.invoke("Analyze this requirement...")
        
        >>> llm_custom = get_llm(temperature=0.5, max_tokens=2000)
        >>> response = llm_custom.invoke("Generate detailed analysis...")
    """
    global _llm_instance

    # Validate environment on first call
    if _llm_instance is None:
        _validate_environment()

    # Create base configuration
    api_key = os.getenv("GOOGLE_API_KEY")
    llm_config = {
        "model": "gemini-pro",
        "google_api_key": api_key,
    }

    # Add optional parameters if provided
    if temperature is not None:
        llm_config["temperature"] = temperature
    if max_tokens is not None:
        llm_config["max_output_tokens"] = max_tokens

    # Create or return instance
    if _llm_instance is None:
        logger.info(
            "Initializing ChatGoogleGenerativeAI (Gemini) singleton instance."
        )
        _llm_instance = ChatGoogleGenerativeAI(**llm_config)
        logger.info("LLM instance initialized successfully.")
    else:
        # If custom parameters provided, update instance configuration
        if temperature is not None or max_tokens is not None:
            logger.debug(
                f"Creating LLM instance with custom parameters: "
                f"temperature={temperature}, max_tokens={max_tokens}"
            )
            return ChatGoogleGenerativeAI(**llm_config)

    return _llm_instance


def reset_llm() -> None:
    """
    Reset the singleton LLM instance.

    This is primarily useful for testing purposes. After calling this function,
    the next call to get_llm() will create a new instance.

    Example:
        >>> reset_llm()
        >>> new_llm = get_llm()  # Creates a fresh instance
    """
    global _llm_instance
    if _llm_instance is not None:
        logger.info("Resetting LLM singleton instance.")
        _llm_instance = None
