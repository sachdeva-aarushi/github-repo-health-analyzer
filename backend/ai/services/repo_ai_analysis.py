"""
AI-powered repository analysis orchestrator.

This is the main business logic service for AI narration.
It coordinates the flow:
    GitHub API â†’ Deterministic Analyzers â†’ Context Builder â†’ LLM â†’ Narrated Insights

RULES:
- All GitHub API fetches are grouped here (single point of fetch per request).
- Existing analyzers are called but NEVER modified.
- AI layer only interprets â€” it does not replace analytics.
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
    get_open_prs_count,
)
from analysis.health_analysis import analyze_health
from analysis.contributor_analysis import analyze_contributors
from analysis.risk_analysis import compute_risk
from analysis.evolution_analysis import summarize_repository, analyze_repo_structure, extract_tech_stack

from ai.services.context_builder import build_context
from ai.services.llm_service import generate_llm_response
from ai.utils.prompt_loader import load_prompt, load_system_prompt

from ai.core.orchestrator import AIOrchestrator
from ai.utils.prompt_loader import load_system_prompt
from ai.memory.session_memory import session_store

logger = logging.getLogger(__name__)

# NEW ARCHITECTURE: Authoritative GitIntel Repository Intelligence Analyst system prompt.
try:
    _SYSTEM_PROMPT = load_system_prompt("analyst")
except Exception:
    _SYSTEM_PROMPT = (
        "You are the GitIntel Repository Intelligence Analyst. "
        "Ground every answer in the Dashboard Snapshot and Structured Insights. "
        "Never claim data is missing when it exists in the provided context."
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

    # Get canonical owner and repo in case of redirects
    canonical_owner, canonical_repo = owner, repo
    if repo_metadata and "full_name" in repo_metadata:
        parts = repo_metadata["full_name"].split("/")
        if len(parts) == 2:
            canonical_owner, canonical_repo = parts[0], parts[1]

    # Fetch structure data separately â€” these are optional for the AI context.
    languages = {}
    structure = {"total_files": 0, "total_folders": 0}
    try:
        languages = get_repo_languages(canonical_owner, canonical_repo) or {}
        tree = get_repo_tree(canonical_owner, canonical_repo)
        structure = analyze_repo_structure(tree)
    except Exception:
        logger.warning("Could not fetch language/structure data for %s/%s", canonical_owner, canonical_repo)

    # Fetch actual open PRs count and calculate open issues count
    actual_open_prs = get_open_prs_count(canonical_owner, canonical_repo)
    open_issues_and_prs = repo_metadata.get("open_issues_count", 0) if repo_metadata else 0
    actual_open_issues = max(0, open_issues_and_prs - actual_open_prs)

    # ------------------------------------------------------------------
    # Step 2: Run deterministic analyzers (source of truth â€” untouched).
    # ------------------------------------------------------------------
    health_data = analyze_health(
        commits, 
        contributors, 
        pull_requests, 
        issues, 
        actual_open_issues=actual_open_issues, 
        actual_open_prs=actual_open_prs
    )
    contributor_data = analyze_contributors(contributors) if contributors else {}
    risk_data = compute_risk(
        contributors, 
        pull_requests, 
        issues, 
        commits, 
        actual_open_prs=actual_open_prs, 
        actual_open_issues=actual_open_issues
    )
    evolution_data = summarize_repository(
        metadata=repo_metadata,
        languages=languages,
        structure=structure,
        pull_requests=pull_requests,
        issues=issues,
        actual_open_prs=actual_open_prs,
        actual_open_issues=actual_open_issues,
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


def ask_repository_question_ai(owner: str, repo: str, question: str, dashboard_context: dict | None = None, session_id: str | None = None) -> Dict[str, Any]:
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

    # Get canonical owner and repo in case of redirects
    canonical_owner, canonical_repo = owner, repo
    if repo_metadata and "full_name" in repo_metadata:
        parts = repo_metadata["full_name"].split("/")
        if len(parts) == 2:
            canonical_owner, canonical_repo = parts[0], parts[1]

    languages = {}
    structure = {"total_files": 0, "total_folders": 0}
    try:
        languages = get_repo_languages(canonical_owner, canonical_repo) or {}
        tree = get_repo_tree(canonical_owner, canonical_repo)
        structure = analyze_repo_structure(tree)
    except Exception:
        pass

    # Fetch actual open PRs count and calculate open issues count
    actual_open_prs = get_open_prs_count(canonical_owner, canonical_repo)
    open_issues_and_prs = repo_metadata.get("open_issues_count", 0) if repo_metadata else 0
    actual_open_issues = max(0, open_issues_and_prs - actual_open_prs)

    health_data = analyze_health(
        commits, 
        contributors, 
        pull_requests, 
        issues, 
        actual_open_issues=actual_open_issues, 
        actual_open_prs=actual_open_prs
    )
    contributor_data = analyze_contributors(contributors) if contributors else {}
    risk_data = compute_risk(
        contributors, 
        pull_requests, 
        issues, 
        commits, 
        actual_open_prs=actual_open_prs, 
        actual_open_issues=actual_open_issues
    )
    evolution_data = summarize_repository(
        metadata=repo_metadata,
        languages=languages,
        structure=structure,
        pull_requests=pull_requests,
        issues=issues,
        actual_open_prs=actual_open_prs,
        actual_open_issues=actual_open_issues,
    )

    # ------------------------------------------------------------------
    # NEW ARCHITECTURE PATH (v2) — Dashboard Snapshot + Structured Intelligence + Orchestrator
    # ------------------------------------------------------------------
    orchestrator_used = False
    try:
        from ai.core.orchestrator import AIOrchestrator
        orchestrator = AIOrchestrator()

        package = orchestrator.build_context_package(
            owner=owner,
            repo=repo,
            user_question=question,
            health_data=health_data,
            contributor_data=contributor_data,
            risk_data=risk_data,
            evolution_data=evolution_data,
            repo_metadata=repo_metadata,
            frontend_snapshot=dashboard_context,
            session_id=session_id,
        )
        user_prompt = orchestrator.render_prompt(package)

        import os
        answer = generate_llm_response(
            user_prompt=user_prompt,
            system_prompt=_SYSTEM_PROMPT,
            max_tokens=int(os.getenv("MAX_TOKENS", "1536")),
            temperature=float(os.getenv("TEMPERATURE", "0.25")),
        )

        orchestrator.record_turn(session_id, package, answer)
        orchestrator_used = True

    except Exception as exc:
        # Graceful degradation to the original simple flow
        logger.warning("Orchestrator path failed, falling back: %s", exc)
        from ai.services.context_builder import build_context as legacy_build_context
        context = legacy_build_context(
            health_data=health_data,
            contributor_data=contributor_data,
            risk_data=risk_data,
            evolution_data=evolution_data,
            repo_metadata=repo_metadata,
        )
        user_prompt = (
            f"Repository Metrics Context:\n{context}\n\n"
            f"User Question:\n{question}\n\n"
            "Answer using the repository metrics. Reference visible charts when the question mentions them."
        )
        import os
        answer = generate_llm_response(
            user_prompt=user_prompt,
            system_prompt=_SYSTEM_PROMPT,
            max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
            temperature=float(os.getenv("TEMPERATURE", "0.3")),
        )

    result = {
        "owner": owner,
        "repo": repo,
        "question": question,
        "answer": answer,
        "model_used": os.getenv("MODEL_NAME", "gemini-2.5-flash"),
    }
    if orchestrator_used:
        result["architecture"] = "v2_orchestrator"
    else:
        result["architecture"] = "legacy_fallback"
    return result

