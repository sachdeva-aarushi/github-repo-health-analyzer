import { useEffect, useState } from "react";
import { fetchHealth } from "../api";
import Navbar from '../components/Navbar';
import HealthDonut from "../charts/healthdonut";
import DimensionBars from "../charts/dimensionchart";
import HealthTimeline from "../charts/healthtimeline";
import IssuePRChart from "../charts/issuePRchart";
import DependencyHeatmap from "../charts/dependencyheatmap";
import MaintainerWorkload from "../charts/maintainerworkload";

export default function Health() {
    const [health, setHealth] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    const owner = "facebook";
    const repo = "react";

    useEffect(() => {
        async function load() {
            try {
                setLoading(true);
                const res = await fetchHealth(owner, repo);
                setHealth(res.health);
                setError(null);
            } catch (err) {
                console.error("Error fetching health:", err);
                setError(err.message || "Failed to fetch health data");
                setHealth(null);
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    if (loading) return <p>Loading...</p>;
    if (error) return <p className="error">Error: {error}</p>;
    if (!health) return <p>No health data available</p>;

    return (
        <div className="app-container">
        <Navbar owner={owner} repo={repo} />

            {/* ===== HEADER ===== */}
            <h1 className="app-title">
                {owner}/{repo}
            </h1>

            {/* ===== BADGES ===== */}
            <div className="badge-row">
                <span className="badge green">● Actively Maintained</span>
                <span className="badge green">● Safe to Use</span>
                <span className="badge blue">
                    ● {health.summary.contributors} Contributors
                </span>
            </div>

            {/* ===== OVERALL HEALTH ===== */}
            <h3 className="section-title">Overall Health</h3>

            <div className="health-grid">

                {/* Health Score */}
                <div className="health-card">
                    <h4>Health Score</h4>
                    <p className="health-score">
                        {health.score}/100
                    </p>
                    <span className="status">{health.status}</span>
                </div>

                {/* Release cadence (proxy using PR merge time) */}
                <div className="health-card">
                    <h4>PR Merge Time</h4>
                    <p>{health.summary.avg_pr_merge_time} hrs</p>
                    <span className="subtext">avg merge time</span>
                </div>

                {/* Issue close rate */}
                <div className="health-card">
                    <h4>Issue Close Rate</h4>
                    <p>{health.summary.issue_close_rate}%</p>
                    <span className="subtext">resolution efficiency</span>
                </div>

                {/* Recency */}
                <div className="health-card">
                    <h4>Last Commit</h4>
                    <p>{health.summary.last_commit_days} days ago</p>
                    <span className="subtext">activity recency</span>
                </div>

            </div>

            {/* ===== RISK SIGNALS ===== */}
            <h3 className="section-title">Risk Signals</h3>

            <div className="risk-list">
                {health.risk_signals.map((r, i) => (
                    <div key={i} className={`risk-item ${r.status}`}>
                        {r.name}
                    </div>
                ))}
            </div>
            {/* ===== VISUAL ANALYTICS ===== */}
            <h3 className="section-title">Health Insights</h3>

            <div className="health-visual-grid">

                {/* Donut */}
                <div className="visual-card">
                    <h4>Health Composition</h4>
                    <HealthDonut data={health.health_distribution} />
                </div>

                {/* Dimension Bars */}
                <div className="visual-card">
                    <h4>Dimension Scores</h4>
                    <DimensionBars data={health.dimension_scores} />
                </div>

            </div>
            {/* ===== ADVANCED ANALYTICS ===== */}
            <div className="health-visual-grid">

            {/* Timeline */}
                {health.timeline && health.timeline.length > 0 && (
                    <div className="visual-card">
                        <h4>Health Score History</h4>
                        <HealthTimeline data={health.timeline} />
                    </div>
                )}

                {/* Issue vs PR */}
                {health.issue_pr_stats && (
                    <div className="visual-card">
                        <h4>Issue & PR Health</h4>
                        <IssuePRChart data={health.issue_pr_stats} />
                    </div>
                )}

            </div>
            {/* ===== NEW ANALYTICS ===== */}
            <div className="health-visual-grid">

                {/* Evolution Phase */}
                <div className="visual-card">
                    <h4>Repository Phase</h4>
                    <p className="phase-text">{health.phase}</p>
                </div>

                {/* Dependency Heatmap */}
                <div className="visual-card">
                    <h4>Dependency Health</h4>
                    <DependencyHeatmap data={health.dependency_heatmap} />
                </div>

            </div>

            <div className="visual-card" style={{ marginTop: "20px" }}>
                <h4>Maintainer Workload</h4>
                <MaintainerWorkload data={health.workload} />
            </div>

        </div>
    );
}