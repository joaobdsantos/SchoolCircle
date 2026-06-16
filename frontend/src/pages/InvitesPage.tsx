import { useEffect, useState } from "react";

import {
  acceptInvite,
  cancelInvite,
  createInvite,
  declineInvite,
  listGroups,
  listInvites,
  type GroupInvite,
  type StudyGroup,
} from "../services/groups";

export function InvitesPage() {
  const [invites, setInvites] = useState<GroupInvite[]>([]);
  const [groups, setGroups] = useState<StudyGroup[]>([]);
  const [groupId, setGroupId] = useState("");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [inviteData, groupData] = await Promise.all([listInvites(), listGroups()]);
        setInvites(inviteData);
        setGroups(groupData);
        if (!groupId && groupData.length > 0) {
          setGroupId(groupData[0].id);
        }
      } catch {
        setError("Nao foi possivel carregar os convites.");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  async function refreshInvites() {
    const data = await listInvites();
    setInvites(data);
  }

  async function handleCreateInvite(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!groupId || !recipientEmail.trim()) {
      setError("Selecione um grupo e informe o email do destinatario.");
      return;
    }

    try {
      setIsSubmitting(true);
      await createInvite({ group: groupId, sent_to_email: recipientEmail.trim().toLowerCase() });
      setSuccess("Convite enviado com sucesso.");
      setRecipientEmail("");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Nao foi possivel enviar o convite.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleAction(action: "accept" | "decline" | "cancel", inviteId: string) {
    try {
      if (action === "accept") {
        await acceptInvite(inviteId);
      } else if (action === "decline") {
        await declineInvite(inviteId);
      } else {
        await cancelInvite(inviteId);
      }

      setInvites((current) => current.filter((invite) => invite.id !== inviteId));
    } catch (actionError) {
      setError(actionError instanceof Error ? actionError.message : "Nao foi possivel concluir a acao.");
    }
  }

  return (
    <section className="stack">
      <div className="toolbar">
        <div>
          <p className="eyebrow">Convites</p>
          <h2>Gerenciar convites de grupo</h2>
        </div>
        <span className="badge">Pendentes</span>
      </div>

      <div className="flow-grid">
        <form className="page-card stack" onSubmit={handleCreateInvite}>
          <div>
            <p className="eyebrow">Novo convite</p>
            <h3>Enviar convite por UUID</h3>
          </div>

          {error ? <div className="notice error">{error}</div> : null}
          {success ? <div className="notice success">{success}</div> : null}

          <div>
            <label htmlFor="invite-group">Grupo</label>
            <select id="invite-group" value={groupId} onChange={(event) => setGroupId(event.target.value)}>
              <option value="">Selecione</option>
              {groups.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="invite-recipient">Email do destinatario</label>
            <input
              id="invite-recipient"
              type="email"
              value={recipientEmail}
              onChange={(event) => setRecipientEmail(event.target.value)}
              placeholder="usuario@exemplo.com"
              required
            />
          </div>

          <p className="table-note">
            O backend resolve o destinatario pelo email cadastrado e cria o convite para esse usuario.
          </p>

          <div className="form-actions">
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Enviando..." : "Enviar convite"}
            </button>
          </div>
        </form>

        <div className="page-card stack">
          <div className="flex-between">
            <div>
              <p className="eyebrow">Pendentes</p>
              <h3>Convites recebidos</h3>
            </div>
            <button type="button" className="ghost-button" onClick={() => refreshInvites()}>
              Atualizar
            </button>
          </div>

          {loading ? <p className="muted">Carregando...</p> : null}

          <div className="stack">
            {invites.map((invite) => (
              <article key={invite.id} className="invite-card stack">
                <div className="flex-between">
                  <div>
                    <h4 style={{ margin: 0 }}>{invite.group_name}</h4>
                    <p className="muted" style={{ marginBottom: 0 }}>
                      Convidado por {invite.sent_by_name} em {new Date(invite.sent_at).toLocaleDateString("pt-BR")}
                    </p>
                  </div>
                  <span className="badge warn">Pendente</span>
                </div>

                <div className="segment">
                  <button type="button" onClick={() => handleAction("accept", invite.id)}>
                    Aceitar
                  </button>
                  <button type="button" className="ghost-button" onClick={() => handleAction("decline", invite.id)}>
                    Recusar
                  </button>
                  <button type="button" className="secondary-button" onClick={() => handleAction("cancel", invite.id)}>
                    Cancelar
                  </button>
                </div>
              </article>
            ))}

            {!loading && invites.length === 0 ? <p className="muted">Sem convites pendentes.</p> : null}
          </div>
        </div>
      </div>
    </section>
  );
}