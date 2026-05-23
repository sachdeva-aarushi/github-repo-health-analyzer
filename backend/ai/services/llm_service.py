"""
LLM service — provider abstraction layer.

This is the single entry point for all LLM calls in the application.
It selects the correct provider based on the PROVIDER environment variable
and delegates the call. Adding a new provider requires only:
  1. Creating a new file in ai/providers/
  2. Adding a case here.

Business logic, prompting strategy, and context building all live in
ai/services/repo_ai_analysis.py — not here.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Supported provider identifiers
_PROVIDER_GEMINI = "gemini"

_DEFAULT_PROVIDER = _PROVIDER_GEMINI


def generate_llm_response(
    user_prompt: str,
    system_prompt: str = "You are a senior software architect analyzing GitHub repositories.",
    max_tokens: int = 1024,
    temperature: float = 0.3,
) -> str:
    """
    Route an LLM request to the configured provider.

    Args:
        user_prompt: The data/context prompt for the model.
        system_prompt: Role/persona instructions for the model.
        max_tokens: Maximum tokens in the response.
        temperature: Sampling temperature.

    Returns:
        Generated text response from the LLM.

    Raises:
        RuntimeError: If the provider call fails.
    """
    # Enforce Gemini as the only active provider
    provider = os.getenv("PROVIDER", _DEFAULT_PROVIDER).lower().strip()
    if provider != _PROVIDER_GEMINI:
        logger.warning("Provider '%s' is deprecated/unsupported. Forcing route to Gemini.", provider)
    
    logger.info("LLM request routed to Gemini provider.")
    from ai.providers.gemini_provider import generate_response
    return generate_response(user_prompt, system_prompt, max_tokens, temperature)


def run_gemini_validation():
    """
    Validates Gemini API Key on application startup.
    Prints status information directly to console.
    """
    import sys
    print("\n" + "="*50)
    print(" GITINTEL STARTUP VALIDATION: GEMINI LLM PROVIDER")
    print("="*50)
    sys.stdout.flush()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY is missing in the environment or .env file.")
        print("[ERROR] AI analysis features will fail.")
        print("="*50 + "\n")
        sys.stdout.flush()
        return False
        
    import google.generativeai as genai
    try:
        genai.configure(api_key=api_key)
        # Attempt to list models to verify the key works
        models = list(genai.list_models())
        default_model = os.getenv("MODEL_NAME", "gemini-2.5-flash")
        
        print("[SUCCESS] GEMINI_API_KEY loaded successfully!")
        print(f"[SUCCESS] Gemini connection verified. Default Model: {default_model}")
        print("="*50 + "\n")
        sys.stdout.flush()
        return True
    except Exception as e:
        print("[ERROR] GEMINI_API_KEY is loaded but is INVALID (Authentication Failure).")
        print(f"[ERROR] Gemini API Error: {e}")
        print("="*50 + "\n")
        sys.stdout.flush()
        return False


