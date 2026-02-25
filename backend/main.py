import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from github_api import get_commits, get_rate_limit, get_contributors
from analysis import analyze_commits, analyze_contributors

#Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI(
    title="GitHub Repo Health Analyzer API",
    description="Analyzes commit activity and health metrics for public GitHub repositories.",
    version="1.0.0",
)

#Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/commits/{owner}/{repo}")
def get_commit_analysis(owner: str, repo: str):
    """
    Analyze repository commits and return daily commit counts.

    Args:
        owner: Repository owner (username or organization)
        repo: Repository name

    Returns:
        JSON with dates, counts, and total_commits arrays for charting.
    """
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
@app.get("/contributors/{owner}/{repo}")
def contributors(owner: str, repo: str):
    raw_data = get_contributors(owner, repo)
    analyzed = analyze_contributors(raw_data)
    return analyzed