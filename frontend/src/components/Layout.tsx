import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";

import { clearSession, ACCESS_TOKEN_KEY, DISPLAY_NAME_KEY } from "../services/auth";

export function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const hasAccessToken = Boolean(localStorage.getItem(ACCESS_TOKEN_KEY));
  const showAuthenticatedNav = hasAccessToken;
  const displayName = localStorage.getItem(DISPLAY_NAME_KEY) ?? "Usuario";

  function handleLogout() {
    clearSession();
    navigate("/login");
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-block">
          <p className="eyebrow">MVP Base</p>
          <h1>School Circle</h1>
          {hasAccessToken ? <p className="header-subtitle">{displayName}</p> : null}
        </div>

        {showAuthenticatedNav ? (
          <nav className="app-nav">
            <Link to="/home">Home</Link>
            <Link to="/presence">Presença</Link>
            <Link to="/study-sessions">Estudo</Link>
            <Link to="/progress">Progresso</Link>
            <Link to="/groups">Grupos</Link>
            <Link to="/invites">Convites</Link>
            <Link to="/history">Histórico</Link>
            <Link to="/academic-profile">Perfil academico</Link>
            <Link to="/edit-profile">Editar Conta</Link>
            <button type="button" className="link-button" onClick={handleLogout}>
              Sair
            </button>
          </nav>
        ) : null}
      </header>

      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}
