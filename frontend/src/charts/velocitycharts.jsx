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
                tension: 0.3,
                fill: false
            }
        ]
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                display: true
            }
        },
        scales: {
            x: {
                ticks: {
                    display: false // hides messy week labels
                }
            }
        }
    };

    return <Line data={chartData} options={options} />;
}