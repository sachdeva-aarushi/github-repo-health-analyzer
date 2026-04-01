import { Line } from "react-chartjs-2";
import InsightStrip from "../components/InsightStrip";

export default function RiskIssueChart({ data }) {
    if (!data) return null;

    const chartData = {
        labels: ["Current"],
        datasets: [
            { label: "Open Issues", data: [data.open_issues], borderColor: "#ef4444", backgroundColor: "rgba(239, 68, 68, 0.1)", fill: true, tension: 0.3 }
        ]
    };

    const levelColor = data.level === "HIGH" ? "red" : data.level === "MEDIUM" ? "orange" : "green";

    return (
        <div className={`risk-card border-${levelColor}`}>
            <div className="risk-card-header">
                <div className="risk-card-title-container">
                    Issue Accumulation Risk
                </div>
                <span className={`risk-badge bg-${levelColor}-light`}>{data.level}</span>
            </div>
            <div className="risk-card-subtitle">
                Is technical debt growing faster than it's resolved?
            </div>

            <div style={{ height: '192px', marginBottom: '24px' }}>
                <Line data={chartData} options={{ maintainAspectRatio: false }} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {data.insights.map((i, idx) => (
                    <InsightStrip key={idx} text={i} />
                ))}
                {data.insights.length === 0 && <InsightStrip text={`${data.open_issues} open issues`} />}
            </div>
        </div>
    );
}
