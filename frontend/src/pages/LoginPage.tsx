import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (!email.trim() || !password.trim()) {
      setError("Preencha e-mail e senha.");
      return;
    }

    // TODO: Integrar chamada real de login com a API.
    alert("Login válido no frontend (sem integração com backend ainda).");
  }

  return (
    <section className="page-card">
      <h2>Entrar</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="login-email">E-mail</label>
          <br />
          <input
            id="login-email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>

        <div style={{ marginTop: "0.75rem" }}>
          <label htmlFor="login-password">Senha</label>
          <br />
          <input
            id="login-password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>

        {error ? (
          <p style={{ color: "#b42318", marginTop: "0.75rem" }}>{error}</p>
        ) : null}

        <button type="submit" style={{ marginTop: "1rem" }}>
          Entrar
        </button>
      </form>

      <p style={{ marginTop: "1rem" }}>
        Não tem conta? <Link to="/register">Criar conta</Link>
      </p>
    </section>
  );
}
