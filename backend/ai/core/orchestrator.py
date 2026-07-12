"""
AI Orchestrator — the central coordination layer for all intelligent repository analysis.

Responsibilities:
- Accept a user question + optional dashboard snapshot (or synthesize one)
- Run the Structured Intelligence Layer
- Decide which widgets, metrics, and prior conversation turns are relevant
- Assemble a complete AIContextPackage
- Coordinate with Session Memory
- Prepare the final prompt sections for Gemini

This is the component that turns "just another chatbot" into a true
GitIntel Repository Intelligence Analyst.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from ai.core.models import (
    AIContextPackage,
    DashboardSnapshot,
    StructuredInsights,
    ConversationTurn,
    SessionContext,
)
from ai.core.snapshot import synthesize_snapshot_from_analytics
from ai.core.intelligence import compute_structured_insights
from ai.memory.session_memory import session_store

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Production orchestrator for the new AI architecture.

    Usage (typical flow inside ask_repository_question_ai or new endpoints):
        orchestrator = AIOrchestrator()
        package = orchestrator.build_context_package(
            owner=owner,
            repo=repo,
            user_question=question,
            health_data=...,
            contributor_data=...,
            risk_data=...,
            session_id=client_provided_or_generated_id,
        )
        prompt = orchestrator.render_prompt(package)
        answer = llm_service.generate_llm_response(...)
        orchestrator.record_turn(session_id, package, answer)
    """

    def __init__(self):
        self._relevant_widget_keywords = {
            "lorenz": ["lorenz_curve", "contribution", "inequality", "gini", "distribution"],
            "bus": ["bus_factor", "concentration", "single point", "dependency"],
            "pr": ["pr_backlog", "pull request", "review", "merge"],
            "issue": ["issue_backlog", "issue", "backlog"],
            "health": ["health", "score", "overall"],
            "activity": ["activity", "trend", "commit", "velocity"],
            "contributor": ["contributor", "top", "participation"],
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_context_package(
        self,
        owner: str,
        repo: str,
        user_question: str,
        health_data: Optional[Dict[str, Any]] = None,
        contributor_data: Optional[Dict[str, Any]] = None,
        risk_data: Optional[Dict[str, Any]] = None,
        evolution_data: Optional[Dict[str, Any]] = None,
        repo_metadata: Optional[Dict[str, Any]] = None,
        frontend_snapshot: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        page: str = "overview",
    ) -> AIContextPackage:
        """
        The main entry point. Produces a fully populated AIContextPackage.
        """

        # 1. Snapshot: prefer frontend if provided, otherwise synthesize
        snapshot = None
        if frontend_snapshot:
            # Check if it has a complete DashboardSnapshot signature
            if "repository" in frontend_snapshot and "widget_data" in frontend_snapshot:
                try:
                    snapshot = DashboardSnapshot(**frontend_snapshot)
                except Exception as exc:
                    logger.warning("Invalid full frontend snapshot structure: %s", exc)
            
            # If not a complete/valid full snapshot, treat as lightweight metadata
            if not snapshot:
                page_val = frontend_snapshot.get("activeTab") or frontend_snapshot.get("activePage") or frontend_snapshot.get("page") or page
                snapshot = synthesize_snapshot_from_analytics(
                    owner, repo, health_data, contributor_data, risk_data, evolution_data, page=page_val
                )
                # Store all extra lightweight metadata in active_filters
                for k, v in frontend_snapshot.items():
                    if k not in ("page", "activeTab", "activePage", "repository"):
                        snapshot.active_filters[k] = v
        else:
            snapshot = synthesize_snapshot_from_analytics(
                owner, repo, health_data, contributor_data, risk_data, evolution_data, page=page
            )

        # 2. Structured insights (the "analytical brain")
        insights = compute_structured_insights(
            health_data=health_data,
            contributor_data=contributor_data,
            risk_data=risk_data,
            dashboard_snapshot=snapshot,
        )

        # 3. Relevance filtering
        relevant_metrics = self._select_relevant_metrics(user_question, snapshot, insights)
        relevant_widgets = self._select_relevant_widgets(user_question, snapshot)

        # Attach relevance decisions into the snapshot for prompt transparency
        snapshot.active_filters["orchestrator_selected_widgets"] = relevant_widgets

        # 4. Session memory
        history: List[Dict[str, Any]] = []
        if session_id:
            session = session_store.get_or_create(session_id, f"{owner}/{repo}")
            history = [turn.model_dump() for turn in session.turns[-4:]]  # last 4 turns

        # Compute the compact context summary
        from ai.services.context_builder import build_compact_analysis_summary
        repo_context_summary = build_compact_analysis_summary(
            health_data=health_data,
            contributor_data=contributor_data,
            risk_data=risk_data,
            evolution_data=evolution_data,
            repo_metadata=repo_metadata,
        )

        package = AIContextPackage(
            user_question=user_question,
            dashboard_snapshot=snapshot,
            structured_insights=insights,
            relevant_metrics=relevant_metrics,
            conversation_history=history,
            repository=f"{owner}/{repo}",
            owner=owner,
            repo_context_summary=repo_context_summary,
        )

        logger.info("Orchestrator built context package for %s/%s (session=%s)", owner, repo, session_id)
        return package

    def render_prompt(self, package: AIContextPackage) -> str:
        """
        Produces the final user-side prompt string using the new structured format.

        The actual system prompt lives in prompts/system/analyst.txt.
        This method only builds the CONTEXT + USER sections.
        """
        lines: List[str] = []

        # --- ROLE & INSTRUCTIONS ---
        lines.append("=== ROLE & INSTRUCTIONS ===")
        lines.append(
            "You are the GitIntel Repository Intelligence Analyst — an expert AI system specialized in "
            "interpreting GitHub repository health, contributor dynamics, risk signals, and long-term project sustainability.\n"
            "Rules:\n"
            "- Ground every answer in the Repository Analysis Context and Current UI View State provided below.\n"
            "- Reference specific metrics, values, and filenames where available.\n"
            "- Distinguish between hard numbers and logical implications.\n"
            "- End substantive answers with 1-2 concrete, actionable recommendations."
        )
        lines.append("")

        # --- REPOSITORY ANALYSIS CONTEXT ---
        lines.append("=== REPOSITORY ANALYSIS CONTEXT ===")
        if package.repo_context_summary:
            lines.append(package.repo_context_summary)
        else:
            lines.append("- No detailed repository metrics context available.")
        lines.append("")

        # --- CURRENT UI VIEW STATE ---
        lines.append("=== CURRENT UI VIEW STATE ===")
        if package.dashboard_snapshot:
            snap = package.dashboard_snapshot
            lines.append(f"- Active Page/Tab: {snap.page}")
            if snap.active_filters:
                for k, v in snap.active_filters.items():
                    if v is not None:
                        formatted_key = k.replace("_", " ")
                        if formatted_key and formatted_key[0].islower():
                            formatted_key = formatted_key.title()
                        lines.append(f"- {formatted_key}: {v}")
            else:
                lines.append("- No active filters or selected items.")
        else:
            lines.append("- No active UI snapshot state.")
        lines.append("")

        # --- CONVERSATION HISTORY ---
        lines.append("=== CONVERSATION HISTORY ===")
        if package.conversation_history:
            for turn in package.conversation_history[-3:]:
                lines.append(f"Q: {turn.get('question', '')}")
                lines.append(f"A (summary): {turn.get('answer_summary', '')}")
        else:
            lines.append("- No prior history in this chat session.")
        lines.append("")

        # --- CURRENT USER QUESTION ---
        lines.append("=== CURRENT USER QUESTION ===")
        lines.append(package.user_question)

        return "\n".join(lines)

    def record_turn(
        self,
        session_id: Optional[str],
        package: AIContextPackage,
        full_answer: str,
    ) -> None:
        """Store this exchange in session memory for future context."""
        if not session_id:
            return

        session = session_store.get_or_create(session_id, package.repository)

        # Create a compact summary for memory
        summary = self._create_turn_summary(package, full_answer)

        turn = ConversationTurn(
            question=package.user_question,
            answer_summary=summary,
            referenced_widgets=package.dashboard_snapshot.visible_widgets if package.dashboard_snapshot else [],
            key_insights=package.structured_insights.key_risks + package.structured_insights.key_strengths,
        )

        session.turns.append(turn)
        session.last_active = turn.timestamp
        session.accumulated_insights.extend(turn.key_insights)
        # Keep memory bounded
        if len(session.turns) > 12:
            session.turns = session.turns[-8:]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _select_relevant_widgets(self, question: str, snapshot: DashboardSnapshot) -> List[str]:
        q_lower = question.lower()
        selected = []
        for widget_id in snapshot.visible_widgets:
            keywords = self._relevant_widget_keywords.get(widget_id.split("_")[0], [])
            if any(kw in q_lower for kw in keywords) or widget_id in q_lower:
                selected.append(widget_id)
        # If nothing matched, return all visible widgets (conservative)
        return selected or snapshot.visible_widgets

    def _select_relevant_metrics(self, question: str, snapshot: DashboardSnapshot, insights: StructuredInsights) -> Dict[str, Any]:
        q = question.lower()
        out: Dict[str, Any] = {}

        if any(k in q for k in ["health", "score", "overall"]):
            out["health_score"] = snapshot.metrics.get("health_score")
        if any(k in q for k in ["bus", "concentrat", "contributor"]):
            out.update(snapshot.contributor_stats)
        if any(k in q for k in ["risk", "danger", "problem"]):
            out["key_risks"] = insights.key_risks
        if any(k in q for k in ["trend", "activity", "velocity"]):
            out["activity_trend"] = insights.activity_trend
        return out or snapshot.metrics

    def _summarize_widget_data(self, data: Dict[str, Any]) -> str:
        if not data:
            return ""
        # Keep it short for token budget
        items = []
        for k, v in list(data.items())[:5]:
            if isinstance(v, (list, dict)) and len(str(v)) > 80:
                items.append(f"{k}=[...]")
            else:
                items.append(f"{k}={v}")
        return ", ".join(items)

    def _summarize_dict(self, d: Dict[str, Any]) -> str:
        return ", ".join(f"{k}={v}" for k, v in list(d.items())[:8])

    def _create_turn_summary(self, package: AIContextPackage, answer: str) -> str:
        # Very lightweight summary — in production this could be another small LLM call
        ins = package.structured_insights
        return f"Health={ins.overall_health_signal}, Concentration={ins.contributor_concentration}, Trend={ins.activity_trend}. " + answer[:160]
