from fastapi import APIRouter, HTTPException
from services.github_service import (get_commits,get_contributors,get_pull_requests,get_issues,get_repo_tree)
from analysis.health_analysis import analyze_health
router = APIRouter(
    prefix="/repo",
    tags=["Health Analysis"])

from utils.cache import global_cache

@router.get("/health/{owner}/{repo}")
def get_repo_health(owner: str, repo: str):
    cache_key = f"endpoint:health:{owner.lower()}:{repo.lower()}"
    
    def fetch():
        try:
            commits = get_commits(owner, repo)
            if commits is None:
                commits = []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch commits: {str(e)}")
        
        try:
            contributors = get_contributors(owner, repo)
            if contributors is None:
                contributors = []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch contributors: {str(e)}")
        
        try:
            prs = get_pull_requests(owner, repo)
            if prs is None:
                prs = []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch pull requests: {str(e)}")
        
        try:
            issues = get_issues(owner, repo)
            if issues is None:
                issues = []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch issues: {str(e)}")

        try:
            tree_data = get_repo_tree(owner, repo)
            files = [item for item in tree_data.get("tree", []) if item.get("type") == "blob"]
        except Exception:
            files = []
        
        try:
            health = analyze_health(
                commits=commits,
                contributors=contributors,
                prs=prs,
                issues=issues,
                files=files
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to analyze health: {str(e)}")

        return {
            "repository": f"{owner}/{repo}",
            "health": health
        }

    return global_cache.get_or_fetch(cache_key, fetch)