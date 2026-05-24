"""
Dashboard Snapshot Engine.

Responsible for constructing a complete, structured DashboardSnapshot for every AI request.

Two modes of operation:
1. Synthesis mode (current reality): Build a high-fidelity snapshot purely from backend analytics.
2. Hydration mode (future): Merge/validate a snapshot sent by the frontend.

The goal is that the AI layer is NEVER without dashboard context again.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from ai.core.models import DashboardSnapshot, WidgetSnapshot
from ai.core.widget_registry import widget_registry


def synthesize_snapshot_from_analytics(
    owner: str,
    repo: str,
    health_data: Optional[Dict[str, Any]] = None,
    contributor_data: Optional[Dict[str, Any]] = None,
    risk_data: Optional[Dict[str, Any]] = None,
    evolution_data: Optional[Dict[str, Any]] = None,
    page: str = "overview",
    date_range: str = "all",
) -> DashboardSnapshot:
    """
    Build a DashboardSnapshot entirely from existing deterministic analyzer outputs.

    This is the critical bridge that gives the new AI architecture immediate
    awareness of charts/metrics even before the frontend sends snapshot data.
    """
    repository = f"{owner}/{repo}"

    visible_widgets: list[str] = []
    widget_data: dict[str, WidgetSnapshot] = {}
    metrics: dict[str, Any] = {}
    contributor_stats: dict[str, Any] = {}
    repository_analytics: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Health & overall metrics
    # ------------------------------------------------------------------
    if health_data:
        metrics["health_score"] = health_data.get("score")
        metrics["health_status"] = health_data.get("status")
        metrics["dimension_scores"] = health_data.get("dimension_scores", {})
        visible_widgets.append("health_score")

        # Create a synthetic health widget snapshot
        widget_data["health_score"] = widget_registry.build_widget_snapshot(
            "health_score",
            {
                "score": health_data.get("score"),
                "status": health_data.get("status"),
                "dimensions": health_data.get("dimension_scores", {}),
            },
            {"source": "health_analysis"},
        )

        if "risk_signals" in health_data:
            visible_widgets.append("risk_summary")
            widget_data["risk_summary"] = widget_registry.build_widget_snapshot(
                "risk_summary",
                {"risks": health_data.get("risk_signals", [])},
                {"source": "health_analysis"},
            )

    # ------------------------------------------------------------------
    # Contributor / Lorenz / Bus Factor
    # ------------------------------------------------------------------
    if contributor_data:
        contributor_stats = {
            "total_contributors": len(contributor_data.get("contributors", [])),
            "top_contributor_percentage": contributor_data.get("top_contributor_percentage"),
            "bus_factor": contributor_data.get("bus_factor"),
        }

        # Lorenz curve widget
        if "lorenz_curve" in contributor_data:
            visible_widgets.append("lorenz_curve")
            lorenz_data = {
                "points": contributor_data["lorenz_curve"],
                "top_contributor_share": contributor_data.get("top_contributor_percentage"),
                "bus_factor": contributor_data.get("bus_factor"),
            }
            widget_data["lorenz_curve"] = widget_registry.build_widget_snapshot(
                "lorenz_curve", lorenz_data, {"source": "contributor_analysis"}
            )

        # Top contributors
        visible_widgets.append("top_contributors")
        widget_data["top_contributors"] = widget_registry.build_widget_snapshot(
            "top_contributors",
            {"contributors": contributor_data.get("contributors", [])[:10]},
            {"source": "contributor_analysis"},
        )

        # Bus factor explicit widget
        visible_widgets.append("bus_factor")
        widget_data["bus_factor"] = widget_registry.build_widget_snapshot(
            "bus_factor",
            {
                "bus_factor": contributor_data.get("bus_factor"),
                "top_share": contributor_data.get("top_contributor_percentage"),
            },
            {"source": "contributor_analysis"},
        )

    # ------------------------------------------------------------------
    # Risk data (PR backlog, issues, trends)
    # ------------------------------------------------------------------
    if risk_data:
        pr_risk = risk_data.get("pr_risk", {})
        if pr_risk:
            visible_widgets.append("pr_backlog")
            widget_data["pr_backlog"] = widget_registry.build_widget_snapshot(
                "pr_backlog",
                {
                    "open_prs": pr_risk.get("open_prs"),
                    "merge_ratio": pr_risk.get("merge_ratio"),
                    "insights": pr_risk.get("insights", []),
                },
                {"source": "risk_analysis"},
            )

        issue_risk = risk_data.get("issue_risk", {})
        if issue_risk:
            visible_widgets.append("issue_backlog")
            widget_data["issue_backlog"] = widget_registry.build_widget_snapshot(
                "issue_backlog",
                {
                    "open_issues": issue_risk.get("open_issues"),
                    "close_ratio": issue_risk.get("close_ratio"),
                    "insights": issue_risk.get("insights", []),
                },
                {"source": "risk_analysis"},
            )

        # Activity trend from risk summary if present
        if "trend" in risk_data.get("summary", {}):
            visible_widgets.append("activity_trend")
            widget_data["activity_trend"] = widget_registry.build_widget_snapshot(
                "activity_trend",
                {"trend": risk_data["summary"]["trend"]},
                {"source": "risk_analysis"},
            )

    # ------------------------------------------------------------------
    # Evolution / structure data
    # ------------------------------------------------------------------
    if evolution_data:
        repository_analytics = {
            "stars": evolution_data.get("stars"),
            "forks": evolution_data.get("forks"),
            "total_files": evolution_data.get("total_files"),
            "total_pull_requests": evolution_data.get("total_pull_requests"),
            "total_issues": evolution_data.get("total_issues"),
            "tech_stack": evolution_data.get("tech_stack", []),
        }

    # Deduplicate while preserving order
    seen = set()
    visible_widgets = [w for w in visible_widgets if not (w in seen or seen.add(w))]

    return DashboardSnapshot(
        page=page,
        repository=repository,
        date_range=date_range,
        visible_widgets=visible_widgets,  # type: ignore[arg-type]
        widget_data=widget_data,
        metrics=metrics,
        contributor_stats=contributor_stats,
        repository_analytics=repository_analytics,
    )


def hydrate_snapshot(
    raw_frontend_snapshot: Dict[str, Any],
    fallback_analytics: Optional[Dict[str, Any]] = None,
) -> DashboardSnapshot:
    """
    Future entry point: when the frontend starts sending dashboard context,
    this method will validate, enrich, and normalize it.

    For now it simply converts a raw dict into our typed model and
    fills gaps using synthesized data if needed.
    """
    # Basic passthrough for now — in the future we will deeply merge
    # with synthesized data and run validation against the widget registry.
    try:
        return DashboardSnapshot(**raw_frontend_snapshot)
    except Exception:
        # If the frontend payload is malformed, fall back to synthesis
        if fallback_analytics:
            return synthesize_snapshot_from_analytics(**fallback_analytics)
        raise
