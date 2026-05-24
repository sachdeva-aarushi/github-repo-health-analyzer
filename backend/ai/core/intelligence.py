"""
Structured Intelligence Layer.

This layer sits between raw analyzer outputs / dashboard snapshots and the LLM.

Its job is to compute higher-order repository health signals so that Gemini
narrates rather than performs first-principles discovery.

All functions here are deterministic and versioned. They are the "analytical brain"
that makes the AI feel like a true repository intelligence analyst.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from ai.core.models import StructuredInsights, DashboardSnapshot


def compute_structured_insights(
    health_data: Optional[Dict[str, Any]] = None,
    contributor_data: Optional[Dict[str, Any]] = None,
    risk_data: Optional[Dict[str, Any]] = None,
    dashboard_snapshot: Optional[DashboardSnapshot] = None,
) -> StructuredInsights:
    """
    Main entry point. Produces a rich set of pre-computed analytical conclusions.
    """

    # Start with safe defaults
    insights = StructuredInsights()

    # ------------------------------------------------------------------
    # Contributor concentration & inequality
    # ------------------------------------------------------------------
    if contributor_data:
        top_pct = contributor_data.get("top_contributor_percentage", 0) or 0
        bus = contributor_data.get("bus_factor", 99)

        if top_pct >= 60 or bus <= 2:
            insights.contributor_concentration = "high"
            insights.contribution_inequality = min(top_pct / 100.0, 0.95)
            insights.bus_factor_risk = "critical" if bus <= 1 else "high"
            insights.participation_distribution = "concentrated"
        elif top_pct >= 35 or bus <= 4:
            insights.contributor_concentration = "medium"
            insights.contribution_inequality = min(top_pct / 100.0, 0.75)
            insights.bus_factor_risk = "medium"
            insights.participation_distribution = "balanced"
        else:
            insights.contributor_concentration = "low"
            insights.contribution_inequality = min(top_pct / 100.0, 0.55)
            insights.bus_factor_risk = "low"
            insights.participation_distribution = "balanced"

        # Lorenz / Gini approximation if we have the curve
        lorenz = contributor_data.get("lorenz_curve")
        if lorenz and len(lorenz) > 1:
            # Very rough Gini proxy from the last point
            last_point = lorenz[-1]
            if isinstance(last_point, dict):
                # cumulative_share is already a percentage
                gini_proxy = 1.0 - (last_point.get("cumulative_share", 100) / 100.0)
                insights.contribution_inequality = round(max(0.1, min(gini_proxy, 0.95)), 3)

    # ------------------------------------------------------------------
    # Activity trend
    # ------------------------------------------------------------------
    if risk_data and "trend" in risk_data.get("summary", {}):
        trend = risk_data["summary"]["trend"]
        desc = str(trend.get("value", "")).lower()
        if "drop" in desc or "declin" in desc:
            insights.activity_trend = "declining"
        elif "rising" in desc or "accelerat" in desc:
            insights.activity_trend = "accelerating"
        else:
            insights.activity_trend = "stable"

    # ------------------------------------------------------------------
    # Review & issue bottlenecks
    # ------------------------------------------------------------------
    if risk_data:
        pr = risk_data.get("pr_risk", {})
        if pr.get("level") == "HIGH" or pr.get("open_prs", 0) > 100:
            insights.review_bottleneck_risk = "high"
        elif pr.get("level") == "MEDIUM":
            insights.review_bottleneck_risk = "medium"
        else:
            insights.review_bottleneck_risk = "low"

        issue = risk_data.get("issue_risk", {})
        if issue.get("level") == "HIGH" or issue.get("open_issues", 0) > 200:
            insights.issue_backlog_risk = "high"
        elif issue.get("level") == "MEDIUM":
            insights.issue_backlog_risk = "medium"
        else:
            insights.issue_backlog_risk = "low"

    # ------------------------------------------------------------------
    # Overall health signal (simple but effective)
    # ------------------------------------------------------------------
    health_score = 50
    if health_data:
        health_score = health_data.get("score", 50)

    if health_score >= 75:
        insights.overall_health_signal = "healthy"
    elif health_score >= 50:
        insights.overall_health_signal = "moderate"
    else:
        insights.overall_health_signal = "at_risk"

    # ------------------------------------------------------------------
    # Key risks & strengths (derived)
    # ------------------------------------------------------------------
    risks: List[str] = []
    strengths: List[str] = []

    if insights.bus_factor_risk in ("high", "critical"):
        risks.append("Extreme contributor concentration (bus factor risk)")
    if insights.review_bottleneck_risk == "high":
        risks.append("Severe PR review backlog")
    if insights.issue_backlog_risk == "high":
        risks.append("Growing issue backlog")
    if insights.activity_trend == "declining":
        risks.append("Declining development activity")

    if insights.contributor_concentration == "low":
        strengths.append("Healthy contributor distribution")
    if insights.activity_trend == "accelerating":
        strengths.append("Increasing development velocity")
    if health_score >= 70:
        strengths.append("Strong overall health metrics")

    insights.key_risks = risks
    insights.key_strengths = strengths

    # ------------------------------------------------------------------
    # Growth indicator (very lightweight for now)
    # ------------------------------------------------------------------
    if insights.activity_trend == "accelerating":
        insights.growth_indicator = "growing"
    elif insights.activity_trend == "declining":
        insights.growth_indicator = "shrinking"
    else:
        insights.growth_indicator = "flat"

    return insights
