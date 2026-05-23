import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers.structure_router import router as structure_router
from routers.ai_router import router as ai_router
from routers.commits_router import router as commits_router

from services.github_service import get_commits, get_rate_limit, get_contributors
from analysis.commit_analysis import analyze_commits
from analysis.contributor_analysis import analyze_contributors

from routers.overview_router import router as overview_router
from routers.health_router import router as health_router
from routers import risk_router

#Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI(
    title="GitHub Repo Health Analyzer API",
    description="Analyzes commit activity and health metrics for public GitHub repositories.",
    version="1.0.0",
)

#Include routers
app.include_router(overview_router)
app.include_router(structure_router)
app.include_router(commits_router)
app.include_router(health_router)
app.include_router(risk_router.router)
app.include_router(ai_router, prefix="/ai", tags=["AI Analysis"])

#Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #frontend URL
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from services.github_service import run_startup_validation
from ai.services.llm_service import run_gemini_validation

@app.on_event("startup")
def startup_event():
    run_startup_validation()
    run_gemini_validation()




#Endpoints

@app.get("/")
def root():
    """Root endpoint to check if API is running."""
    return {"status": "API running", "version": "1.0.0"}


@app.get("/health")
def health():
    """
    Health check – reports API status and GitHub rate-limit info so the
    frontend / developer can see if the token is configured and how many
    requests remain.
    """
    rate = get_rate_limit()
    token_set = bool(os.getenv("GITHUB_TOKEN"))
    return {
        "status": "healthy",
        "github_token_configured": token_set,
        "rate_limit": rate,
    }


@app.get("/test/{owner}/{repo}")
def test_repo(owner: str, repo: str):
    """
    Quick test – fetches a repo's commits and returns the count.

    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
    """
    commits = get_commits(owner, repo)

    if commits is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch data for repository {owner}/{repo}. "
                   f"Please check if the repository exists and you are not rate-limited.",
        )

    return {
        "repository": f"{owner}/{repo}",
        "commit_count": len(commits),
    }


from utils.cache import global_cache

@app.get("/commits/{owner}/{repo}")
def get_commit_analysis(owner: str, repo: str):
    cache_key = f"endpoint:commits:{owner.lower()}:{repo.lower()}"
    
    def fetch():
        commits = get_commits(owner, repo)

        if commits is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch data for repository {owner}/{repo}. "
                       f"Please check if the repository exists and you are not rate-limited.",
            )

        analysis_result = analyze_commits(commits)

        return {
            "repository": f"{owner}/{repo}",
            "data": analysis_result,
        }

    return global_cache.get_or_fetch(cache_key, fetch)


@app.get("/contributors/{owner}/{repo}")
def contributors(owner: str, repo: str):
    cache_key = f"endpoint:contributors:{owner.lower()}:{repo.lower()}"
    
    def fetch():
        raw_data = get_contributors(owner, repo)
        analyzed = analyze_contributors(raw_data)
        return analyzed

    return global_cache.get_or_fetch(cache_key, fetch)


import time
from ai.services.llm_service import generate_llm_response

@app.post("/api/ai/test")
@app.post("/ai/test")
def test_ai_connection():
    """
    Lightweight health-check endpoint that sends a minimal prompt to Gemini
    and returns latency and model information.
    """
    start_time = time.time()
    try:
        response = generate_llm_response(
            user_prompt="Respond with 'success'",
            system_prompt="You are a validation tester. Respond ONLY with the word 'success'.",
            max_tokens=10,
            temperature=0.0
        )
        latency = time.time() - start_time
        return {
            "status": "success",
            "model": os.getenv("MODEL_NAME", "gemini-2.5-flash"),
            "latency_seconds": round(latency, 3),
            "response": response.strip()
        }
    except Exception as e:
        latency = time.time() - start_time
        return {
            "status": "failure",
            "model": os.getenv("MODEL_NAME", "gemini-2.5-flash"),
            "latency_seconds": round(latency, 3),
            "error": str(e)
        }




