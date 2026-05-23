"""
AI-powered repository analysis orchestrator.

This is the main business logic service for AI narration.
It coordinates the flow:
    GitHub API → Deterministic Analyzers → Context Builder → LLM → Narrated Insights

RULES:
- All GitHub API fetches are grouped here (single point of fetch per request).
- Existing analyzers are called but NEVER modified.
- AI layer only interprets — it does not replace analytics.
- LLM calls go through llm_service (not directly to a provider).
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from services.github_service import (
    get_commits,
    get_contributors,
    get_pull_requests,
    get_issues,
    get_repo_metadata,
    get_repo_languages,
    get_repo_tree,
)
from analysis.health_analysis import analyze_health
from analysis.contributor_analysis import analyze_contributors
from analysis.risk_analysis import compute_risk
from analysis.evolution_analysis import summarize_repository, analyze_repo_structure, extract_tech_stack

from ai.services.context_builder import build_context
from ai.services.llm_service import generate_llm_response
from ai.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)

# System prompt establishes the AI's role and strict boundaries.
_SYSTEM_PROMPT = (
    "You are a senior software architect. "
    "You interpret structured repository analytics and narrate insights clearly. "
    "You do NOT have access to the raw source code. "
    "Base your analysis ONLY on the metrics provided. "
    "Be balanced, constructive, and actionable."
)


def analyze_repository_ai(owner: str, repo: str) -> Dict[str, Any]:
    """
    Perform AI-narrated analysis of a GitHub repository.

    Fetches raw data once, runs all deterministic analyzers, builds a
    compressed context, and asks the LLM to narrate the findings.

    Args:
        owner: Repository owner (GitHub username or org).
        repo: Repository name.

    Returns:
        Dict with keys: owner, repo, ai_summary, analysis_timestamp, model_used.

    Raises:
        ValueError: If the repository cannot be found or data is insufficient.
        RuntimeError: If the LLM call fails.
    """
    logger.info("Starting AI analysis for %s/%s", owner, repo)

    # ------------------------------------------------------------------
    # Step 1: Fetch all raw data in one place (no duplicate fetching).
    # ------------------------------------------------------------------
    try:
        commits = get_commits(owner, repo) or []
        contributors = get_contributors(owner, repo) or []
        pull_requests = get_pull_requests(owner, repo) or []
        issues = get_issues(owner, repo) or []
        repo_metadata = get_repo_metadata(owner, repo)
    except Exception as e:
        logger.error("Failed to fetch data for %s/%s: %s", owner, repo, e)
        raise ValueError(f"Could not fetch repository data for {owner}/{repo}: {e}")

    if not repo_metadata:
        raise ValueError(f"Repository {owner}/{repo} not found or is inaccessible.")

    # Fetch structure data separately — these are optional for the AI context.
    languages = {}
    structure = {"total_files": 0, "total_folders": 0}
    try:
        languages = get_repo_languages(owner, repo) or {}
        tree = get_repo_tree(owner, repo)
        structure = analyze_repo_structure(tree)
    except Exception:
        logger.warning("Could not fetch language/structure data for %s/%s", owner, repo)

    # ------------------------------------------------------------------
    # Step 2: Run deterministic analyzers (source of truth — untouched).
    # ------------------------------------------------------------------
    health_data = analyze_health(commits, contributors, pull_requests, issues)
    contributor_data = analyze_contributors(contributors) if contributors else {}
    risk_data = compute_risk(contributors, pull_requests, issues, commits)
    evolution_data = summarize_repository(
        metadata=repo_metadata,
        languages=languages,
        structure=structure,
        pull_requests=pull_requests,
        issues=issues,
    )

    # ------------------------------------------------------------------
    # Step 3: Build compressed AI context from analyzer outputs.
    # ------------------------------------------------------------------
    context = build_context(
        health_data=health_data,
        contributor_data=contributor_data,
        risk_data=risk_data,
        evolution_data=evolution_data,
        repo_metadata=repo_metadata,
    )

    # ------------------------------------------------------------------
    # Step 4: Load prompt template and render with context.
    # ------------------------------------------------------------------
    prompt_template = load_prompt("repo_summary")
    user_prompt = prompt_template.format(repo_data=context)

    # ------------------------------------------------------------------
    # Step 5: Call LLM through the service abstraction (not directly).
    # ------------------------------------------------------------------
    import os
    ai_summary = generate_llm_response(
        user_prompt=user_prompt,
        system_prompt=_SYSTEM_PROMPT,
        max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
        temperature=float(os.getenv("TEMPERATURE", "0.3")),
    )

    logger.info("AI analysis complete for %s/%s", owner, repo)

    return {
        "owner": owner,
        "repo": repo,
        "ai_summary": ai_summary,
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        "model_used": os.getenv("MODEL_NAME", "gemini-2.5-flash"),
    }


def ask_repository_question_ai(owner: str, repo: str, question: str) -> Dict[str, Any]:
    """
    Answer a specific user question about a repository using its metrics.
    """
    logger.info("Answering AI question for %s/%s: %s", owner, repo, question[:50])

    try:
        commits = get_commits(owner, repo) or []
        contributors = get_contributors(owner, repo) or []
        pull_requests = get_pull_requests(owner, repo) or []
        issues = get_issues(owner, repo) or []
        repo_metadata = get_repo_metadata(owner, repo)
    except Exception as e:
        logger.error("Failed to fetch data for %s/%s: %s", owner, repo, e)
        raise ValueError(f"Could not fetch repository data for {owner}/{repo}: {e}")

    if not repo_metadata:
        raise ValueError(f"Repository {owner}/{repo} not found or is inaccessible.")

    languages = {}
    structure = {"total_files": 0, "total_folders": 0}
    try:
        languages = get_repo_languages(owner, repo) or {}
        tree = get_repo_tree(owner, repo)
        structure = analyze_repo_structure(tree)
    except Exception:
        pass

    health_data = analyze_health(commits, contributors, pull_requests, issues)
    contributor_data = analyze_contributors(contributors) if contributors else {}
    risk_data = compute_risk(contributors, pull_requests, issues, commits)
    evolution_data = summarize_repository(
        metadata=repo_metadata,
        languages=languages,
        structure=structure,
        pull_requests=pull_requests,
        issues=issues,
    )

    context = build_context(
        health_data=health_data,
        contributor_data=contributor_data,
        risk_data=risk_data,
        evolution_data=evolution_data,
        repo_metadata=repo_metadata,
    )

    user_prompt = (
        f"Repository Metrics Context:\n{context}\n\n"
        f"User Question:\n{question}\n\n"
        f"Answer the user's question clearly, constructively, and concisely using only the repository metrics provided."
    )

    import os
    answer = generate_llm_response(
        user_prompt=user_prompt,
        system_prompt=_SYSTEM_PROMPT,
        max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
        temperature=float(os.getenv("TEMPERATURE", "0.3")),
    )

    return {
        "owner": owner,
        "repo": repo,
        "question": question,
        "answer": answer,
        "model_used": os.getenv("MODEL_NAME", "gemini-2.5-flash"),
    }

