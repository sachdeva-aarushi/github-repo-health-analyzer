export default function MaintainerWorkload({ data }) {

    return (
        <div className="workload-container">
            {data.map((dev, i) => (
                <div key={i} className="workload-row">

                    <span className="dev-name">{dev.name}</span>

                    <div className="workload-bar-bg">
                        <div
                            className="workload-bar-fill"
                            style={{ width: `${dev.percentage}%` }}
                        />
                    </div>

                    <span>{dev.percentage}%</span>

                </div>
            ))}
        </div>
    );
}