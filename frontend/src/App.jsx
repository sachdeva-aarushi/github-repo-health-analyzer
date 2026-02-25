import { useState } from 'react';
import { fetchCommitData, fetchContributors } from './api';
import CommitsChart from './charts/CommitsChart';
import ContributorsBarChart from "./charts/ContributorsBarChart";

function App() {
    const [owner, setOwner] = useState('');
    const [repo, setRepo] = useState('');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [contributors, setContributors] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Reset state
        setError(null);
        setData(null);
        setLoading(true);

        try {
            const commitResult = await fetchCommitData(owner, repo);
            setData(commitResult);

            const contributorResult = await fetchContributors(owner, repo);
            setContributors(contributorResult);

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
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
                        Results for {data.repository}
                    </h2>

                    <div className="chart-card">
                        <CommitsChart
                            dates={data.data.dates}
                            counts={data.data.counts}
                            repository={data.repository}
                        />
                    </div>

                    <details className="json-toggle">
                        <summary>View Raw JSON Data</summary>
                        <pre className="json-pre">
                            {JSON.stringify(data, null, 2)}
                        </pre>
                    </details>
                    {contributors && (
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
                    )}
                </div>
            )}
        </div>
    );
}

export default App;
