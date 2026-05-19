import { Link, Outlet, useLocation } from "react-router-dom";

import { ACCESS_TOKEN_KEY } from "../services/auth";

export function Layout() {
  const location = useLocation();
  const hasAccessToken = Boolean(localStorage.getItem(ACCESS_TOKEN_KEY));
  const showAuthenticatedNav =
    hasAccessToken && ["/home", "/academic-profile"].includes(location.pathname);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">MVP Base</p>
          <h1>School Circle</h1>
        </div>

        {showAuthenticatedNav ? (
          <nav className="app-nav">
            <Link to="/home">Home</Link>
            <Link to="/academic-profile">Perfil academico</Link>
          </nav>
        ) : null}
      </header>

      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}
