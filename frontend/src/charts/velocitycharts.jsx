import {
    Chart as ChartJS,
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement,
    Tooltip,
    Legend
} from "chart.js";

import { Line } from "react-chartjs-2";

ChartJS.register(
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement,
    Tooltip,
    Legend
);

export default function VelocityChart({ data }) {
    if (!data || !data.weeks || data.weeks.length === 0) {
        return <p style={{ color: '#94a3b8', textAlign: 'center' }}>No velocity data available.</p>;
    }

    const chartData = {
        labels: data.weeks,
        datasets: [
            {
                label: "Commits per Week",
                data: data.counts,
                tension: 0.4,
                fill: true,
                borderColor: "#4ecdc4",
                backgroundColor: "rgba(78, 205, 196, 0.15)",
                pointBackgroundColor: "#4ecdc4",
                pointBorderColor: "#fff",
                pointRadius: 4,
                pointHoverRadius: 6,
                borderWidth: 2,
            }
        ]
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                display: true,
                labels: {
                    color: "#e2e8f0"
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    display: false
                },
                grid: {
                    color: "rgba(255,255,255,0.05)"
                }
            },
            y: {
                ticks: {
                    color: "#94a3b8"
                },
                grid: {
                    color: "rgba(255,255,255,0.05)"
                }
            }
        }
    };

    return <Line data={chartData} options={options} />;
}