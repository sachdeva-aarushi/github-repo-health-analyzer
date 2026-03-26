import numpy as np
import pandas as pd
from datetime import datetime


def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 50
    return max(0, min(100, (value - min_val) / (max_val - min_val) * 100))


def analyze_health(commits, contributors, prs, issues):

    # =========================
    # 1. COMMIT ACTIVITY
    # =========================
    commit_dates = []

    for c in commits:
        try:
            date = c["commit"]["author"]["date"]
            commit_dates.append(pd.to_datetime(date))
        except:
            continue

    if not commit_dates:
        return {}

    df = pd.DataFrame({"date": commit_dates})

    daily_counts = df["date"].dt.date.value_counts()

    avg_daily = daily_counts.mean()
    max_daily = daily_counts.max()
    std_daily = daily_counts.std()

    # normalized relative to repo behavior
    commit_score = normalize(avg_daily, 0, max_daily)


    # =========================
    # 2. RECENCY (DECAY MODEL)
    # =========================
    last_commit = max(commit_dates)
    days_since = (datetime.utcnow() - last_commit).days

    # exponential decay instead of linear penalty
    recency_score = 100 * np.exp(-days_since / 30)


    # =========================
    # 3. CONTRIBUTORS (INEQUALITY BASED)
    # =========================
    contrib_df = pd.DataFrame(contributors)

    total = contrib_df["contributions"].sum()
    contrib_df["pct"] = contrib_df["contributions"] / total * 100

    # inequality measure
    top_contributor_pct = contrib_df.iloc[0]["pct"]

    contributor_score = max(0, 100 - top_contributor_pct)


    # =========================
    # 4. PR MERGE SPEED
    # =========================
    merge_times = []

    for pr in prs:
        if pr.get("merged_at"):
            created = pd.to_datetime(pr["created_at"])
            merged = pd.to_datetime(pr["merged_at"])
            diff = (merged - created).total_seconds() / 3600
            merge_times.append(diff)

    if merge_times:
        avg_merge = np.mean(merge_times)

        # normalize within observed range
        pr_score = normalize(avg_merge, min(merge_times), max(merge_times))
        pr_score = 100 - pr_score  # lower time = better
    else:
        avg_merge = 0
        pr_score = 50


    # =========================
    # 5. ISSUE HEALTH
    # =========================
    open_issues = sum(1 for i in issues if i["state"] == "open")
    closed_issues = sum(1 for i in issues if i["state"] == "closed")

    total_issues = open_issues + closed_issues

    if total_issues > 0:
        close_rate = (closed_issues / total_issues) * 100
    else:
        close_rate = 0

    # penalize backlog
    backlog_penalty = min(open_issues * 0.5, 50)

    issue_score = max(0, close_rate - backlog_penalty)


    # =========================
    # FINAL SCORE (BALANCED)
    # =========================
    scores = [
        commit_score,
        recency_score,
        contributor_score,
        pr_score,
        issue_score
    ]

    final_score = round(np.mean(scores), 2)


    # =========================
    # STATUS
    # =========================
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


    return {
        "score": final_score,
        "status": status,

        "summary": {
            "last_commit_days": days_since,
            "contributors": len(contributors),
            "issue_close_rate": round(close_rate, 2),
            "avg_pr_merge_time": round(avg_merge, 2)
        },

        "dimension_scores": dimension_scores,
        "health_distribution": health_distribution,
        "risk_signals": risks
    }