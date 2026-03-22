from fastapi import APIRouter, HTTPException
from services.github_service import get_commits
from analysis.commit_analysis import analyze_commit_velocity

router = APIRouter(tags=["Commits"])

@router.get("/commit-velocity/{owner}/{repo}")
def get_commit_velocity(owner: str, repo: str):

    commits = get_commits(owner, repo)

    if commits is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch commits for {owner}/{repo}."
        )

    velocity = analyze_commit_velocity(commits)

    return {
        "repository": f"{owner}/{repo}",
        "velocity": velocity
    }