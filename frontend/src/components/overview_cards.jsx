export default function OverviewCards({ data }) {
    return (
        <div className="overview-grid">

            <div className="card">
                Stars
                <h2>{data.stars}</h2>
            </div>

            <div className="card">
                Files
                <h2>{data.total_files}</h2>
            </div>

            <div className="card">
                Folders
                <h2>{data.total_folders}</h2>
            </div>

            <div className="card">
                Tech Stack
                <h2>{data.tech_stack.join(", ")}</h2>
            </div>

            <div className="card">
                Pull Requests
                <h2>{data.total_pull_requests}</h2>
            </div>

            <div className="card">
                Issues
                <h2>{data.total_issues}</h2>
            </div>

        </div>
    );
}