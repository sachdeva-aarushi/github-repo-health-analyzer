import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

function CommitsChart({ dates, counts, repository }) {
    // Prepare data for Chart.js
    const data = {
        labels: dates,
        datasets: [
            {
                label: 'Commits per Day',
                data: counts,
                borderColor: '#4ecdc4',
                backgroundColor: 'rgba(78, 205, 196, 0.15)',
                pointBackgroundColor: '#4ecdc4',
                pointBorderColor: '#4ecdc4',
                pointHoverBackgroundColor: '#7fffe6',
                pointHoverBorderColor: '#7fffe6',
                tension: 0.3,
                fill: true,
            },
        ],
    };

    // Chart configuration
    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    color: '#8fa4c4',
                    font: { family: 'Inter, sans-serif' },
                },
            },
            title: {
                display: true,
                text: `Commit Activity — ${repository}`,
                color: '#e8edf5',
                font: {
                    family: 'Space Mono, monospace',
                    size: 14,
                    weight: '600',
                },
            },
        },
        scales: {
            x: {
                ticks: { color: '#506380', font: { size: 11 } },
                grid: { color: 'rgba(78, 205, 196, 0.06)' },
            },
            y: {
                beginAtZero: true,
                ticks: { stepSize: 1, color: '#506380', font: { size: 11 } },
                grid: { color: 'rgba(78, 205, 196, 0.06)' },
            },
        },
    };

    return <Line data={data} options={options} />;
}

export default CommitsChart;
