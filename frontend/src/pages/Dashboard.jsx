import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { fetchCommitData, fetchContributors, fetchRepoOverview, fetchHotFiles } from '../api';
import CommitsChart from '../charts/CommitsChart';
import ContributorsBarChart from '../charts/ContributorsBarChart';
import LorenzCurveChart from '../charts/LorenzCurveChart';
import WeekdayChart from '../charts/WeekDayChart';
import OverviewCards from '../components/overview_cards';
import Navbar from '../components/Navbar';
import { fetchCommitVelocity } from "../api";
import VelocityChart from "../charts/velocitycharts";
import HotFilesChart from "../charts/hotefileschart";

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
    const [hotFiles, setHotFiles] = useState(null);

    useEffect(() => {
        if (!owner || !repo) return;

        const fetchAll = async () => {
            setLoading(true);
            setError(null);
            setData(null);
            setContributors(null);
            setOverview(null);
            setHotFiles(null);

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
                const hot = await fetchHotFiles(owner, repo);
                setHotFiles(hot.hot_files);
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

            <h1 className="app-title">
                Dashboard — <span>{owner}/{repo}</span>
            </h1>

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
                <div className="results-section">
                    {/* Summary metric cards */}
                    {data.data.summary && (
                        <div className="summary-cards">
                            <div className="summary-card">
                                <h4>Total Commits</h4>
                                <p>{data.data.total_commits}</p>
                            </div>
                            <div className="summary-card">
                                <h4>Avg Commits / Day</h4>
                                <p>{data.data.summary.avg_commits_per_day}</p>
                            </div>
                            <div className="summary-card">
                                <h4>Std Dev</h4>
                                <p>{data.data.summary.std_dev_commits}</p>
                            </div>
                            <div className="summary-card">
                                <h4>Most Active Day</h4>
                                <p>
                                    {data.data.summary.most_active_day.date}
                                    {' '}({data.data.summary.most_active_day.commits})
                                </p>
                            </div>

                            {overview && (
                                <div className="overview-section">
                                    <OverviewCards data={overview} />
                                </div>
                            )}
                        </div>
                    )}

                    {/* Commit activity chart */}
                    <div className="chart-card">
                        <CommitsChart
                            dates={data.data.dates}
                            counts={data.data.counts}
                            repository={data.repository}
                        />
                    </div>

                    {/* Weekday distribution */}
                    {data.data.summary && (
                        <div className="chart-card">
                            <h3>Weekly Commit Distribution</h3>
                            <WeekdayChart data={data.data.summary.weekday_distribution} />
                        </div>
                    )}

                    {/* Raw JSON toggle */}
                    <details className="json-toggle">
                        <summary>View Raw JSON Data</summary>
                        <pre className="json-pre">
                            {JSON.stringify(data, null, 2)}
                        </pre>
                    </details>

                    {/* Contributors */}
                    {contributors && (
                        <>
                            <div className="chart-card">
                                <h3>Contributor Distribution</h3>
                                <ContributorsBarChart data={contributors.contributors} />
                                <div style={{ marginTop: '10px' }}>
                                    <p><strong>Top Contributor %:</strong> {contributors.top_contributor_percentage}%</p>
                                    <p><strong>Bus Factor:</strong> {contributors.bus_factor}</p>
                                </div>
                            </div>

                            <div className="chart-card" style={{ marginTop: '30px' }}>
                                <h3>Contribution Inequality (Lorenz Curve)</h3>
                                <LorenzCurveChart data={contributors.lorenz_curve} />
                            </div>
                        </>
                    )}
                    {velocity && (
                        <div className="chart-card">
                            <h3>Commit Velocity (Weekly)</h3>
                            <VelocityChart data={velocity} />
                        </div>
                    )}
                    {hotFiles && (
                        <div className="chart-card">
                            <h3>Hot Files</h3>
                            <HotFilesChart data={hotFiles} />
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default Dashboard;
