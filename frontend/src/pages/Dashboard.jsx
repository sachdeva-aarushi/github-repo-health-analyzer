import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { fetchCommitData, fetchContributors, fetchRepoOverview } from '../api';
import CommitsChart from '../charts/CommitsChart';
import ContributorsBarChart from '../charts/ContributorsBarChart';
import LorenzCurveChart from '../charts/LorenzCurveChart';
import WeekdayChart from '../charts/WeekDayChart';
import Navbar from '../components/Navbar';
import { fetchCommitVelocity } from "../api";
import AIChatPanel from '../components/ai/AIChatPanel';
import VelocityChart from "../charts/velocitycharts";


function Dashboard() {
    const [searchParams] = useSearchParams();
    const owner = searchParams.get('owner') || '';
    const repo = searchParams.get('repo') || '';


    const [data, setData] = useState(null);
    const [contributors, setContributors] = useState(null);
    const [overview, setOverview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [velocity, setVelocity] = useState(null);
    

    useEffect(() => {
        if (!owner || !repo) return;

        const fetchAll = async () => {
            setLoading(true);
            setError(null);
            setData(null);
            setContributors(null);
            setOverview(null);
            

            try {
                const [commitResult, contributorResult, overviewResult] = await Promise.all([
                    fetchCommitData(owner, repo),
                    fetchContributors(owner, repo),
                    fetchRepoOverview(owner, repo),
                ]);
                const vel = await fetchCommitVelocity(owner, repo);
                setVelocity(vel.velocity);
                setData(commitResult);
                setContributors(contributorResult);
                setOverview(overviewResult);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchAll();
    }, [owner, repo]);

    return (
        <div className="app-container">
            <Navbar owner={owner} repo={repo} />
            {loading && (
                <div className="loading-container">
                    <div className="spinner" />
                    <span className="loading-text">Fetching repository data...</span>
                </div>
            )}

            {error && (
                <div className="error-box">Error: {error}</div>
            )}

            {data && (
                <div className="dashboard-layout">
                    <aside className="dashboard-ai-sidebar">
                        <AIChatPanel owner={owner} repo={repo} />
                    </aside>
                    <main className="dashboard-main-content">
                <div className="results-section">
                    {/* Summary metric cards */}
                    {data.data.summary && (
                        <div className="summary-cards">
                            <div className="risk-summary-card border-shade-1 card-border-shade-1">
                                <div className="risk-summary-title">Avg Commits / Day</div>
                                <div className="risk-summary-level">{data.data.summary.avg_commits_per_day}</div>
                            </div>
                            <div className="risk-summary-card border-shade-2 card-border-shade-2">
                                <div className="risk-summary-title">Commit Std Dev</div>
                                <div className="risk-summary-level">{data.data.summary.std_dev_commits}</div>
                            </div>
                            {overview && (
                                <>
                                    <div className="risk-summary-card border-shade-3 card-border-shade-3">
                                        <div className="risk-summary-title">Stars</div>
                                        <div className="risk-summary-level">{overview.stars}</div>
                                    </div>
                                    <div className="risk-summary-card border-shade-4 card-border-shade-4">
                                        <div className="risk-summary-title">Files</div>
                                        <div className="risk-summary-level">{overview.total_files}</div>
                                    </div>
                                    <div className="risk-summary-card border-shade-5 card-border-shade-5">
                                        <div className="risk-summary-title">Folders</div>
                                        <div className="risk-summary-level">{overview.total_folders}</div>
                                    </div>
                                </>
                            )}
                        </div>
                    )}

                    <div className="dashboard-graphs-grid">
                        <div className="risk-card border-shade-1 card-border-shade-1">
                            <div className="risk-card-header">
                                <div className="risk-card-title-container">Commit Activity</div>
                            </div>
                            <div style={{ marginTop: '16px' }}>
                                <CommitsChart
                                    dates={data.data.dates}
                                    counts={data.data.counts}
                                    repository={data.repository}
                                />
                            </div>
                        </div>

                        {data.data.summary && (
                            <div className="risk-card border-shade-2 card-border-shade-2">
                                <div className="risk-card-header">
                                    <div className="risk-card-title-container">Weekly Commit Distribution</div>
                                </div>
                                <div style={{ marginTop: '16px' }}>
                                    <WeekdayChart data={data.data.summary.weekday_distribution} />
                                </div>
                            </div>
                        )}

                        {contributors && (
                            <div className="risk-card border-shade-3 card-border-shade-3">
                                <div className="risk-card-header">
                                    <div className="risk-card-title-container">Contributor Distribution</div>
                                </div>
                                <div style={{ marginTop: '16px' }}>
                                    <ContributorsBarChart data={contributors.contributors} />
                                    <div style={{ marginTop: '16px', fontSize: '14px', color: '#64748b' }}>
                                        <p><strong>Top Contributor %:</strong> {contributors.top_contributor_percentage}%</p>
                                        <p><strong>Bus Factor:</strong> {contributors.bus_factor}</p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {velocity && (
                            <div className="risk-card border-shade-4 card-border-shade-4">
                                <div className="risk-card-header">
                                    <div className="risk-card-title-container">Commit Velocity (Weekly)</div>
                                </div>
                                <div style={{ marginTop: '16px' }}>
                                    <VelocityChart data={velocity} />
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Lorenz Curve at the bottom */}
                    {contributors && (
                        <div className="risk-card border-shade-5 card-border-shade-5" style={{ marginTop: '24px' }}>
                            <div className="risk-card-header">
                                <div className="risk-card-title-container">Contribution Inequality (Lorenz Curve)</div>
                            </div>
                            <div style={{ marginTop: '16px' }}>
                                <LorenzCurveChart data={contributors.lorenz_curve} />
                            </div>
                        </div>
                    )}

                    {/* Raw JSON toggle */}
                    <details className="json-toggle" style={{ marginTop: '40px' }}>
                        <summary>View Raw JSON Data</summary>
                        <pre className="json-pre">
                            {JSON.stringify(data, null, 2)}
                        </pre>
                    </details>
                </div>
                    </main>
                </div>
            )}
        </div>
    );
}

export default Dashboard;
