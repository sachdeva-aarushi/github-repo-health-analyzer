import { NavLink } from 'react-router-dom';

function Navbar({ owner, repo }) {
    const query = owner && repo
        ? `?owner=${encodeURIComponent(owner)}&repo=${encodeURIComponent(repo)}`
        : '';

    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <NavLink to="/" className="navbar-logo">
                    <img src="/logo.png" alt="GitIntel logo" className="navbar-logo-img" />
                    GitIntel
                </NavLink>
            </div>
            {owner && repo && (
                <div className="navbar-repo-name">
                    {owner} / <span>{repo}</span>
                </div>
            )}
            <div className="navbar-links">
                <NavLink
                    to={`/dashboard${query}`}
                    className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
                >
                    Dashboard
                </NavLink>
                <NavLink
                    to={`/health${query}`}
                    className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
                >
                    Health
                </NavLink>
                <NavLink
                    to={`/risk${query}`}
                    className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
                >
                    Risk
                </NavLink>
                <NavLink
                    to={`/structure${query}`}
                    className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
                >
                    Structure
                </NavLink>
            </div>
        </nav>
    );
}

export default Navbar;
