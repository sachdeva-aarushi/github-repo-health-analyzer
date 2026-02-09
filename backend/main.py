from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from github_api import get_commits
from analysis import analyze_commits

# Create FastAPI app
app = FastAPI(title="GitHub Repo Health Analyzer API")

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint to check if API is running"""
    return {"status": "API running"}

@app.get("/test/{owner}/{repo}")
def test_repo(owner: str, repo: str):
    """
    Test endpoint to fetch repository commits and return basic info.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
    
    Returns:
        Dictionary with repository name and commit count
    """
    # Fetch commits from GitHub
    commits = get_commits(owner, repo)
    
    # Handle API errors
    if commits is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch data for repository {owner}/{repo}. Please check if the repository exists."
        )
    
    # Return repository info
    return {
        "repository": f"{owner}/{repo}",
        "commit_count": len(commits)
    }

@app.get("/commits/{owner}/{repo}")
def get_commit_analysis(owner: str, repo: str):
    """
    Analyze repository commits and return daily commit counts.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
    
    Returns:
        Dictionary with dates and counts arrays for charting
    """
    # Fetch commits from GitHub
    commits = get_commits(owner, repo)
    
    # Handle API errors
    if commits is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch data for repository {owner}/{repo}. Please check if the repository exists."
        )
    
    # Analyze commits using pandas
    analysis_result = analyze_commits(commits)
    
    # Return chart-ready data
    return {
        "repository": f"{owner}/{repo}",
        "data": analysis_result
    }
