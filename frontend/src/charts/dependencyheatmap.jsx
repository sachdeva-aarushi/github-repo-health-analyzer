export default function DependencyHeatmap({ data }) {

    const getColor = (status) => {
        switch (status) {
            case "current": return "#22c55e";
            case "patch": return "#86efac";
            case "minor": return "#f59e0b";
            case "major": return "#ef4444";
            default: return "#e5e7eb";
        }
    };

    return (
        <div className="heatmap-grid">
            {data.map((cell, i) => (
                <div
                    key={i}
                    className="heatmap-cell"
                    style={{ background: getColor(cell) }}
                />
            ))}
        </div>
    );
}