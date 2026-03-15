import pandas as pd
from typing import List, Dict


def analyze_commits(commits: List[Dict]) -> Dict:
    if not commits:
        return {"dates": [], "counts": [], "total_commits": 0}

    commit_dates = []
    for commit in commits:
        try:
            timestamp = commit['commit']['author']['date']
            commit_dates.append(timestamp)
        except (KeyError, TypeError):
            continue

    if not commit_dates:
        return {"dates": [], "counts": [], "total_commits": 0}

    df = pd.DataFrame({'date': commit_dates})

    df['date'] = pd.to_datetime(df['date'])

    df['date'] = df['date'].dt.date

    # Count commits per day
    daily_counts = df['date'].value_counts().sort_index()

    # Convert to lists for JSON response
    dates = [str(date) for date in daily_counts.index]
    counts = daily_counts.values.tolist()
    daily_df = pd.DataFrame({"date": dates,"count": counts})

    daily_df["date"] = pd.to_datetime(daily_df["date"])
    avg_commits_per_day = daily_df["count"].mean()
    std_dev_commits = daily_df["count"].std()

    most_active_row = daily_df.loc[daily_df["count"].idxmax()]
    most_active_day = {"date": str(most_active_row["date"].date()),"commits": int(most_active_row["count"])}

    daily_df["weekday"] = daily_df["date"].dt.day_name()

    weekday_distribution = (daily_df.groupby("weekday")["count"]
    .sum()
    .reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
    .fillna(0)
    .astype(int)
    .to_dict()
)

    return {
    "dates": dates,
    "counts": counts,
    "total_commits": len(commit_dates),
    "summary": {
        "avg_commits_per_day": round(avg_commits_per_day, 2),
        "std_dev_commits": round(std_dev_commits, 2),
        "most_active_day": most_active_day,
        "weekday_distribution": weekday_distribution
    }
}