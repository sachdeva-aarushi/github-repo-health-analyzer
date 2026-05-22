import { Bar } from "react-chartjs-2";

export default function WeekdayChart({ data }) {
    const labels = Object.keys(data);
    const values = Object.values(data);

    const chartData = {
        labels: labels,
        datasets: [
            {
                label: "Commits",
                data: values,
                backgroundColor: "rgba(39, 211, 255, 0.5)",
                borderColor: "#27D3FF",
                borderWidth: 1,
                borderRadius: 4,
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
            x: {
                ticks: { color: '#9CB3CC' },
                grid: { color: 'rgba(39, 211, 255, 0.06)' },
            },
            y: {
                ticks: { color: '#9CB3CC' },
                grid: { color: 'rgba(39, 211, 255, 0.06)' },
            },
        },
    };

    return <Bar data={chartData} options={options} />;
}