from analysis.commit_analysis import analyze_commit_velocity

@router.get("/commit-velocity/{owner}/{repo}")
def get_commit_velocity(owner: str, repo: str):

    commits = get_commits(owner, repo)

    velocity = analyze_commit_velocity(commits)

    return {
        "repository": f"{owner}/{repo}",
        "velocity": velocity
    }