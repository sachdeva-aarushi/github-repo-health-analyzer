import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
    Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Register ALL Chart.js components (used across all chart files)
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

function CommitsChart({ dates, counts, repository }) {
    const data = {
        labels: dates,
        datasets: [
            {
                label: 'Commits per Day',
                data: counts,
                borderColor: '#0969da',
                backgroundColor: 'rgba(9, 105, 218, 0.1)',
                pointBackgroundColor: '#0969da',
                pointBorderColor: '#0969da',
                tension: 0.3,
                fill: true,
            },
        ],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: `Commit Activity — ${repository}`,
                font: { size: 14, weight: '600' },
            },
        },
        scales: {
            x: {
                ticks: { font: { size: 11 } },
                grid: { color: '#eee' },
            },
            y: {
                beginAtZero: true,
                ticks: { stepSize: 1, font: { size: 11 } },
                grid: { color: '#eee' },
            },
        },
    };

    return <Line data={data} options={options} />;
}

export default CommitsChart;
