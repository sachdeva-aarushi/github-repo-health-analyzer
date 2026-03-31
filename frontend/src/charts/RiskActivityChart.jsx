import { Line } from "react-chartjs-2";

export default function RiskActivityChart({ data }) {
    if (!data) return null;

    const chartData = {
        labels: ["W1", "W2", "W3", "W4"],
        datasets: [
            { label: "Commits", data: [30, 25, 20, 18], borderColor: "#10b981", backgroundColor: "rgba(16, 185, 129, 0.1)", fill: true, tension: 0.3 }
        ]
    };

    const levelColor = data.level === "HIGH" ? "red" : data.level === "MEDIUM" ? "orange" : "green";

    return (
        <div className={`risk-card border-${levelColor}`}>
            <div className="risk-card-header">
                <div className="risk-card-title-container">
                    Activity Drop Risk
                </div>
                <span className={`risk-badge bg-${levelColor}-light`}>{data.level}</span>
            </div>
            <div className="risk-card-subtitle">
                Is the project at risk of going inactive? Commit frequency over 12 months.
            </div>

            <div style={{ height: '192px', marginBottom: '24px' }}>
                <Line data={chartData} options={{ maintainAspectRatio: false }} />
            </div>

        </div>
    );
}
