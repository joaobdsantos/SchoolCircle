import { Link, useNavigate } from "react-router-dom";

import { clearSession, DISPLAY_NAME_KEY } from "../services/auth";

export function HomePage() {
  const navigate = useNavigate();
  const displayName = localStorage.getItem(DISPLAY_NAME_KEY) ?? "Usuario";

  function handleLogout() {
    clearSession();
    navigate("/login");
  }

  return (
    <section className="hero-card">
      <div className="hero-copy">
        <p className="eyebrow">Dashboard</p>
        <h2>Bem-vindo, {displayName}.</h2>
        <p>
          Acompanhe presença, estudo, grupos, progresso e convites a partir de um só painel.
        </p>

        <div className="hero-actions">
          <Link className="primary-button" to="/presence">
            Registrar presença
          </Link>
          <Link className="secondary-button" to="/study-sessions">
            Registrar estudo
          </Link>
          <button type="button" className="ghost-button" onClick={handleLogout}>
            Sair
          </button>
        </div>
      </div>

      <div className="hero-grid">
        <Link className="mini-card" to="/progress">
          <span>Progresso</span>
          <strong>Streak, pontos e gráfico</strong>
        </Link>
        <Link className="mini-card" to="/groups">
          <span>Grupos</span>
          <strong>Listar, criar e ver ranking</strong>
        </Link>
        <Link className="mini-card" to="/invites">
          <span>Convites</span>
          <strong>Aceitar ou recusar pendências</strong>
        </Link>
        <Link className="mini-card" to="/history">
          <span>Histórico</span>
          <strong>Revisar transações recentes</strong>
        </Link>
      </div>
    </section>
  );
}
