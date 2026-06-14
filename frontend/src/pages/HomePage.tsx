import { useNavigate } from "react-router-dom";
import { clearSession } from "../services/auth";

export function HomePage() {
  const navigate = useNavigate();

  function handleLogout() {
    clearSession();
    navigate("/login");
  }

  return (
    <section className="page-card">
      <p className="eyebrow">Home</p>
      <h2>Bem-vindo!</h2>
      <p>Que bom ter voce por aqui.</p>
      
      <div style={{ marginTop: "2rem" }}>
        <button onClick={handleLogout} style={{ backgroundColor: "#dc3545", color: "white" }}>
          Sair
        </button>
      </div>
    </section>
  );
}
