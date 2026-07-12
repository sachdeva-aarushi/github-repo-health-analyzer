"""
Context builder for AI narration.

Collects and structures repository analysis outputs into a clean, compressed
context string for AI interpretation.

RULES:
- Only consumes outputs from existing deterministic analyzers.
- Does NOT call GitHub API or run any analysis logic itself.
- Sanitizes all user-controlled strings (repo name, description) before injection.
- Respects the token budget defined in token_utils.
"""

from typing import Dict, Any, Optional
from ai.utils.token_utils import truncate_to_token_budget
from ai.utils.prompt_loader import sanitize_user_content


def build_compact_analysis_summary(
    health_data: Optional[Dict[str, Any]] = None,
    contributor_data: Optional[Dict[str, Any]] = None,
    risk_data: Optional[Dict[str, Any]] = None,
    evolution_data: Optional[Dict[str, Any]] = None,
    repo_metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Build a structured, compact, and token-efficient summary of the repository analysis.
    This serves as the grounding context for the LLM.
    """
    parts = []

    # 1. Repository Overview
    if repo_metadata:
        parts.append("=== REPOSITORY OVERVIEW ===")
        name = sanitize_user_content(str(repo_metadata.get("full_name", "Unknown")))
        description = sanitize_user_content(str(repo_metadata.get("description") or "No description provided."))
        language = sanitize_user_content(str(repo_metadata.get("language") or "Unknown"))
        parts.append(f"- Repository: {name}")
        parts.append(f"- Description: {description}")
        parts.append(f"- Primary Language: {language}")
        parts.append(f"- Stars: {repo_metadata.get('stargazers_count', 0)}")
        parts.append(f"- Forks: {repo_metadata.get('forks_count', 0)}")
        parts.append(f"- Open Issues Count: {repo_metadata.get('open_issues_count', 0)}")
        parts.append("")

    # 2. Health Score & Metrics
    if health_data:
        parts.append("=== HEALTH ANALYSIS ===")
        parts.append(f"- Overall Health Score: {health_data.get('score', 0)}/100 ({health_data.get('status', 'Unknown')})")
        
        summary = health_data.get("summary", {})
        if summary:
            parts.append(f"- Last Commit Recency: {summary.get('last_commit_days', 'N/A')} days ago")
            parts.append(f"- Issue Close Rate: {summary.get('issue_close_rate', 0)}%")
            parts.append(f"- Avg PR Merge Time: {summary.get('avg_pr_merge_time', 0)} hours")

        dimension_scores = health_data.get("dimension_scores", {})
        if dimension_scores:
            parts.append("- Dimension Scores (out of 100):")
            for dim, score in dimension_scores.items():
                dim_name = dim.replace("_", " ").title()
                parts.append(f"  * {dim_name}: {score}")
        parts.append("")

    # 3. Top Risks
    parts.append("=== TOP RISKS ===")
    has_risks = False
    if risk_data and "summary" in risk_data:
        for key, val in risk_data["summary"].items():
            level = val.get("level", "LOW")
            value_desc = val.get("value", "N/A")
            if level in ("HIGH", "MEDIUM"):
                label = key.replace("_", " ").title()
                parts.append(f"- [{level} RISK] {label}: {value_desc}")
                has_risks = True
    
    if health_data and "risk_signals" in health_data:
        for signal in health_data["risk_signals"]:
            name = signal.get("name", "Unknown")
            status = signal.get("status", "low")
            if status in ("high", "medium"):
                parts.append(f"- [{status.upper()} RISK] {name}")
                has_risks = True

    if not has_risks:
        parts.append("- No high or medium risks identified. Repository is stable.")
    parts.append("")

    # 4. Contributor Stats & Workload
    if contributor_data or (health_data and "workload" in health_data):
        parts.append("=== CONTRIBUTOR & WORKLOAD STATS ===")
        if contributor_data:
            parts.append(f"- Bus Factor: {contributor_data.get('bus_factor', 'N/A')}")
            parts.append(f"- Top Contributor Share: {contributor_data.get('top_contributor_percentage', 0)}%")
            parts.append(f"- Total Contributors: {len(contributor_data.get('contributors', []))}")
        
        # Workload (exact maintainer commit share)
        workload = health_data.get("workload", []) if health_data else []
        if workload:
            parts.append("- Maintainer Commit Distribution:")
            for member in workload[:5]: # Top 5
                parts.append(f"  * {member.get('name')}: {member.get('commits')} commits ({member.get('percentage')}%)")
        parts.append("")

    # 5. Dependency Issues / Heatmap
    if health_data and "dependency_heatmap" in health_data:
        parts.append("=== DEPENDENCY ISSUES & HEATMAP ===")
        heatmap = health_data["dependency_heatmap"]
        total_files = len(heatmap)
        
        counts = {"current": 0, "patch": 0, "minor": 0, "major": 0, "critical": 0}
        hotspots = []
        for cell in heatmap:
            status = cell.get("status", "current")
            counts[status] = counts.get(status, 0) + 1
            if status in ("major", "minor", "critical"):
                hotspots.append((cell.get("name"), status))
        
        parts.append(f"- Total Tracked Files/Dependencies: {total_files}")
        parts.append(f"- Status Breakdown: Healthy (current)={counts['current']}, Stable (patch)={counts['patch']}, Warning (minor)={counts['minor']}, Risky (major)={counts['major']}, Critical={counts['critical']}")
        
        if hotspots:
            parts.append("- Dependency Hotspots / Outdated Files (Top 5):")
            for name, status in hotspots[:5]:
                parts.append(f"  * {name} ({status.upper()} risk level)")
        else:
            parts.append("- All analyzed dependencies are healthy and up to date.")
        parts.append("")

    # 6. Structure Overview
    if evolution_data:
        parts.append("=== STRUCTURE OVERVIEW ===")
        parts.append(f"- Total Files: {evolution_data.get('total_files', 'N/A')}")
        parts.append(f"- Total Folders: {evolution_data.get('total_folders', 'N/A')}")
        parts.append(f"- Total Pull Requests: {evolution_data.get('total_pull_requests', 'N/A')}")
        parts.append(f"- Total Issues: {evolution_data.get('total_issues', 'N/A')}")
        
        languages = evolution_data.get("languages", {})
        if languages:
            sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
            lang_strs = []
            total_bytes = sum(languages.values())
            for lang, bytes_count in sorted_langs:
                pct = round(bytes_count / total_bytes * 100, 1) if total_bytes else 0
                lang_strs.append(f"{lang} ({pct}%)")
            parts.append(f"- Languages: {', '.join(lang_strs)}")
        parts.append("")

    return "\n".join(parts)


def build_context(
    health_data: Optional[Dict[str, Any]] = None,
    contributor_data: Optional[Dict[str, Any]] = None,
    risk_data: Optional[Dict[str, Any]] = None,
    evolution_data: Optional[Dict[str, Any]] = None,
    repo_metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Build a structured, token-efficient context string from analyzer outputs.
    """
    context = build_compact_analysis_summary(
        health_data=health_data,
        contributor_data=contributor_data,
        risk_data=risk_data,
        evolution_data=evolution_data,
        repo_metadata=repo_metadata,
    )
    return truncate_to_token_budget(context)

