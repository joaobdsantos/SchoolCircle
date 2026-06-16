import { useEffect, useMemo, useState } from "react";

import { listPointTransactions, type PointTransaction } from "../services/gamification";

type FilterKind = "ALL" | "ATTENDANCE" | "STUDY_SESSION";

export function HistoryPage() {
  const [transactions, setTransactions] = useState<PointTransaction[]>([]);
  const [filter, setFilter] = useState<FilterKind>("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadTransactions() {
      try {
        setLoading(true);
        const data = await listPointTransactions();
        setTransactions(data);
      } catch {
        setError("Nao foi possivel carregar o historico.");
      } finally {
        setLoading(false);
      }
    }

    loadTransactions();
  }, []);

  const filteredTransactions = useMemo(() => {
    if (filter === "ALL") {
      return transactions;
    }

    return transactions.filter((transaction) => transaction.source_type === filter);
  }, [filter, transactions]);

  return (
    <section className="page-card stack">
      <div className="toolbar">
        <div>
          <p className="eyebrow">Historico</p>
          <h2>Transacoes de pontos</h2>
        </div>
        <div className="segment">
          <button type="button" className={filter === "ALL" ? "active" : ""} onClick={() => setFilter("ALL")}>
            Todas
          </button>
          <button type="button" className={filter === "ATTENDANCE" ? "active" : ""} onClick={() => setFilter("ATTENDANCE")}>
            Presenca
          </button>
          <button type="button" className={filter === "STUDY_SESSION" ? "active" : ""} onClick={() => setFilter("STUDY_SESSION")}>
            Estudo
          </button>
        </div>
      </div>

      {error ? <div className="notice error">{error}</div> : null}
      {loading ? <p className="muted">Carregando...</p> : null}

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Data</th>
              <th>Tipo</th>
              <th>Descricao</th>
              <th>Pontos</th>
            </tr>
          </thead>
          <tbody>
            {filteredTransactions.map((transaction) => (
              <tr key={transaction.id}>
                <td>{new Date(transaction.created_at).toLocaleDateString("pt-BR")}</td>
                <td>{transaction.source_type === "ATTENDANCE" ? "Presença" : "Estudo"}</td>
                <td>{transaction.reason}</td>
                <td>+{transaction.points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {!loading && filteredTransactions.length === 0 ? (
        <p className="muted">Nenhuma transacao encontrada.</p>
      ) : null}
    </section>
  );
}