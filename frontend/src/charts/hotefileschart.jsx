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

export default function HotFilesChart({ data }) {

    if (!data || !data.files) return null;

    const chartData = {
        labels: data.files,
        datasets: [
            {
                label: "File Changes",
                data: data.counts,
                backgroundColor: "#4ecdc4"
            }
        ]
    };

    return <Bar data={chartData} />;
}