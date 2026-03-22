import {
    LineChart, Line, XAxis, YAxis,
    Tooltip, CartesianGrid, ResponsiveContainer
} from "recharts";

export default function VelocityChart({ data }) {

    const chartData = data.weeks.map((week, i) => ({
        week,
        commits: data.counts[i]
    }));

    return (
        <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer>
                <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="week" hide />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="commits" />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}