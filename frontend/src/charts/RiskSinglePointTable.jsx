export default function RiskSinglePointTable({ data }) {
    if (!data) return null;
    const risky = (data.contributors || []).filter(c => c && c.percentage > 20).slice(0, 5);
    return (
        <div className="risk-card border-red">
            <div className="risk-card-header">
                <div className="risk-card-title-container">
                    Single Point of Failure
                </div>
                <span className="risk-badge bg-red-light">HIGH</span>
            </div>
            <div className="risk-card-subtitle">
                One person merges most PRs or owns core files
            </div>
            <table className="risk-table">
                <thead>
                    <tr>
                        <th>Contributor</th>
                        <th>Owns</th>
                        <th style={{ textAlign: 'right' }}>Risk</th>
                    </tr>
                </thead>
                <tbody>
                    {risky.map((c, i) => (
                        <tr key={i}>
                            <td className="contributor-cell">
                                <div className="avatar-circle">
                                    {(c.login || "").substring(0, 2).toUpperCase() || "??"}
                                </div>
                                {c.login || "Unknown"}
                            </td>
                            <td style={{ color: '#ef4444', fontFamily: 'monospace', fontWeight: 700 }}>
                                {(c.percentage || 0).toFixed(1)}%
                            </td>
                            <td style={{ textAlign: 'right' }}>
                                <span className="risk-badge bg-red-light" style={{ padding: '6px 12px' }}>Critical</span>
                            </td>
                        </tr>
                    ))}
                    {risky.length === 0 && (
                        <tr>
                            <td colSpan="3" style={{ textAlign: 'center', color: '#64748b' }}>No single point of failure detected.</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}
