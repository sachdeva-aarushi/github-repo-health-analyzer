"""
AI analysis router.

Thin router — delegates all business logic to ai/services/repo_ai_analysis.py.
Uses a sync def (not async) intentionally: the underlying service makes blocking
requests.get() and synchronous OpenAI SDK calls. FastAPI automatically runs sync
routes in a threadpool, avoiding event loop starvation.
"""

from fastapi import APIRouter, HTTPException
from models.ai_model import AISummaryRequest, AISummaryResponse

router = APIRouter(tags=["AI Analysis"])


from utils.cache import global_cache

@router.post("/summary", response_model=AISummaryResponse)
def get_ai_summary(request: AISummaryRequest):
    """
    Generate an AI-narrated summary of repository health and analysis.

    Fetches repository data, runs all deterministic analyzers, and
    passes the structured output to an LLM for narration.

    Args:
        request: Contains owner and repo name.

    Returns:
        AI-generated summary with metadata.
    """
    # Import here to keep the router file free of heavy dependencies
    # and to avoid circular imports at module load time.
    from ai.services.repo_ai_analysis import analyze_repository_ai

    cache_key = f"endpoint:ai_summary:{request.owner.lower()}:{request.repo.lower()}"

    def fetch():
        try:
            result = analyze_repository_ai(request.owner, request.repo)
            return result

        except ValueError as e:
            # Bad repo name, repo not found, insufficient data
            raise HTTPException(status_code=404, detail=str(e))

        except RuntimeError as e:
            # LLM provider failures (auth, rate limit, connection)
            raise HTTPException(status_code=502, detail=str(e))

        except Exception as e:
            # Unexpected errors — logged in the service layer
            raise HTTPException(
                status_code=500,
                detail=f"AI analysis failed unexpectedly: {type(e).__name__}",
            )

    res = global_cache.get_or_fetch(cache_key, fetch)
    return AISummaryResponse(**res)


from models.ai_model import AIQuestionRequest, AIQuestionResponse

@router.post("/question", response_model=AIQuestionResponse)
def get_ai_question(request: AIQuestionRequest):
    """
    Answer a user question about a repository using its metrics.
    """
    from ai.services.repo_ai_analysis import ask_repository_question_ai

    # Generate a cache key that includes the lower-cased owner, repo, and question text
    cache_key = f"endpoint:ai_question:{request.owner.lower()}:{request.repo.lower()}:{request.question.lower().strip()}"

    def fetch():
        try:
            result = ask_repository_question_ai(request.owner, request.repo, request.question)
            return result

        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=str(e))

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"AI Q&A failed unexpectedly: {type(e).__name__}",
            )

    res = global_cache.get_or_fetch(cache_key, fetch)
    return AIQuestionResponse(**res)


