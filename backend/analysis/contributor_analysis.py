import pandas as pd
from typing import List, Dict


def analyze_contributors(contributors_data: List[Dict]) -> Dict:
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

