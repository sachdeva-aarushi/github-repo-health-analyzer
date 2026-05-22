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
        # Fetch raw GitHub data
        metadata = get_repo_metadata(owner, repo)
        languages = get_repo_languages(owner, repo)
        tree = get_repo_tree(owner, repo)
        pull_requests = get_pull_requests(owner, repo)
        issues = get_issues(owner, repo)

        # Analyze structure
        structure = analyze_repo_structure(tree)

        # Combine into final summary
        summary = summarize_repository(
            metadata,
            languages,
            structure,
            pull_requests,
            issues
        )

        return summary

    return global_cache.get_or_fetch(cache_key, fetch)