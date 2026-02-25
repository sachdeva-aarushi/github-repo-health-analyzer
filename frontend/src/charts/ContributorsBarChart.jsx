import { Bar } from "react-chartjs-2";

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