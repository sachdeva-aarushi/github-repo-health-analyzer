import { Bar } from "react-chartjs-2";
import { Pie } from "react-chartjs-2";

const BLUE_PALETTE = [
    '#27D3FF', '#53A8FF', '#1C5D7A', '#0B3046', '#102033',
    '#27D3FF', '#53A8FF', '#1C5D7A', '#0B3046', '#102033',
];

function ContributorsBarChart({ data }) {
    return (
        <Bar
            data={{
                labels: data.map(c => c.login),
                datasets: [
                    {
                        label: "Commits",
                        data: data.map(c => c.contributions),
                        backgroundColor: "rgba(39, 211, 255, 0.6)",
                        borderColor: "#27D3FF",
                        borderWidth: 1,
                        borderRadius: 4,
                    }
                ]
            }}
            options={{
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
            }}
        />

    );
}

function ContributorsPieChart({ data }) {
    return (
        <Pie
            data={{
                labels: data.map(c => c.login),
                datasets: [
                    {
                        data: data.map(c => c.percentage),
                        backgroundColor: BLUE_PALETTE.slice(0, data.length),
                        borderWidth: 2,
                        borderColor: '#091525',
                    }
                ]
            }}
            options={{
                plugins: {
                    legend: { labels: { color: '#9CB3CC', usePointStyle: true, boxWidth: 8 } },
                },
            }}
        />
    );
}

export { ContributorsPieChart };
export default ContributorsBarChart;