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
                backgroundColor: "rgba(75,192,192,0.6)"
            }
        ]
    };

    return <Bar data={chartData} />;
}