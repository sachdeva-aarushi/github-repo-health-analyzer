export default function DependencyHeatmap({ data, repo }) {

    const getStatusInfo = (status) => {
        switch (status) {
            case "current": return { color: "#27D3FF", label: "Healthy", desc: "Up to date", risk: "Low Risk" };
            case "patch": return { color: "#53A8FF", label: "Stable", desc: "Patch available", risk: "Low Risk" };
            case "minor": return { color: "#448AFF", label: "Warning", desc: "Minor update needed", risk: "Medium Risk" };
            case "major": return { color: "#1C5D7A", label: "Risky", desc: "Major update needed", risk: "High Risk" };
            default: return { color: "#0A2239", label: "Critical", desc: "Unknown/Deprecated", risk: "Critical Risk" };
        }
    };

    const legendItems = [
        { label: "Healthy", color: "#27D3FF" },
        { label: "Stable", color: "#53A8FF" },
        { label: "Warning", color: "#448AFF" },
        { label: "Risky", color: "#1C5D7A" },
        { label: "Critical", color: "#0A2239" },
    ];

    if (!data || data.length === 0) {
        return <div style={{ color: '#9CB3CC', textAlign: 'center', padding: '20px 0' }}>No files found to map</div>;
    }

    return (
        <div>
            <div className="heatmap-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(32px, 1fr))', gap: '6px' }}>
                {data.map((cell, i) => {
                    const info = getStatusInfo(cell.status);
                    const depName = cell.name;
                    return (
                        <div
                            key={i}
                            className="heatmap-cell"
                            style={{ background: info.color, height: '32px', width: '100%', borderRadius: '4px' }}
                        >
                            <div className="heatmap-tooltip">
                                <div className="heatmap-tooltip-title" style={{ maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{depName}</div>
                                <div className="heatmap-tooltip-status" style={{ color: info.color }}>
                                    {info.label} • {info.risk}
                                </div>
                                <div className="heatmap-tooltip-desc">{info.desc}</div>
                            </div>
                        </div>
                    );
                })}
            </div>
            
            <div className="heatmap-legend">
                {legendItems.map((item, idx) => (
                    <div key={idx} className="heatmap-legend-item">
                        <div className="heatmap-legend-color" style={{ background: item.color }}></div>
                        <span>{item.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}