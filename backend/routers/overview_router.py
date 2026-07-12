from fastapi import APIRouter
from services.github_service import (
    get_repo_metadata,
    get_repo_languages,
    get_repo_tree,
    get_pull_requests,
    get_issues
)
from analysis.evolution_analysis import (
    analyze_repo_structure,
    summarize_repository
)
router = APIRouter(
    prefix="/repo",
    tags=["Repository Overview"]
)

from utils.cache import global_cache

@router.get("/overview/{owner}/{repo}")
def repository_overview(owner: str, repo: str):
    cache_key = f"endpoint:overview:{owner.lower()}:{repo.lower()}"
    
    def fetch():
        # Fetch raw GitHub data to get canonical name
        metadata = get_repo_metadata(owner, repo)
        
        canonical_owner, canonical_repo = owner, repo
        if metadata and "full_name" in metadata:
            parts = metadata["full_name"].split("/")
            if len(parts) == 2:
                canonical_owner, canonical_repo = parts[0], parts[1]

        languages = get_repo_languages(canonical_owner, canonical_repo)
        tree = get_repo_tree(canonical_owner, canonical_repo)
        pull_requests = get_pull_requests(canonical_owner, canonical_repo)
        issues = get_issues(canonical_owner, canonical_repo)

        # Fetch actual open PRs count via Link header
        from services.github_service import get_open_prs_count
        actual_open_prs = get_open_prs_count(canonical_owner, canonical_repo)

        # Get open issues (metadata's open_issues_count has issues + PRs)
        open_issues_and_prs = metadata.get("open_issues_count", 0) if metadata else 0
        actual_open_issues = max(0, open_issues_and_prs - actual_open_prs)

        # Analyze structure
        structure = analyze_repo_structure(tree)

        # Combine into final summary
        summary = summarize_repository(
            metadata,
            languages,
            structure,
            pull_requests,
            issues,
            actual_open_prs=actual_open_prs,
            actual_open_issues=actual_open_issues
        )

        return summary

    return global_cache.get_or_fetch(cache_key, fetch)