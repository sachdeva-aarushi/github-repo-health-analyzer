import { Line } from "react-chartjs-2";

export default function LorenzCurveChart({ data }) {
  return (
    <Line
      data={{
        labels: data.map(d => d.cumulative_contributors_pct),
        datasets: [
          {
            label: "Lorenz Curve",
            data: data.map(d => d.cumulative_share),
            borderColor: "blue",
            fill: false,
          },
          {
            label: "Perfect Equality",
            data: data.map(d => d.cumulative_contributors_pct),
            borderColor: "gray",
            borderDash: [5, 5],
            fill: false,
          }
        ]
      }}
      options={{
        scales: {
          x: { title: { display: true, text: "Cumulative % of Contributors" } },
          y: { title: { display: true, text: "Cumulative % of Commits" } }
        }
      }}
    />
  );
}