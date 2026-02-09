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
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>GitHub Repo Health Analyzer</h1>

            <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
                <div style={{ marginBottom: '10px' }}>
                    <input
                        type="text"
                        placeholder="Owner (e.g., facebook)"
                        value={owner}
                        onChange={(e) => setOwner(e.target.value)}
                        required
                        style={{
                            padding: '8px',
                            marginRight: '10px',
                            width: '200px'
                        }}
                    />
                    <input
                        type="text"
                        placeholder="Repo (e.g., react)"
                        value={repo}
                        onChange={(e) => setRepo(e.target.value)}
                        required
                        style={{
                            padding: '8px',
                            marginRight: '10px',
                            width: '200px'
                        }}
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            padding: '8px 16px',
                            cursor: loading ? 'not-allowed' : 'pointer'
                        }}
                    >
                        {loading ? 'Loading...' : 'Analyze'}
                    </button>
                </div>
            </form>

            {error && (
                <div style={{
                    padding: '10px',
                    backgroundColor: '#ffebee',
                    color: '#c62828',
                    borderRadius: '4px',
                    marginBottom: '20px'
                }}>
                    Error: {error}
                </div>
            )}

            {data && (
                <div>
                    <h2>Results for {data.repository}</h2>

                    <div style={{
                        marginBottom: '30px',
                        padding: '20px',
                        backgroundColor: '#ffffff',
                        borderRadius: '8px',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                    }}>
                        <CommitsChart
                            dates={data.data.dates}
                            counts={data.data.counts}
                            repository={data.repository}
                        />
                    </div>

                    <details style={{ marginTop: '20px' }}>
                        <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                            View Raw JSON Data
                        </summary>
                        <pre style={{
                            backgroundColor: '#f5f5f5',
                            padding: '15px',
                            borderRadius: '4px',
                            overflow: 'auto',
                            marginTop: '10px'
                        }}>
                            {JSON.stringify(data, null, 2)}
                        </pre>
                    </details>
                </div>
            )}
        </div>
    );
}

export default App;
