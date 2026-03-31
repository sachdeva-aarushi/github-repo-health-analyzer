import { useEffect, useState } from "react";
import { getRisk } from "../api";
import Navbar from '../components/Navbar';
import RiskBusFactorChart from "../charts/RiskBusFactorChart";
import RiskSinglePointTable from "../charts/RiskSinglePointTable";
import RiskPRChart from "../charts/RiskPRChart";
import RiskIssueChart from "../charts/RiskIssueChart";
import RiskActivityChart from "../charts/RiskActivityChart";
import RiskResponsivenessChart from "../charts/RiskResponsivenessChart";
import {
    Chart as ChartJS, ArcElement, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement);

const SectionTitle = ({ children }) => (
    <div className="risk-section-title">
        <div className="risk-section-text">{children}</div>
        <div className="risk-section-line"></div>
    </div>
);

const RiskCard = ({ title, level, value }) => {
    const levelColor = level === "HIGH" ? "red" : level === "MEDIUM" ? "orange" : "green";
    return (
        <div className={`risk-summary-card border-${levelColor}`}>
            <div className="risk-summary-title">
                {title}
            </div>
            <div className={`risk-summary-level text-${levelColor}`}>{level}</div>
            <div className="risk-summary-value">{value}</div>
        </div>
    );
};

const Risk = () => {
    const [data, setData] = useState(null);

    const owner = "facebook";
    const repo = "react";

    useEffect(() => {
        getRisk(owner, repo).then(res => setData(res));
    }, []);

    if (!data) return <div style={{ padding: '24px', color: '#64748b' }}>Loading risk analysis...</div>;

    const summary = data.summary;

    return (
        <div className="app-container">
            <Navbar owner={owner} repo={repo} />

            <div className="risk-page-container" style={{ padding: 0, marginTop: '24px' }}>
                <div className="risk-summary-grid">
                    <RiskCard title="Bus Factor" {...summary.bus_factor} />
                    <RiskCard title="PR Backlog" {...summary.pr_backlog} />
                    <RiskCard title="Trend Risk" {...summary.trend} />
                    <RiskCard title="Maintainer Load" {...summary.maintainer_load} />
                    <RiskCard title="Responsiveness" {...summary.responsiveness} />
                </div>

                <section>
                    <SectionTitle>CONTRIBUTOR & OWNERSHIP RISK</SectionTitle>
                    <div className="risk-grid">
                        <RiskBusFactorChart data={data.bus_factor_detail} />
                        <RiskSinglePointTable data={data.bus_factor_detail} />
                    </div>
                </section>

                <section>
                    <SectionTitle>BACKLOG & ISSUE RISK</SectionTitle>
                    <div className="risk-grid">
                        <RiskPRChart data={data.pr_risk} />
                        <RiskIssueChart data={data.issue_risk} />
                    </div>
                </section>

                <section>
                    <SectionTitle>ACTIVITY & RESPONSIVENESS RISK</SectionTitle>
                    <div className="risk-grid">
                        <RiskActivityChart data={data.activity_risk} />
                        <RiskResponsivenessChart data={data.responsiveness_detail} />
                    </div>
                </section>
            </div>
        </div>
    );
};

export default Risk;