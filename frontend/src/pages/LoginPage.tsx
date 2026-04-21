import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";

import { ACCESS_TOKEN_KEY, login, REFRESH_TOKEN_KEY } from "../services/auth";

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (!email.trim() || !password.trim()) {
      setError("Preencha e-mail e senha.");
      return;
    }

    try {
      setIsSubmitting(true);
      const data = await login({
        email: email.trim().toLowerCase(),
        password,
      });

      localStorage.setItem(ACCESS_TOKEN_KEY, data.access);
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh);
      navigate("/home", { replace: true });
    } catch {
      setError("E-mail ou senha invalidos.");
    } finally {
      setIsSubmitting(false);
    }
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

        <button type="submit" style={{ marginTop: "1rem" }} disabled={isSubmitting}>
          {isSubmitting ? "Entrando..." : "Entrar"}
        </button>
      </form>

      <p style={{ marginTop: "1rem" }}>
        Não tem conta? <Link to="/register">Criar conta</Link>
      </p>
    </section>
  );
}
