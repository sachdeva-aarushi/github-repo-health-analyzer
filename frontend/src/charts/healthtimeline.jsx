import {
    Chart as ChartJS,
    LineElement,
    PointElement,
    LinearScale,
    CategoryScale,
    Tooltip,
    Legend
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
    LineElement,
    PointElement,
    LinearScale,
    CategoryScale,
    Tooltip,
    Legend
);

export default function HealthTimeline({ data }) {

    const labels = data.map(d => d.month);
    const values = data.map(d => d.commits);

    const chartData = {
        labels,
        datasets: [
            {
                label: "Commits",
                data: values,
                borderColor: "#53A8FF",
                backgroundColor: "rgba(83, 168, 255, 0.1)",
                tension: 0.3,
                fill: true,
            }
        ]
    };

    const options = {
        responsive: true,
        plugins: {
            legend: { labels: { color: '#9CB3CC' } },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y >= 100) {
                            label += '100+';
                        } else {
                            label += context.parsed.y;
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            x: { ticks: { color: '#9CB3CC' }, grid: { color: 'rgba(39, 211, 255, 0.06)' } },
            y: { ticks: { color: '#9CB3CC' }, grid: { color: 'rgba(39, 211, 255, 0.06)' } },
        },
    };

    return <Line data={chartData} options={options} />;
}