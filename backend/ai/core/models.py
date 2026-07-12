"""
Core data models for the new GitIntel AI architecture.

These Pydantic models define the contract between:
- Dashboard Snapshot Engine
- Widget Registry
- Structured Intelligence Layer
- AI Orchestrator
- Future RAG sources

All new AI flows should use these types instead of raw dicts.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# -----------------------------------------------------------------------------
# Widget & Dashboard Snapshot Models
# -----------------------------------------------------------------------------

WidgetId = Literal[
    "lorenz_curve",
    "activity_trend",
    "top_contributors",
    "health_score",
    "risk_summary",
    "pr_backlog",
    "issue_backlog",
    "bus_factor",
    "contribution_heatmap",
    "review_velocity",
]


class WidgetSnapshot(BaseModel):
    """
    Structured representation of a single visible dashboard widget.
    The AI receives both raw data and explicit analytical meaning.
    """
    id: WidgetId
    title: str
    description: str = Field(..., description="Human-readable purpose of the widget")
    analytical_meaning: str = Field(..., description="What this widget reveals about the repository")
    data: Dict[str, Any] = Field(default_factory=dict, description="Raw widget values (Gini, points, counts, etc.)")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DashboardSnapshot(BaseModel):
    """
    Complete context of what the user is currently looking at in the UI.

    This is the primary mechanism that solves "AI not aware of dashboard context".
    Every AI request should carry (or have synthesized) a DashboardSnapshot.
    """
    page: str = Field(..., description="Current active page/tab in the dashboard")
    repository: str = Field(..., description="Full repository name (owner/repo)")
    date_range: str = Field(default="all", description="Selected time window (e.g. 30d, 90d, all)")
    active_filters: Dict[str, Any] = Field(default_factory=dict)
    visible_widgets: List[WidgetId] = Field(default_factory=list)
    widget_data: Dict[str, WidgetSnapshot] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Top-level KPI values")
    contributor_stats: Dict[str, Any] = Field(default_factory=dict)
    repository_analytics: Dict[str, Any] = Field(default_factory=dict)
    snapshot_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# -----------------------------------------------------------------------------
# Structured Intelligence Layer Outputs
# -----------------------------------------------------------------------------

class StructuredInsights(BaseModel):
    """
    Pre-computed analytical conclusions.

    Gemini should narrate these, not rediscover them.
    This layer turns raw numbers into repository health signals.
    """
    contributor_concentration: Literal["high", "medium", "low"] = "medium"
    contribution_inequality: float = Field(0.0, ge=0.0, le=1.0, description="Approximate Gini coefficient or top-share ratio")
    bus_factor_risk: Literal["critical", "high", "medium", "low"] = "medium"
    activity_trend: Literal["accelerating", "stable", "declining", "sporadic"] = "stable"
    review_bottleneck_risk: Literal["high", "medium", "low"] = "medium"
    issue_backlog_risk: Literal["high", "medium", "low"] = "medium"
    participation_distribution: Literal["concentrated", "balanced", "fragmented"] = "balanced"
    growth_indicator: Literal["growing", "flat", "shrinking"] = "flat"
    overall_health_signal: Literal["healthy", "moderate", "at_risk"] = "moderate"
    key_risks: List[str] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    computed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# -----------------------------------------------------------------------------
# AI Orchestration Context Package
# -----------------------------------------------------------------------------

class AIContextPackage(BaseModel):
    """
    The single source of truth passed to the prompt builder / Gemini.

    The orchestrator is responsible for populating this object.
    """
    user_question: str
    dashboard_snapshot: Optional[DashboardSnapshot] = None
    structured_insights: StructuredInsights
    relevant_metrics: Dict[str, Any] = Field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="Prior turns in this session")
    repository: str
    owner: str
    repo_context_summary: Optional[str] = None



# -----------------------------------------------------------------------------
# Future RAG / Retrieval Abstraction (interfaces only — not implemented)
# -----------------------------------------------------------------------------

class RetrievalSource(BaseModel):
    """
    Placeholder for future retrieval-augmented sources.
    Each source will be responsible for returning relevant text chunks
    (issues, PR discussions, commit messages, docs, etc.).
    """
    source_type: Literal["issues", "prs", "commits", "docs", "vector"] = "issues"
    query: str
    top_k: int = 5
    results: List[Dict[str, Any]] = Field(default_factory=list)


class RetrievalContext(BaseModel):
    """Container for all retrieval results that can be injected into context."""
    sources: List[RetrievalSource] = Field(default_factory=list)
    retrieval_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# -----------------------------------------------------------------------------
# Session Memory Record
# -----------------------------------------------------------------------------

class ConversationTurn(BaseModel):
    """Single exchange stored in session memory."""
    question: str
    answer_summary: str   # short, structured summary for memory (not full text)
    referenced_widgets: List[str] = Field(default_factory=list)
    key_insights: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SessionContext(BaseModel):
    """In-memory conversation state for a single user session."""
    session_id: str
    repository: str
    turns: List[ConversationTurn] = Field(default_factory=list)
    last_active: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    accumulated_insights: List[str] = Field(default_factory=list)
