export default function RiskResponsivenessChart({ data }) {
    if (!data) return null;

    const metrics = [
        { label: "Time to first response", val: data.first_response + "d", width: "40%", color: "#fb923c" },
        { label: "Avg time to merge", val: data.merge_time + "d", width: "70%", color: "#fb923c" },
        { label: "Issue close time", val: data.close_time + "d", width: "85%", color: "#ef4444" },
        { label: "Stale PRs (>30d)", val: data.stale_prs, width: "30%", color: "#ef4444" },
    ];

    return (
        <div className="risk-card border-orange">
            <div className="risk-card-header">
                <div className="risk-card-title-container">
                    Responsiveness Risk
                </div>
                <span className="risk-badge bg-orange-light">MEDIUM</span>
            </div>
            <div className="risk-card-subtitle">
                Slow responses can drive contributors away
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', marginTop: '8px', marginBottom: '32px' }}>
                {metrics.map((m, i) => (
                    <div key={i} className="resp-row">
                        <div className="resp-label">{m.label}</div>
                        <div className="resp-bar-container">
                            <div className="resp-bar-bg">
                                <div className="resp-bar-fill" style={{ width: m.width, background: m.color }}></div>
                            </div>
                            <div className="resp-val">{m.val}</div>
                        </div>
                    </div>
                ))}
            </div>

        </div>
    );
}
