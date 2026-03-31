from fastapi import APIRouter
from services.github_service import (
    get_contributors,
    get_pull_requests,
    get_issues,
    get_commits
)
from analysis.risk_analysis import compute_risk

router = APIRouter(prefix="/risk", tags=["Risk"])


@router.get("/{owner}/{repo}")
def get_risk(owner: str, repo: str):
    contributors = get_contributors(owner, repo)
    prs = get_pull_requests(owner, repo)
    issues = get_issues(owner, repo)
    commits = get_commits(owner, repo)

    return compute_risk(contributors, prs, issues, commits)