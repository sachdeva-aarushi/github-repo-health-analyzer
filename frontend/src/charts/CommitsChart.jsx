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
                borderColor: '#27D3FF',
                backgroundColor: 'rgba(39, 211, 255, 0.1)',
                pointBackgroundColor: '#27D3FF',
                pointBorderColor: '#27D3FF',
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
                labels: { color: '#9CB3CC' },
            },
            title: {
                display: true,
                text: `Commit Activity — ${repository}`,
                font: { size: 14, weight: '600', family: 'Sora' },
                color: '#F4F8FF',
            },
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
            x: {
                ticks: { font: { size: 11 }, color: '#9CB3CC' },
                grid: { color: 'rgba(39, 211, 255, 0.06)' },
            },
            y: {
                beginAtZero: true,
                ticks: { stepSize: 1, font: { size: 11 }, color: '#9CB3CC' },
                grid: { color: 'rgba(39, 211, 255, 0.06)' },
            },
        },
    };

    return <Line data={data} options={options} />;
}

export default CommitsChart;
