"""
Pydantic schemas for the AI analysis endpoints.

Request and response models are kept separate so they can evolve independently.
Errors are communicated via HTTP status codes (HTTPException), not response body fields.
"""

from pydantic import BaseModel, Field


class AISummaryRequest(BaseModel):
    """Request body for POST /ai/summary."""

    owner: str = Field(..., min_length=1, max_length=100, description="GitHub repository owner.")
    repo: str = Field(..., min_length=1, max_length=100, description="GitHub repository name.")

    model_config = {"json_schema_extra": {"example": {"owner": "torvalds", "repo": "linux"}}}


class AISummaryResponse(BaseModel):
    """Successful response from POST /ai/summary."""

    owner: str = Field(..., description="GitHub repository owner.")
    repo: str = Field(..., description="GitHub repository name.")
    ai_summary: str = Field(..., description="AI-narrated analysis of the repository.")
    analysis_timestamp: str = Field(..., description="ISO 8601 UTC timestamp of analysis.")
    model_used: str = Field(..., description="LLM model identifier used to generate the summary.")


class AIQuestionRequest(BaseModel):
    """Request body for POST /ai/question."""
    owner: str = Field(..., min_length=1, max_length=100, description="GitHub repository owner.")
    repo: str = Field(..., min_length=1, max_length=100, description="GitHub repository name.")
    question: str = Field(..., min_length=1, max_length=1000, description="The user's question.")
    # NEW in v2 architecture
    dashboard_context: dict | None = None
    session_id: str | None = None


class AIQuestionResponse(BaseModel):
    """Successful response from POST /ai/question."""
    owner: str = Field(..., description="GitHub repository owner.")
    repo: str = Field(..., description="GitHub repository name.")
    question: str = Field(..., description="The user's question.")
    answer: str = Field(..., description="AI's response.")
    model_used: str = Field(..., description="LLM model identifier used.")

