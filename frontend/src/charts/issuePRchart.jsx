import {
    Chart as ChartJS,
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
    Legend
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
    Legend
);

export default function IssuePRChart({ data }) {

    const months = Object.keys(data.opened);

    const chartData = {
        labels: months,
        datasets: [
            {
                label: "Issues Opened",
                data: months.map(m => data.opened[m] || 0),
                backgroundColor: "rgba(83, 168, 255, 0.6)",
                borderColor: "#53A8FF",
                borderWidth: 1,
                borderRadius: 3,
            },
            {
                label: "Issues Closed",
                data: months.map(m => data.closed[m] || 0),
                backgroundColor: "rgba(0, 216, 255, 0.6)",
                borderColor: "#00D8FF",
                borderWidth: 1,
                borderRadius: 3,
            },
            {
                label: "PRs Merged",
                data: months.map(m => data.merged[m] || 0),
                backgroundColor: "rgba(39, 211, 255, 0.6)",
                borderColor: "#27D3FF",
                borderWidth: 1,
                borderRadius: 3,
            }
        ]
    };

    const options = {
        responsive: true,
        plugins: {
            legend: { labels: { color: '#9CB3CC' } },
        },
        scales: {
            x: { ticks: { color: '#9CB3CC' }, grid: { color: 'rgba(39, 211, 255, 0.06)' } },
            y: { ticks: { color: '#9CB3CC' }, grid: { color: 'rgba(39, 211, 255, 0.06)' } },
        },
    };

    return <Bar data={chartData} options={options} />;
}