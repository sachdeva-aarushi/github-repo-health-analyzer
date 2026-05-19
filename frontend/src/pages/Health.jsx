import { useEffect, useState } from "react";
import { useSearchParams } from 'react-router-dom';
import { fetchHealth } from "../api";
import Navbar from '../components/Navbar';
import AIChatPanel from '../components/ai/AIChatPanel';

const healthPrompts = [
    "Explain this health score",
    "How maintainable is this repository?",
    "What affects repository health?",
    "How healthy is contributor activity?"
];
import HealthDonut from "../charts/healthdonut";
import DimensionBars from "../charts/dimensionchart";
import HealthTimeline from "../charts/healthtimeline";
import IssuePRChart from "../charts/issuePRchart";
import DependencyHeatmap from "../charts/dependencyheatmap";
import MaintainerWorkload from "../charts/maintainerworkload";

export default function Health() {
    const [searchParams] = useSearchParams();
    const owner = searchParams.get('owner') || '';
    const repo = searchParams.get('repo') || '';

    const [health, setHealth] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!owner || !repo) return;
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
    }, [owner, repo]);

    if (loading) return <p>Loading...</p>;
    if (error) return <p className="error">Error: {error}</p>;
    if (!health) return <p>No health data available</p>;

    return (
        <div className="app-container">
        <Navbar owner={owner} repo={repo} />

            <div className="dashboard-layout">
                <aside className="dashboard-ai-sidebar">
                    <AIChatPanel 
                        owner={owner} 
                        repo={repo} 
                        pageContext="Health Insights"
                        quickPrompts={healthPrompts}
                    />
                </aside>
                <main className="dashboard-main-content">


            {/* ===== OVERALL HEALTH ===== */}
            <h3 className="section-title" style={{ textAlign: 'center' }}>Overall Health</h3>

            <div className="health-grid">

                {/* Health Score */}
                <div className="health-card border-shade-1 card-border-shade-1">
                    <h4>Health Score</h4>
                    <p className="health-score">
                        {health.score}/100
                    </p>
                    <span className="status">{health.status}</span>
                </div>

                {/* Release cadence (proxy using PR merge time) */}
                <div className="health-card border-shade-2 card-border-shade-2">
                    <h4>PR Merge Time</h4>
                    <p style={{ fontSize: health.summary.avg_pr_merge_time === 0 ? '16px' : '22px' }}>
                        {health.summary.avg_pr_merge_time === 0 ? "No PRs created" : `${health.summary.avg_pr_merge_time} hrs`}
                    </p>
                    <span className="subtext">avg merge time</span>
                </div>

                {/* Issue close rate */}
                <div className="health-card border-shade-3 card-border-shade-3">
                    <h4>Issue Close Rate</h4>
                    <p style={{ fontSize: health.summary.issue_close_rate === 0 ? '16px' : '22px' }}>
                        {health.summary.issue_close_rate === 0 ? "No issues created" : `${health.summary.issue_close_rate}%`}
                    </p>
                    <span className="subtext">resolution efficiency</span>
                </div>

                {/* Recency */}
                <div className="health-card border-shade-4 card-border-shade-4">
                    <h4>Last Commit</h4>
                    <p>{health.summary.last_commit_days} days ago</p>
                    <span className="subtext">activity recency</span>
                </div>

            </div>

            {/* ===== RISK SIGNALS ===== */}
            <h3 className="section-title" style={{ textAlign: 'center' }}>Risk Signals</h3>

            <div className="risk-list">
                {health.risk_signals.length === 0 ? (
                    <div className="risk-item low" style={{ textAlign: 'center' }}>No risk signals detected. Repository is stable.</div>
                ) : (
                    health.risk_signals.map((r, i) => (
                        <div key={i} className={`risk-item ${r.status}`}>
                            {r.name}
                        </div>
                    ))
                )}
            </div>
            {/* ===== VISUAL ANALYTICS ===== */}
            <h3 className="section-title" style={{ textAlign: 'center' }}>Health Insights</h3>

            <div className="health-visual-grid">

                {/* Donut */}
                <div className="visual-card border-shade-1 card-border-shade-1">
                    <h4>Health Composition</h4>
                    <HealthDonut data={health.health_distribution} />
                </div>

                {/* Dimension Bars */}
                <div className="visual-card border-shade-2 card-border-shade-2">
                    <h4>Dimension Scores</h4>
                    <DimensionBars data={health.dimension_scores} />
                </div>

            </div>
            {/* ===== ADVANCED ANALYTICS ===== */}
            <div className="health-visual-grid">

            {/* Timeline */}
                {health.timeline && health.timeline.length > 0 && (
                    <div className="visual-card border-shade-3 card-border-shade-3">
                        <h4>Health Score History</h4>
                        <HealthTimeline data={health.timeline} />
                    </div>
                )}

                {/* Issue vs PR */}
                {health.issue_pr_stats && (
                    <div className="visual-card border-shade-4 card-border-shade-4">
                        <h4>Issue & PR Health</h4>
                        {(!health.issue_pr_stats.opened || Object.keys(health.issue_pr_stats.opened).length === 0) ? (
                            <p style={{ color: '#9CB3CC', padding: '40px 0', textAlign: 'center' }}>No issues or PRs created</p>
                        ) : (
                            <IssuePRChart data={health.issue_pr_stats} />
                        )}
                    </div>
                )}

            </div>
            {/* ===== NEW ANALYTICS ===== */}
            <div className="health-visual-grid">

                {/* Evolution Phase */}
                <div className="visual-card border-shade-5 card-border-shade-5">
                    <h4>Repository Phase</h4>
                    <p className="phase-text">{health.phase}</p>
                </div>

                {/* Dependency Heatmap */}
                <div className="visual-card border-shade-1 card-border-shade-1">
                    <h4>Dependency Health</h4>
                    <DependencyHeatmap data={health.dependency_heatmap} repo={repo} />
                </div>

            </div>

            <div className="visual-card border-shade-2 card-border-shade-2" style={{ marginTop: "20px" }}>
                <h4>Maintainer Workload</h4>
                <MaintainerWorkload data={health.workload} />
            </div>
                </main>
            </div>
        </div>
    );
}