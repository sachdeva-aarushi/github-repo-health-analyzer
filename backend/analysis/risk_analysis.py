from typing import Dict, List
from analysis.contributor_analysis import analyze_contributors


def get_level(score: float) -> str:
    if score >= 75:
        return "HIGH"
    elif score >= 50:
        return "MEDIUM"
    return "LOW"

def compute_bus_factor_risk(contributor_data: List[Dict]) -> Dict:
    data = analyze_contributors(contributor_data)

    top_pct = data["top_contributor_percentage"]
    bus_factor = data["bus_factor"]

    # score logic
    if bus_factor <= 2 or top_pct > 60:
        score = 85
    elif bus_factor <= 4:
        score = 60
    else:
        score = 30

    return {
        "level": get_level(score),
        "score": score,
        "top_contributor_pct": top_pct,
        "bus_factor": bus_factor,
        "contributors": data["contributors"]
    }


def compute_pr_risk(prs: List[Dict]) -> Dict:
    open_prs = [p for p in prs if p["state"] == "open"]
    closed_prs = [p for p in prs if p["state"] == "closed"]

    open_count = len(open_prs)
    closed_count = len(closed_prs)

    if closed_count == 0:
        merge_ratio = 0
    else:
        merge_ratio = closed_count / (open_count + closed_count)

    # scoring
    if open_count > 150 or merge_ratio < 0.4:
        score = 85
    elif open_count > 75:
        score = 60
    else:
        score = 30

    insights = []
    if open_count > 100:
        insights.append(f"{open_count} open PRs — high backlog")
    if merge_ratio < 0.5:
        insights.append("Merge rate is low")
    if len(open_prs) > 0:
        insights.append(f"{len(open_prs)} PRs pending review")

    return {
        "level": get_level(score),
        "score": score,
        "open_prs": open_count,
        "merge_ratio": round(merge_ratio, 2),
        "insights": insights
    }


def compute_issue_risk(issues: List[Dict]) -> Dict:
    open_issues = [i for i in issues if i["state"] == "open"]
    closed_issues = [i for i in issues if i["state"] == "closed"]

    open_count = len(open_issues)
    closed_count = len(closed_issues)

    if closed_count == 0:
        close_ratio = 0
    else:
        close_ratio = closed_count / (open_count + closed_count)

    if open_count > 300 or close_ratio < 0.5:
        score = 85
    elif open_count > 150:
        score = 60
    else:
        score = 30

    insights = []
    if open_count > 200:
        insights.append(f"{open_count} open issues — growing backlog")
    if close_ratio < 0.6:
        insights.append("Issue resolution rate is low")

    return {
        "level": get_level(score),
        "score": score,
        "open_issues": open_count,
        "close_ratio": round(close_ratio, 2),
        "insights": insights
    }


def compute_activity_risk(commits: List[Dict]) -> Dict:
    if not commits:
        return {"level": "HIGH", "score": 90}

    latest_commit = commits[0]["commit"]["author"]["date"]

    # simple heuristic (you can refine later)
    score = 30

    return {
        "level": get_level(score),
        "score": score,
        "last_commit": latest_commit
    }


def compute_risk(contributors, prs, issues, commits) -> Dict:
    bus = compute_bus_factor_risk(contributors)
    pr = compute_pr_risk(prs)
    issue = compute_issue_risk(issues)
    activity = compute_activity_risk(commits)

    return {
        "summary": {
            "bus_factor": {
                "level": bus["level"],
                "value": f"Top contributor {round(bus['top_contributor_pct'],1)}%"
            },
            "pr_backlog": {
                "level": pr["level"],
                "value": f"{pr['open_prs']} open PRs"
            },
            "trend": {
                "level": "HIGH",
                "value": "Rising risk signals"
            },
            "maintainer_load": {
                "level": "MEDIUM",
                "value": "Compute later"
            },
            "responsiveness": {
                "level": "MEDIUM",
                "value": "Compute later"
            }
        },

        "bus_factor_detail": bus,
        "pr_risk": pr,
        "issue_risk": issue,
        "activity_risk": activity
    }