import { Bar } from "react-chartjs-2";
import { Pie } from "react-chartjs-2";

export default function ContributorsBarChart({ data }) {
    return (
        <Bar
            data={{
                labels: data.map(c => c.login),
                datasets: [
                    {
                        label: "Commits",
                        data: data.map(c => c.contributions),
                        backgroundColor: "rgba(11, 119, 161, 0.6)"
                    }
                ]
            }}
        />

    );
}
export default function ContributorsPieChart({ data }) {
    return (
        <Pie
            data={{
                labels: data.map(c => c.login),
                datasets: [
                    {
                        data: data.map(c => c.percentage),
                        backgroundColor: data.map(() =>
                            `hsl(${Math.random() * 360}, 70%, 60%)`
                        )
                    }
                ]
            }}
        />
    );
}