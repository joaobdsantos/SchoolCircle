import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { listGroupRanking, type GroupRankingRow } from "../services/groups";

export function GroupRankingPage() {
  const { groupId } = useParams();
  const [ranking, setRanking] = useState<GroupRankingRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadRanking() {
      if (!groupId) {
        setError("Grupo nao informado.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const data = await listGroupRanking(groupId);
        setRanking(data);
      } catch {
        setError("Nao foi possivel carregar o ranking.");
      } finally {
        setLoading(false);
      }
    }

    loadRanking();
  }, [groupId]);

  return (
    <section className="page-card stack">
      <div className="toolbar">
        <div>
          <p className="eyebrow">Ranking</p>
          <h2>Pontuacao do grupo</h2>
        </div>
        <Link className="ghost-button" to={`/groups/${groupId}/members`}>
          Ver membros
        </Link>
      </div>

      {error ? <div className="notice error">{error}</div> : null}
      {loading ? <p className="muted">Carregando...</p> : null}

      <div className="stack">
        {ranking.map((entry) => (
          <article key={entry.user_id} className="stat-card">
            <div className="flex-between">
              <div>
                <p className="eyebrow">#{entry.rank}</p>
                <h3 style={{ margin: 0 }}>{entry.user_name}</h3>
                <p className="muted" style={{ marginBottom: 0 }}>
                  {entry.role} • Streak {entry.current_streak} dias
                </p>
              </div>
              <div className="stat-value" style={{ margin: 0 }}>
                {entry.group_points}
              </div>
            </div>
          </article>
        ))}

        {!loading && ranking.length === 0 ? <p className="muted">Sem participantes ativos ainda.</p> : null}
      </div>
    </section>
  );
}