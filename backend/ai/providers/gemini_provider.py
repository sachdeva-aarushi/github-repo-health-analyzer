"""
Gemini LLM provider.

Wraps the official Google Generative AI SDK for Gemini models.
Contains ONLY provider-level concerns:
- client initialization
- API call execution
- provider-specific error handling and timeouts
"""

import os
import logging
from typing import Optional
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPICallError, PermissionDenied, ResourceExhausted

logger = logging.getLogger(__name__)

# Lazy initialization flag
_is_configured = False


def _configure_client() -> None:
    """
    Configure the Google Generative AI SDK using the GEMINI_API_KEY.

    Raises:
        EnvironmentError: If GEMINI_API_KEY is not set.
    """
    global _is_configured
    if not _is_configured:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set. "
                "Add it to your .env file: GEMINI_API_KEY=your_key_here"
            )
        genai.configure(api_key=api_key)
        _is_configured = True


def generate_response(
    user_prompt: str,
    system_prompt: str = "You are a senior software architect analyzing GitHub repositories.",
    max_tokens: int = 2048,
    temperature: float = 0.3,
) -> str:
    """
    Generate a response from the Gemini LLM.

    Args:
        user_prompt: The data/context prompt (repository metrics, etc.).
        system_prompt: Role and guardrails for the model.
        max_tokens: Maximum tokens in the model response.
        temperature: Sampling temperature (lower = more deterministic).

    Returns:
        Generated response content as a string.

    Raises:
        RuntimeError: On any provider-level failure with a descriptive message.
    """
    model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")

    try:
        _configure_client()
        
        # Initialize generative model with the system instruction
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )

        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        # Call generate_content with a default request timeout of 30 seconds
        response = model.generate_content(
            user_prompt,
            generation_config=generation_config,
            request_options={"timeout": 30.0}
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text

    except PermissionDenied as e:
        logger.error("Gemini authentication failed — check GEMINI_API_KEY: %s", e)
        raise RuntimeError("LLM authentication failed. Check your GEMINI_API_KEY.")

    except ResourceExhausted as e:
        logger.warning("Gemini rate limit exceeded: %s", e)
        raise RuntimeError("LLM rate limit exceeded. Please try again shortly.")

    except GoogleAPICallError as e:
        logger.error("Gemini API error: %s", e)
        raise RuntimeError(f"Gemini API error: {e.message if hasattr(e, 'message') else str(e)}")

    except Exception as e:
        logger.error("Unexpected error in Gemini provider: %s", e)
        raise RuntimeError(f"LLM provider error: {str(e)}")
