import { useState } from 'react';
import { fetchCommitData, fetchContributors, fetchRepoOverview, fetchRepoStructure, fetchFileContent } from './api';
import CommitsChart from './charts/CommitsChart';
import ContributorsBarChart from "./charts/ContributorsBarChart";
import LorenzCurveChart from "./charts/LorenzCurveChart";
import WeekdayChart from "./charts/WeekDayChart";
import OverviewCards from "./components/overview_cards";
import RepoTree from "./components/repotree";

function App() {
    const [owner, setOwner] = useState('');
    const [repo, setRepo] = useState('');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [contributors, setContributors] = useState(null);
    const [overview, setOverview] = useState(null);
    const [structure, setStructure] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);
    const [fileContent, setFileContent] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Reset state
        setError(null);
        setData(null);
        setContributors(null);
        setLoading(true);
        setOverview(null);
        setStructure(null);

        try {
            const commitResult = await fetchCommitData(owner, repo);
            setData(commitResult);

            const contributorResult = await fetchContributors(owner, repo);
            setContributors(contributorResult);

            const overviewResult = await fetchRepoOverview(owner, repo);
            setOverview(overviewResult);

            const structureResult = await fetchRepoStructure(owner, repo);
            setStructure(structureResult);

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleFileClick = async (path) => {
        try {
            setSelectedFile(path);

            const file = await fetchFileContent(owner, repo, path);

            // Decode base64 safely resolving UTF-8 characters (like emojis and non-English text)
            const binaryStr = atob(file.content.replace(/\n/g, ""));
            const bytes = new Uint8Array([...binaryStr].map((char) => char.charCodeAt(0)));
            const decoded = new TextDecoder().decode(bytes);

            setFileContent(decoded);

        } catch (err) {
            console.error(err);
            setFileContent("Error loading file (might be a binary or unsupported format)");
        }
    };

    return (
        <div className="app-container">
            <h1 className="app-title">GitHub Repo <span>Health Analyzer</span></h1>
            <p className="app-subtitle">
                Analyze commit activity and health metrics for any public repository
            </p>

            <form onSubmit={handleSubmit} className="search-form">
                <input
                    id="owner-input"
                    className="input-field"
                    type="text"
                    placeholder="Owner (e.g., facebook)"
                    value={owner}
                    onChange={(e) => setOwner(e.target.value)}
                    required
                />
                <input
                    id="repo-input"
                    className="input-field"
                    type="text"
                    placeholder="Repo (e.g., react)"
                    value={repo}
                    onChange={(e) => setRepo(e.target.value)}
                    required
                />
                <button
                    id="analyze-btn"
                    type="submit"
                    disabled={loading}
                    className="btn-analyze"
                >
                    {loading ? 'Analyzing...' : 'Analyze'}
                </button>
            </form>

            {loading && (
                <div className="loading-container">
                    <div className="spinner" />
                    <span className="loading-text">Fetching repository data...</span>
                </div>
            )}

            {error && (
                <div className="error-box">
                    Error: {error}
                </div>
            )}

            {data && (
                <div className="results-section">
                    <h2 className="results-title">
                        {/* Summary Metrics */}
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
                                        ({data.data.summary.most_active_day.commits})
                                    </p>
                                </div>
                                {overview && (
                                    <div className="overview-section">
                                        <OverviewCards data={overview} />
                                    </div>
                                )}

                            </div>
                        )}
                        Results for {data.repository}
                    </h2>

                    <div className="chart-card">
                        <CommitsChart
                            dates={data.data.dates}
                            counts={data.data.counts}
                            repository={data.repository}
                        />
                    </div>
                    {data.data.summary && (
                        <div className="chart-card">
                            <h3>Weekly Commit Distribution</h3>

                            <WeekdayChart
                                data={data.data.summary.weekday_distribution}
                            />
                        </div>
                    )}

                    <details className="json-toggle">
                        <summary>View Raw JSON Data</summary>
                        <pre className="json-pre">
                            {JSON.stringify(data, null, 2)}
                        </pre>
                    </details>
                    {contributors && (
                        <>
                            {/* Bar Chart */}
                            <div className="chart-card">
                                <h3>Contributor Distribution</h3>

                                <ContributorsBarChart
                                    data={contributors.contributors}
                                />

                                <div style={{ marginTop: "10px" }}>
                                    <p><strong>Top Contributor %:</strong> {contributors.top_contributor_percentage}%</p>
                                    <p><strong>Bus Factor:</strong> {contributors.bus_factor}</p>
                                </div>
                            </div>

                            {/* Lorenz Curve */}
                            <div className="chart-card" style={{ marginTop: "30px" }}>
                                <h3>Contribution Inequality (Lorenz Curve)</h3>
                                <LorenzCurveChart
                                    data={contributors.lorenz_curve}
                                />
                            </div>
                        </>
                    )}
                    {structure && (
                        <div className="chart-card">
                            <div className="tree-container">
                                <RepoTree data={structure} onFileClick={handleFileClick} />
                            </div>
                        </div>
                    )}
                    {fileContent && (
                        <div className="chart-card">
                            <h3>{selectedFile}</h3>

                            <pre className="file-content-box">
                                {fileContent}
                            </pre>
                        </div>
                    )}

                </div>
            )}
        </div>
    );
}

export default App;
