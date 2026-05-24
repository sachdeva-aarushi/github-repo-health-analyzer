"""
Widget Registry — the single source of truth for all dashboard widgets.

Each widget declares:
- identifier
- human title
- description
- analytical meaning (what it tells the AI about the repo)
- schema hints for the data it carries

The registry is used by:
- Dashboard Snapshot Engine (to validate/normalize incoming snapshots)
- Structured Intelligence Layer (to know which signals to compute)
- AI Orchestrator (to decide relevance)

This design makes the system widget-aware and future-proof when new charts are added.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from ai.core.models import WidgetSnapshot, WidgetId


class WidgetRegistry:
    """
    Static registry of all known widgets.

    In a production system this could be loaded from a YAML/JSON config
    or even discovered via plugin system. For now it is explicit and versioned.
    """

    _REGISTRY: Dict[WidgetId, Dict[str, Any]] = {
        "lorenz_curve": {
            "title": "Contribution Distribution (Lorenz Curve)",
            "description": "Visualizes inequality in how commits are distributed across contributors.",
            "analytical_meaning": "High Gini or steep curve indicates a small number of contributors dominate the project (bus factor / concentration risk). Flat curve = healthy distribution.",
            "data_schema": {"gini_coefficient": "float", "points": "array", "top_contributor_share": "float"},
        },
        "activity_trend": {
            "title": "Commit Activity Trend",
            "description": "Shows commit volume over time (weekly/monthly).",
            "analytical_meaning": "Reveals whether development velocity is accelerating, stable, declining, or sporadic. Critical for predicting project health and contributor engagement.",
            "data_schema": {"timeline": "array", "trend_direction": "string"},
        },
        "top_contributors": {
            "title": "Top Contributors",
            "description": "Lists the most active contributors by commit count.",
            "analytical_meaning": "Directly informs bus factor, maintainer load, and single-point-of-failure risk. High top-1 share is a major red flag.",
            "data_schema": {"contributors": "array"},
        },
        "health_score": {
            "title": "Repository Health Score",
            "description": "Composite score (0-100) derived from multiple health dimensions.",
            "analytical_meaning": "Overall vitality indicator. Should be interpreted together with the underlying dimension scores and risk signals.",
            "data_schema": {"score": "int", "status": "string", "dimensions": "object"},
        },
        "risk_summary": {
            "title": "Risk Summary",
            "description": "Aggregated risk signals across bus factor, PR backlog, issues, responsiveness, etc.",
            "analytical_meaning": "Highlights the most pressing threats to long-term maintainability and community health.",
            "data_schema": {"risks": "array"},
        },
        "pr_backlog": {
            "title": "Pull Request Backlog & Velocity",
            "description": "Open PR count, merge ratio, and age distribution.",
            "analytical_meaning": "High open PRs or low merge rate indicate review bottlenecks, contributor frustration, or maintainer overload.",
            "data_schema": {"open_prs": "int", "merge_ratio": "float"},
        },
        "issue_backlog": {
            "title": "Issue Backlog & Resolution",
            "description": "Open issues, close rate, and backlog trend.",
            "analytical_meaning": "Reflects project responsiveness to the community and technical debt visibility.",
            "data_schema": {"open_issues": "int", "close_ratio": "float"},
        },
        "bus_factor": {
            "title": "Bus Factor",
            "description": "Minimum number of contributors needed to reach 50% of commits.",
            "analytical_meaning": "The canonical single-number measure of knowledge concentration risk. ≤2 is critical.",
            "data_schema": {"bus_factor": "int", "top_share": "float"},
        },
        "contribution_heatmap": {
            "title": "Contribution Heatmap",
            "description": "Temporal or file-level contribution intensity.",
            "analytical_meaning": "Shows where energy is focused (recent files, hot modules) and can surface hidden technical debt areas.",
            "data_schema": {"cells": "array"},
        },
        "review_velocity": {
            "title": "Review & Merge Velocity",
            "description": "Average time to first response, merge, and close.",
            "analytical_meaning": "Direct measure of project responsiveness and maintainer bandwidth.",
            "data_schema": {"avg_merge_hours": "float", "stale_prs": "int"},
        },
    }

    @classmethod
    def get_widget(cls, widget_id: WidgetId) -> Optional[Dict[str, Any]]:
        """Return the static definition for a widget."""
        return cls._REGISTRY.get(widget_id)

    @classmethod
    def get_all_widget_ids(cls) -> list[WidgetId]:
        return list(cls._REGISTRY.keys())

    @classmethod
    def build_widget_snapshot(
        cls,
        widget_id: WidgetId,
        raw_data: Dict[str, Any],
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> WidgetSnapshot:
        """
        Factory that creates a validated WidgetSnapshot from raw analyzer output.

        This is the preferred way to turn backend analytics into widget form.
        """
        definition = cls.get_widget(widget_id)
        if not definition:
            # Unknown widget — still allow it but mark it
            return WidgetSnapshot(
                id=widget_id,  # type: ignore[arg-type]
                title=widget_id.replace("_", " ").title(),
                description="Custom / unknown widget",
                analytical_meaning="This widget was not registered. Its meaning must be inferred from its data.",
                data=raw_data,
                metadata=extra_metadata or {},
            )

        return WidgetSnapshot(
            id=widget_id,
            title=definition["title"],
            description=definition["description"],
            analytical_meaning=definition["analytical_meaning"],
            data=raw_data,
            metadata=extra_metadata or {},
        )


# Convenience singleton for easy importing
widget_registry = WidgetRegistry()
