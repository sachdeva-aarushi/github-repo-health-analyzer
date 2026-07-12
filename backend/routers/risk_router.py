from fastapi import APIRouter
from services.github_service import (
    get_contributors,
    get_pull_requests,
    get_issues,
    get_commits,
    get_repo_metadata
)
from analysis.risk_analysis import compute_risk

router = APIRouter(prefix="/risk", tags=["Risk"])


from utils.cache import global_cache

@router.get("/{owner}/{repo}")
def get_risk(owner: str, repo: str):
    cache_key = f"endpoint:risk:{owner.lower()}:{repo.lower()}"
    
    def fetch():
        metadata = get_repo_metadata(owner, repo)
        
        canonical_owner, canonical_repo = owner, repo
        if metadata and "full_name" in metadata:
            parts = metadata["full_name"].split("/")
            if len(parts) == 2:
                canonical_owner, canonical_repo = parts[0], parts[1]

        contributors = get_contributors(canonical_owner, canonical_repo)
        prs = get_pull_requests(canonical_owner, canonical_repo)
        issues = get_issues(canonical_owner, canonical_repo)
        commits = get_commits(canonical_owner, canonical_repo)

        from services.github_service import get_open_prs_count
        actual_open_prs = get_open_prs_count(canonical_owner, canonical_repo)

        open_issues_and_prs = metadata.get("open_issues_count", 0) if metadata else 0
        actual_open_issues = max(0, open_issues_and_prs - actual_open_prs)

        return compute_risk(
            contributors, 
            prs, 
            issues, 
            commits, 
            actual_open_prs=actual_open_prs, 
            actual_open_issues=actual_open_issues
        )

    return global_cache.get_or_fetch(cache_key, fetch)