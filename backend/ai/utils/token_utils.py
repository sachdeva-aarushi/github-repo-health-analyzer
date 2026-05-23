"""
Token counting and context size management utilities.

Uses a simple character-based heuristic (~4 chars per token) to estimate
token usage and truncate context sections that would exceed model limits.
"""


# Conservative token budget for the context passed to the LLM.
# Gemini models support huge contexts; we cap at 3000 to keep
# response generation extremely fast and minimize API latency.
MAX_CONTEXT_TOKENS = 6000



def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a string.

    Uses the standard heuristic of 1 token ≈ 4 characters.

    Args:
        text: The text to estimate tokens for.

    Returns:
        Estimated token count.
    """
    return max(1, len(text) // 4)


def truncate_to_token_budget(text: str, max_tokens: int = MAX_CONTEXT_TOKENS) -> str:
    """
    Truncate text to fit within a token budget.

    Truncates by character count derived from the token limit so the
    resulting string is guaranteed to be within the budget.

    Args:
        text: The text to truncate.
        max_tokens: Maximum allowed tokens.

    Returns:
        Truncated text with a notice appended if truncation occurred.
    """
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]
    return truncated + "\n\n[Context truncated to fit model token limit.]"


def fits_in_budget(text: str, max_tokens: int = MAX_CONTEXT_TOKENS) -> bool:
    """Return True if the text fits within the token budget."""
    return estimate_tokens(text) <= max_tokens
