"""
Prompt template loader utility (enhanced for new AI architecture).

Supports legacy flat prompts + new structured system under prompts/system/
"""
import os
import re

_PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "prompts")


def load_prompt(prompt_name: str) -> str:
    """Legacy flat prompt loader (backward compatible)."""
    prompt_path = os.path.join(_PROMPTS_DIR, f"{prompt_name}.txt")
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt template '{prompt_name}' not found at {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def load_system_prompt(name: str = "analyst") -> str:
    """Load the permanent system role prompt for the GitIntel Analyst."""
    path = os.path.join(_PROMPTS_DIR, "system", f"{name}.txt")
    if not os.path.exists(path):
        raise FileNotFoundError(f"System prompt '{name}' not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_structured_template(name: str = "question") -> str:
    """Load structured context/user section templates."""
    path = os.path.join(_PROMPTS_DIR, "templates", f"{name}.txt")
    if not os.path.exists(path):
        path = os.path.join(_PROMPTS_DIR, f"{name}.txt")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Structured template '{name}' not found")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def sanitize_user_content(text: str, max_length: int = 500) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length] + "..."
    return cleaned
