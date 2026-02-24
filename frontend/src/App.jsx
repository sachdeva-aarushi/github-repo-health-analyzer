import { useState } from 'react';
import { fetchCommitData } from './api';
import CommitsChart from './charts/CommitsChart';

function App() {
    const [owner, setOwner] = useState('');
    const [repo, setRepo] = useState('');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Reset state
        setError(null);
        setData(null);
        setLoading(true);

        try {
            const result = await fetchCommitData(owner, repo);
            setData(result);
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
                </div>
            )}
        </div>
    );
}

export default App;
