import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { updateUserProfile } from "../services/userProfile";

export function EditProfilePage() {
  const navigate = useNavigate();
  
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const hasProfileUpdate = name.trim() || email.trim();
    const hasPasswordUpdate = newPassword.trim();

    if (!hasProfileUpdate && !hasPasswordUpdate) {
      setError("Preencha pelo menos um campo para atualizar.");
      return;
    }

    if (!password.trim()) {
      setError("Informe sua senha atual para confirmar.");
      return;
    }

    if (name.trim() && name.trim().length < 3) {
      setError("Nome deve ter pelo menos 3 caracteres.");
      return;
    }

    if (email.trim() && !isValidEmail(email.trim())) {
      setError("Email invalido.");
      return;
    }

    if (newPassword.trim()) {
      if (newPassword === password) {
        setError("Nova senha deve ser diferente da senha atual.");
        return;
      }

      if (newPassword !== confirmPassword) {
        setError("Senhas nao conferem.");
        return;
      }
    }

    try {
      setIsSubmitting(true);
      const payload: Record<string, string> = {
        password: password,
      };
      
      if (name.trim()) {
        payload.name = name.trim();
      }
      if (email.trim()) {
        payload.email = email.trim();
      }
      if (newPassword.trim()) {
        payload.new_password = newPassword;
      }

      await updateUserProfile(payload);
      setSuccess("Perfil atualizado com sucesso!");
      
      setTimeout(() => {
        navigate("/home");
      }, 1500);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Nao foi possivel atualizar o perfil.";
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  }

  function isValidEmail(value: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  }

  return (
    <section className="page-card">
      <h2>Editar Perfil</h2>

      {error && <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>}
      {success && <div style={{ color: "green", marginBottom: "1rem" }}>{success}</div>}

      <form onSubmit={handleSubmit}>
        <fieldset style={{ border: "1px solid #ccc", padding: "1rem", borderRadius: "4px" }}>
          <legend>Informacoes da Conta</legend>
          
          <div>
            <label htmlFor="name">Nome</label>
            <br />
            <input
              id="name"
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Seu nome"
            />
          </div>

          <div style={{ marginTop: "0.75rem" }}>
            <label htmlFor="email">Email</label>
            <br />
            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="seu@email.com"
            />
          </div>
        </fieldset>

        <fieldset style={{ border: "1px solid #ccc", padding: "1rem", borderRadius: "4px", marginTop: "1.5rem" }}>
          <legend>Alterar Senha</legend>
          
          <div>
            <label htmlFor="new-password">Nova Senha (opcional)</label>
            <br />
            <input
              id="new-password"
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              placeholder="Nova senha"
            />
          </div>

          <div style={{ marginTop: "0.75rem" }}>
            <label htmlFor="confirm-password">Confirmar Nova Senha</label>
            <br />
            <input
              id="confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="Confirme a nova senha"
            />
          </div>
        </fieldset>

        <fieldset style={{ border: "1px solid #ccc", padding: "1rem", borderRadius: "4px", marginTop: "1.5rem" }}>
          <legend>Confirmacao</legend>
          
          <div>
            <label htmlFor="password">Senha Atual (obrigatoria para confirmar)</label>
            <br />
            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Sua senha atual"
            />
          </div>
        </fieldset>

        <div style={{ marginTop: "1.5rem" }}>
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Salvando..." : "Salvar"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/home")}
            style={{ marginLeft: "0.5rem" }}
          >
            Cancelar
          </button>
        </div>
      </form>
    </section>
  );
}
