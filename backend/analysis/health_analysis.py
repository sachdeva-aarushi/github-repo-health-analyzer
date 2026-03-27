import numpy as np
import pandas as pd
from datetime import datetime, timezone


def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 50
    return max(0, min(100, (value - min_val) / (max_val - min_val) * 100))


def analyze_health(commits, contributors, prs, issues):
    commit_dates = []

    for c in commits:
        try:
            date = c["commit"]["author"]["date"]
            commit_dates.append(pd.to_datetime(date))
        except:
            continue

    if not commit_dates:
        return {
            "score": 0,
            "status": "Risky",
            "summary": {
                "last_commit_days": None,
                "contributors": 0,
                "issue_close_rate": 0,
                "avg_pr_merge_time": 0
            },
            "dimension_scores": {
                "commit_frequency": 0,
                "recency": 0,
                "contributors": 0,
                "pr_speed": 0,
                "issues": 0
            },
            "health_distribution": {
                "maintenance": 0,
                "stability": 0,
                "contributors": 0,
                "security": 0,
                "efficiency": 0
            },
            "risk_signals": [{"name": "No commit history", "status": "high"}]
        }

    df = pd.DataFrame({"date": commit_dates})

    daily_counts = df["date"].dt.date.value_counts()

    avg_daily = daily_counts.mean()
    max_daily = daily_counts.max()
    std_daily = daily_counts.std()

    
    commit_score = normalize(avg_daily, 0, max_daily)
    last_commit = max(commit_dates)
    days_since = (datetime.now(timezone.utc) - last_commit).days
    recency_score = 100 * np.exp(-days_since / 30)
    contrib_df = pd.DataFrame(contributors)

    if contrib_df.empty or len(contrib_df) == 0:
        
        contributor_score = 0
        top_contributor_pct = 0
    else:
        total = contrib_df["contributions"].sum()
        contrib_df["pct"] = contrib_df["contributions"] / total * 100

        top_contributor_pct = contrib_df.iloc[0]["pct"]

        contributor_score = max(0, 100 - top_contributor_pct)

    merge_times = []
    avg_merge = 0

    for pr in prs:
        if pr.get("merged_at"):
            created = pd.to_datetime(pr["created_at"])
            merged = pd.to_datetime(pr["merged_at"])
            diff = (merged - created).total_seconds() / 3600
            merge_times.append(diff)

    if merge_times:
        avg_merge = np.mean(merge_times)

        pr_score = normalize(avg_merge, min(merge_times), max(merge_times))
        pr_score = 100 - pr_score 
    else:
        pr_score = 50

    open_issues = sum(1 for i in issues if i["state"] == "open")
    closed_issues = sum(1 for i in issues if i["state"] == "closed")

    total_issues = open_issues + closed_issues

    if total_issues > 0:
        close_rate = (closed_issues / total_issues) * 100
    else:
        close_rate = 0

    backlog_penalty = min(open_issues * 0.5, 50)

    issue_score = max(0, close_rate - backlog_penalty)

    scores = [
        commit_score,
        recency_score,
        contributor_score,
        pr_score,
        issue_score
    ]

    final_score = round(np.mean(scores), 2)

    if final_score >= 75:
        status = "Healthy"
    elif final_score >= 50:
        status = "Moderate"
    else:
        status = "Risky"

    dimension_scores = {
        "commit_frequency": round(commit_score, 2),
        "recency": round(recency_score, 2),
        "contributors": round(contributor_score, 2),
        "pr_speed": round(pr_score, 2),
        "issues": round(issue_score, 2)
    }

    health_distribution = {
        "maintenance": round(commit_score / 5, 2),
        "stability": round(recency_score / 5, 2),
        "contributors": round(contributor_score / 5, 2),
        "security": round(issue_score / 5, 2),
        "efficiency": round(pr_score / 5, 2)
    }

    risks = []

    if top_contributor_pct > 70:
        risks.append({
            "name": "High contributor dependency",
            "status": "high"
        })

    if close_rate < 50:
        risks.append({
            "name": "Low issue resolution rate",
            "status": "medium"
        })

    if avg_merge > 72:
        risks.append({
            "name": "Slow PR merges",
            "status": "medium"
        })

    if days_since > 30:
        risks.append({
            "name": "Inactive repository",
            "status": "high"
        })

    # Create timeline data
    df["month"] = df["date"].dt.to_period("M")
    monthly_commits = df.groupby("month").size()

    timeline = []
    for m, count in monthly_commits.items():
        timeline.append({"month": str(m), "commits": int(count)})

    # Group issues and PRs by month
    issues_opened = {}
    issues_closed = {}
    prs_merged = {}
    
    for issue in issues:
        try:
            if issue.get("created_at"):
                month = pd.to_datetime(issue["created_at"]).strftime("%b")
                issues_opened[month] = issues_opened.get(month, 0) + 1
            if issue.get("closed_at"):
                month = pd.to_datetime(issue["closed_at"]).strftime("%b")
                issues_closed[month] = issues_closed.get(month, 0) + 1
        except:
            continue
    
    for pr in prs:
        try:
            if pr.get("merged_at"):
                month = pd.to_datetime(pr["merged_at"]).strftime("%b")
                prs_merged[month] = prs_merged.get(month, 0) + 1
        except:
            continue

    issue_pr_stats = {
        "opened": issues_opened,
        "closed": issues_closed,
        "merged": prs_merged
    }
    num_cells = 25
    heatmap = []

    for i in range(num_cells):
        if i < num_cells * 0.5:
            cell_status = "current"
        elif i < num_cells * 0.7:
            cell_status = "patch"
        elif i < num_cells * 0.9:
            cell_status = "minor"
        else:
            cell_status = "major"
        heatmap.append(cell_status)
    num_cells = 25
    recent = df[df["date"] > (datetime.now(timezone.utc) - pd.Timedelta(days=30))]
    older = df[df["date"] <= (datetime.now(timezone.utc) - pd.Timedelta(days=30))]

    recent_rate = len(recent)
    older_rate = len(older)

    if recent_rate > older_rate * 1.5:
        phase = "Growth"
    elif recent_rate < older_rate * 0.5:
        phase = "Decline"
    elif days_since > 30:
        phase = "Inactive"
    else:
        phase = "Stable"

    top_contributors = contrib_df.head(5)

    workload = []

    if not top_contributors.empty:
        for _, row in top_contributors.iterrows():
            workload.append({
                "name": row["login"],
                "commits": int(row["contributions"]),
                "percentage": round(row["pct"], 2)
            })

    return {
        "score": final_score,
        "status": status,
        "dependency_heatmap": heatmap,
        "workload": workload,
        "phase": phase,

        "summary": {
            "last_commit_days": days_since,
            "contributors": len(contributors),
            "issue_close_rate": round(close_rate, 2),
            "avg_pr_merge_time": round(avg_merge, 2)
        },

        "dimension_scores": dimension_scores,
        "health_distribution": health_distribution,
        "risk_signals": risks,
        "timeline": timeline,
        "issue_pr_stats": issue_pr_stats
    }