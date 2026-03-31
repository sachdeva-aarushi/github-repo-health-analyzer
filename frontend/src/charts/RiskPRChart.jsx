import { Line } from "react-chartjs-2";
import InsightStrip from "../components/InsightStrip";

export default function RiskPRChart({ data }) {
    if (!data) return null;

    const chartData = {
        labels: ["W1", "W2", "W3", "W4"],
        datasets: [
            { label: "Open PRs", data: [40, 60, 90, data.open_prs], borderColor: "#3b82f6", backgroundColor: "rgba(59, 130, 246, 0.1)", fill: true, tension: 0.3 }
        ]
    };

    const levelColor = data.level === "HIGH" ? "red" : data.level === "MEDIUM" ? "orange" : "green";

    return (
        <div className={`risk-card border-${levelColor}`}>
            <div className="risk-card-header">
                <div className="risk-card-title-container">
                    PR Backlog Risk
                </div>
                <span className={`risk-badge bg-${levelColor}-light`}>{data.level}</span>
            </div>
            <div className="risk-card-subtitle">
                Open PRs vs merge rate — is code review a bottleneck?
            </div>

            <div style={{ height: '192px', marginBottom: '24px' }}>
                <Line data={chartData} options={{ maintainAspectRatio: false }} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {data.insights.map((i, idx) => (
                    <InsightStrip key={idx} text={i} />
                ))}
                {data.insights.length === 0 && <InsightStrip text={`${data.open_prs} open PRs found`} />}
            </div>
        </div>
    );
}
