from typing import Dict, List
from datetime import datetime, timezone, timedelta
from analysis.contributor_analysis import analyze_contributors

def get_trend(items: List[Dict]) -> List[int]:
    now = datetime.now(timezone.utc)
    trend = []
    
    for weeks_ago in [3, 2, 1, 0]:
        t = now - timedelta(weeks=weeks_ago)
        count = 0
        for item in items:
            try:
                created_at_str = item.get("created_at")
                if not created_at_str: continue
                # Handle github's ISO 8601 string
                created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                if created_at > t: continue
                
                closed_at_str = item.get("closed_at")
                if closed_at_str:
                    closed_at = datetime.strptime(closed_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    if closed_at <= t: continue
                count += 1
            except Exception:
                pass
        trend.append(count)
    return trend


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


def compute_pr_risk(prs: List[Dict], actual_open_prs: int = None) -> Dict:
    open_prs = [p for p in prs if p["state"] == "open"]
    closed_prs = [p for p in prs if p["state"] == "closed"]

    open_count = actual_open_prs if actual_open_prs is not None else len(open_prs)
    closed_count = len(closed_prs)

    if closed_count == 0:
        merge_ratio = 0
    else:
        merge_ratio = closed_count / (open_count + closed_count)

    # scoring
    total_prs = open_count + closed_count
    if total_prs > 0 and total_prs < 20:
        if merge_ratio < 0.4:
            score = 85
        elif merge_ratio < 0.6:
            score = 60
        else:
            score = 30
    else:
        if open_count > 150 or (total_prs > 0 and merge_ratio < 0.4):
            score = 85
        elif open_count > 75:
            score = 60
        else:
            score = 30

    insights = []
    if open_count > 100:
        insights.append(f"{open_count} open PRs — high backlog")
    elif open_count > 0:
        insights.append(f"{open_count} open PRs")

    if total_prs > 0:
        if merge_ratio < 0.5:
            insights.append(f"Low merge rate ({int(merge_ratio*100)}%) — check for stalled PRs")
        elif merge_ratio >= 0.8:
            insights.append(f"Good merge rate ({int(merge_ratio*100)}%)")

    trend = get_trend(prs)

    return {
        "level": get_level(score),
        "score": score,
        "open_prs": open_count,
        "merge_ratio": round(merge_ratio, 2),
        "insights": insights,
        "trend": trend
    }


def compute_issue_risk(issues: List[Dict], actual_open_issues: int = None) -> Dict:
    open_issues = [i for i in issues if i["state"] == "open"]
    closed_issues = [i for i in issues if i["state"] == "closed"]

    open_count = actual_open_issues if actual_open_issues is not None else len(open_issues)
    closed_count = len(closed_issues)

    if closed_count == 0:
        close_ratio = 0
    else:
        close_ratio = closed_count / (open_count + closed_count)

    total_issues = open_count + closed_count
    if total_issues > 0 and total_issues < 20:
        if close_ratio < 0.5:
            score = 85
        elif close_ratio < 0.7:
            score = 60
        else:
            score = 30
    else:
        if open_count > 300 or (total_issues > 0 and close_ratio < 0.5):
            score = 85
        elif open_count > 150:
            score = 60
        else:
            score = 30

    insights = []
    if open_count > 200:
        insights.append(f"{open_count} open issues — growing backlog")
    elif open_count > 0:
        insights.append(f"{open_count} open issues")
        
    if total_issues > 0:
        if close_ratio < 0.6:
            insights.append(f"Low resolution rate ({int(close_ratio*100)}%)")
        elif close_ratio > 0.8:
            insights.append(f"Good resolution rate ({int(close_ratio*100)}%)")

    trend = get_trend(issues)

    return {
        "level": get_level(score),
        "score": score,
        "open_issues": open_count,
        "close_ratio": round(close_ratio, 2),
        "insights": insights,
        "trend": trend
    }


def compute_activity_risk(commits: List[Dict]) -> Dict:
    if not commits:
        return {"level": "HIGH", "score": 90}

    latest_commit = commits[0]["commit"]["author"]["date"]

    score = 30

    return {
        "level": get_level(score),
        "score": score,
        "last_commit": latest_commit
    }


def compute_responsiveness(prs: List[Dict], issues: List[Dict]) -> Dict:
    first_response_times = []
    merge_times = []
    close_times = []
    now = datetime.now(timezone.utc)
    stale_prs = 0

    for pr in prs:
        try:
            created = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if pr.get("merged_at"):
                merged = datetime.strptime(pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                merge_times.append((merged - created).total_seconds() / 3600)
            if pr.get("closed_at"):
                closed = datetime.strptime(pr["closed_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                first_response_times.append((closed - created).total_seconds() / 3600)
            if pr["state"] == "open" and (now - created).days > 30:
                stale_prs += 1
        except Exception:
            pass

    for issue in issues:
        try:
            if issue.get("pull_request"):
                continue
            created = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if issue.get("closed_at"):
                closed = datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                close_times.append((closed - created).total_seconds() / 3600)
        except Exception:
            pass

    avg_first = round(sum(first_response_times) / len(first_response_times), 1) if first_response_times else 0
    avg_merge = round(sum(merge_times) / len(merge_times), 1) if merge_times else 0
    avg_close = round(sum(close_times) / len(close_times), 1) if close_times else 0

    return {
        "first_response": avg_first,
        "merge_time": avg_merge,
        "close_time": avg_close,
        "stale_prs": stale_prs
    }


def compute_trend_risk(commits: List[Dict]) -> Dict:
    now = datetime.now(timezone.utc)
    weekly = []
    for weeks_ago in range(3, -1, -1):
        start = now - timedelta(weeks=weeks_ago + 1)
        end = now - timedelta(weeks=weeks_ago)
        count = 0
        for c in commits:
            try:
                date_str = c["commit"]["author"]["date"]
                date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                if start <= date < end:
                    count += 1
            except Exception:
                pass
        weekly.append(count)

    if len(weekly) >= 2 and weekly[-1] < weekly[0] * 0.5:
        level, desc = "HIGH", f"Commit activity dropped from {weekly[0]} to {weekly[-1]} this month"
    elif len(weekly) >= 2 and weekly[-1] > weekly[0] * 1.5:
        level, desc = "LOW", f"Commit activity rising ({weekly[0]} → {weekly[-1]})"
    else:
        level, desc = "MEDIUM", f"Commit activity stable (~{round(sum(weekly)/max(len(weekly),1))} commits/week)"

    return {"level": level, "value": desc}


def compute_maintainer_load(contributors: List[Dict]) -> Dict:
    if not contributors:
        return {"level": "HIGH", "value": "No contributor data"}
    total = sum(c.get("contributions", 0) for c in contributors)
    if total == 0:
        return {"level": "HIGH", "value": "No contributions found"}
    top_pct = contributors[0].get("contributions", 0) / total * 100
    if top_pct > 70:
        level = "HIGH"
    elif top_pct > 40:
        level = "MEDIUM"
    else:
        level = "LOW"
    return {"level": level, "value": f"Top maintainer handles {round(top_pct, 1)}% of commits"}


def compute_risk(contributors, prs, issues, commits, actual_open_prs: int = None, actual_open_issues: int = None) -> Dict:
    bus = compute_bus_factor_risk(contributors)
    pr = compute_pr_risk(prs, actual_open_prs=actual_open_prs)
    issue = compute_issue_risk(issues, actual_open_issues=actual_open_issues)
    activity = compute_activity_risk(commits)
    trend = compute_trend_risk(commits)
    maintainer = compute_maintainer_load(contributors)
    responsiveness = compute_responsiveness(prs, issues)

    resp_score = 100 - min(responsiveness["merge_time"] / 2, 50) - min(responsiveness["stale_prs"] * 2, 50)
    resp_level = get_level(max(0, 100 - resp_score))

    return {
        "summary": {
            "bus_factor": {
                "level": bus["level"],
                "value": f"Top contributor {round(bus['top_contributor_pct'], 1)}%"
            },
            "pr_backlog": {
                "level": pr["level"],
                "value": f"{pr['open_prs']} open PRs"
            },
            "trend": {
                "level": trend["level"],
                "value": trend["value"]
            },
            "maintainer_load": {
                "level": maintainer["level"],
                "value": maintainer["value"]
            },
            "responsiveness": {
                "level": resp_level,
                "value": f"Avg merge {responsiveness['merge_time']}h, {responsiveness['stale_prs']} stale PRs"
            }
        },

        "bus_factor_detail": bus,
        "pr_risk": pr,
        "issue_risk": issue,
        "activity_risk": activity,
        "responsiveness_detail": responsiveness
    }