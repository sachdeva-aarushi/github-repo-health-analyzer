import pandas as pd
from typing import List, Dict


def analyze_commits(commits: List[Dict]) -> Dict:
    """
    Analyze commit data and convert timestamps into daily commit counts.

    Args:
        commits: List of commit data from GitHub API

    Returns:
        Dictionary with dates and commit counts suitable for charting

    Raises:
        ValueError: If commits list is empty or data format is unexpected
    """
    if not commits:
        return {"dates": [], "counts": [], "total_commits": 0}

    # Extract commit dates from the API response
    commit_dates = []
    for commit in commits:
        try:
            timestamp = commit['commit']['author']['date']
            commit_dates.append(timestamp)
        except (KeyError, TypeError):
            # Skip commits with missing author/date info
            continue

    if not commit_dates:
        return {"dates": [], "counts": [], "total_commits": 0}

    # Create a DataFrame with the dates
    df = pd.DataFrame({'date': commit_dates})

    # Convert to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Extract just the date (remove time)
    df['date'] = df['date'].dt.date

    # Count commits per day
    daily_counts = df['date'].value_counts().sort_index()

    # Convert to lists for JSON response
    dates = [str(date) for date in daily_counts.index]
    counts = daily_counts.values.tolist()

    return {
        "dates": dates,
        "counts": counts,
        "total_commits": len(commit_dates),
    }
