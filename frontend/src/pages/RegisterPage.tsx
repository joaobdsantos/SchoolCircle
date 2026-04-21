import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

export function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (
      !name.trim() ||
      !email.trim() ||
      !password.trim() ||
      !confirmPassword.trim()
    ) {
      setError("Preencha todos os campos.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Senha e confirmar senha precisam ser iguais.");
      return;
    }

    // TODO: Integrar chamada real de criação de conta com a API.
    alert("Cadastro válido no frontend (sem integração com backend ainda).");
  }

  return (
    <section className="page-card">
      <h2>Criar conta</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="register-name">Nome</label>
          <br />
          <input
            id="register-name"
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </div>

        <div style={{ marginTop: "0.75rem" }}>
          <label htmlFor="register-email">E-mail</label>
          <br />
          <input
            id="register-email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>

        <div style={{ marginTop: "0.75rem" }}>
          <label htmlFor="register-password">Senha</label>
          <br />
          <input
            id="register-password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>

        <div style={{ marginTop: "0.75rem" }}>
          <label htmlFor="register-confirm-password">Confirmar senha</label>
          <br />
          <input
            id="register-confirm-password"
            type="password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
          />
        </div>

        {error ? (
          <p style={{ color: "#b42318", marginTop: "0.75rem" }}>{error}</p>
        ) : null}

        <button type="submit" style={{ marginTop: "1rem" }}>
          Criar conta
        </button>
      </form>

      <p style={{ marginTop: "1rem" }}>
        Já tem conta? <Link to="/login">Entrar</Link>
      </p>
    </section>
  );
}
