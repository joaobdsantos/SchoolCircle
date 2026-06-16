import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getUserProgress } from "../services/learning";
import {
  leaveGroupMember,
  listGroupMembers,
  type GroupMembership,
} from "../services/groups";

export function GroupMembersPage() {
  const { groupId } = useParams();
  const navigate = useNavigate();
  const [members, setMembers] = useState<GroupMembership[]>([]);
  const [currentUserId, setCurrentUserId] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMembers() {
      if (!groupId) {
        setError("Grupo nao informado.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const [membersData, progressData] = await Promise.all([
          listGroupMembers(groupId),
          getUserProgress(),
        ]);
        setMembers(membersData);
        setCurrentUserId(progressData.user);
      } catch {
        setError("Nao foi possivel carregar os membros. Voce precisa ser membro ativo do grupo.");
      } finally {
        setLoading(false);
      }
    }

    loadMembers();
  }, [groupId]);

  async function handleLeave(membershipId: string) {
    if (!groupId) {
      return;
    }

    try {
      await leaveGroupMember(groupId, membershipId);
      setMembers((current) => current.filter((member) => member.id !== membershipId));
    } catch (leaveError) {
      setError(leaveError instanceof Error ? leaveError.message : "Nao foi possivel sair do grupo.");
    }
  }

  return (
    <section className="page-card stack">
      <div className="toolbar">
        <div>
          <p className="eyebrow">Membros</p>
          <h2>Participantes do grupo</h2>
        </div>
        <div className="segment">
          <Link className="ghost-button" to="/groups">
            Voltar
          </Link>
          <button type="button" className="secondary-button" onClick={() => navigate(`/groups/${groupId}/ranking`)}>
            Ver ranking
          </button>
        </div>
      </div>

      {error ? <div className="notice error">{error}</div> : null}

      {loading ? <p className="muted">Carregando...</p> : null}

      <div className="stack">
        {members.map((member) => (
          <article key={member.id} className="invite-card">
            <div className="flex-between">
              <div>
                <h4 style={{ margin: 0 }}>{member.user_name}</h4>
                <p className="muted" style={{ marginBottom: 0 }}>
                  {member.role} • {member.group_points} pontos • Rank {member.rank ?? "-"}
                </p>
              </div>
              {member.role === "OWNER" ? <span className="badge">Owner</span> : <span className="badge info">Membro</span>}
            </div>

            <div className="form-actions">
              {member.role !== "OWNER" && member.user === currentUserId ? (
                <button type="button" onClick={() => handleLeave(member.id)}>
                  Sair do grupo
                </button>
              ) : null}
            </div>
          </article>
        ))}

        {!loading && members.length === 0 ? <p className="muted">Nenhum membro encontrado.</p> : null}
      </div>
    </section>
  );
}