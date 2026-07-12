from fastapi import APIRouter, HTTPException
from services.github_service import (
    get_commits,
    get_contributors,
    get_pull_requests,
    get_issues,
    get_repo_tree,
    get_repo_metadata
)
from analysis.health_analysis import analyze_health
router = APIRouter(
    prefix="/repo",
    tags=["Health Analysis"])

from utils.cache import global_cache

@router.get("/health/{owner}/{repo}")
def get_repo_health(owner: str, repo: str):
    cache_key = f"endpoint:health:{owner.lower()}:{repo.lower()}"
    
    def fetch():
        metadata = get_repo_metadata(owner, repo)
        
        canonical_owner, canonical_repo = owner, repo
        if metadata and "full_name" in metadata:
            parts = metadata["full_name"].split("/")
            if len(parts) == 2:
                canonical_owner, canonical_repo = parts[0], parts[1]

        try:
            commits = get_commits(canonical_owner, canonical_repo)
            if commits is None:
                commits = []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch commits: {str(e)}")
        
        try:
            contributors = get_contributors(canonical_owner, canonical_repo)
            if contributors is None:
                contributors = []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch contributors: {str(e)}")
        
        try:
            prs = get_pull_requests(canonical_owner, canonical_repo)
            if prs is None:
                prs = []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch pull requests: {str(e)}")
        
        try:
            issues = get_issues(canonical_owner, canonical_repo)
            if issues is None:
                issues = []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch issues: {str(e)}")

        try:
            tree_data = get_repo_tree(canonical_owner, canonical_repo)
            files = [item for item in tree_data.get("tree", []) if item.get("type") == "blob"]
        except Exception:
            files = []
        
        from services.github_service import get_open_prs_count
        actual_open_prs = get_open_prs_count(canonical_owner, canonical_repo)

        open_issues_and_prs = metadata.get("open_issues_count", 0) if metadata else 0
        actual_open_issues = max(0, open_issues_and_prs - actual_open_prs)

        try:
            health = analyze_health(
                commits=commits,
                contributors=contributors,
                prs=prs,
                issues=issues,
                files=files,
                actual_open_issues=actual_open_issues,
                actual_open_prs=actual_open_prs
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to analyze health: {str(e)}")

        return {
            "repository": f"{canonical_owner}/{canonical_repo}",
            "health": health
        }

    return global_cache.get_or_fetch(cache_key, fetch)