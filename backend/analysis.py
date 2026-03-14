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
def analyze_contributors(contributors_data):
    df = pd.DataFrame(contributors_data)

    df = df[["login", "contributions"]]
    df = df.sort_values(by="contributions", ascending=False)

    total_commits = df["contributions"].sum()

    df["percentage"] = (df["contributions"] / total_commits) * 100

    top_contributor_pct = df.iloc[0]["percentage"]

    # Bus factor: contributors needed to reach 50% of commits
    cumulative = df["percentage"].cumsum()
    bus_factor = (cumulative < 50).sum() + 1

    # Sort contributors from lowest to highest for Lorenz curve
    lorenz_df = df.sort_values(by="percentage")

    # Cumulative share of contributors
    lorenz_df["cumulative_contributors"] = (
        range(1, len(lorenz_df) + 1)
    )

    lorenz_df["cumulative_contributors_pct"] = (
        lorenz_df["cumulative_contributors"] / len(lorenz_df) * 100
    )

    # Cumulative share of commits
    lorenz_df["cumulative_share"] = lorenz_df["percentage"].cumsum()
    return {
    "contributors": df.to_dict(orient="records"),
    "top_contributor_percentage": round(top_contributor_pct, 2),
    "bus_factor": int(bus_factor),
    "lorenz_curve": lorenz_df[[
        "cumulative_contributors_pct",
        "cumulative_share"
    ]].to_dict(orient="records")
}

