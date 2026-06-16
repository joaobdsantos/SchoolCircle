import { useEffect, useState } from "react";

import { getUserProgress, listPointTransactions, type PointTransaction, type UserProgress } from "../services/gamification";

type ChartPoint = {
  date: string;
  points: number;
};

function formatDate(value: string | null): string {
  if (!value) {
    return "Sem registro";
  }

  return new Date(value).toLocaleDateString("pt-BR");
}

function buildChartData(transactions: PointTransaction[]): ChartPoint[] {
  const grouped = new Map<string, number>();

  transactions.forEach((transaction) => {
    const dateKey = new Date(transaction.created_at).toLocaleDateString("pt-BR");
    grouped.set(dateKey, (grouped.get(dateKey) ?? 0) + transaction.points);
  });

  return Array.from(grouped.entries())
    .map(([date, points]) => ({ date, points }))
    .sort((left, right) => {
      const [ld, lm, ly] = left.date.split("/").map(Number);
      const [rd, rm, ry] = right.date.split("/").map(Number);
      return new Date(ly, lm - 1, ld).getTime() - new Date(ry, rm - 1, rd).getTime();
    });
}

export function ProgressPage() {
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [transactions, setTransactions] = useState<PointTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError("");
        const [progressData, transactionData] = await Promise.all([
          getUserProgress(),
          listPointTransactions(),
        ]);

        setProgress(progressData);
        setTransactions(transactionData);
      } catch {
        setError("Nao foi possivel carregar o progresso.");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const chartData = buildChartData(transactions.slice(0, 30));
  const maxPoints = Math.max(...chartData.map((item) => item.points), 1);

  if (loading) {
    return (
      <section className="page-card">
        <p className="eyebrow">Progresso</p>
        <h2>Carregando...</h2>
      </section>
    );
  }

  if (!progress) {
    return (
      <section className="page-card">
        <p className="eyebrow">Progresso</p>
        <h2>Erro</h2>
        <p>{error || "Nao foi possivel carregar o progresso."}</p>
      </section>
    );
  }

  return (
    <section className="stack">
      <div className="toolbar">
        <div>
          <p className="eyebrow">Progresso</p>
          <h2>Seu resumo de desempenho</h2>
        </div>
        <span className="badge">Ultimas transacoes</span>
      </div>

      {error ? <div className="notice error">{error}</div> : null}

      <div className="stats-grid">
        <article className="stat-card">
          <p className="muted">Streak atual</p>
          <p className="stat-value">{progress.current_streak}</p>
          <p className="muted">Ultima atividade: {formatDate(progress.last_valid_activity_date)}</p>
        </article>

        <article className="stat-card">
          <p className="muted">Maior streak</p>
          <p className="stat-value">{progress.longest_streak}</p>
          <p className="muted">Dias consecutivos maximos</p>
        </article>

        <article className="stat-card">
          <p className="muted">Total de pontos</p>
          <p className="stat-value">{progress.total_points}</p>
          <p className="muted">Acumulado geral</p>
        </article>
      </div>

      <div className="grid-2">
        <article className="chart-card">
          <div className="flex-between">
            <div>
              <p className="eyebrow">Grafico</p>
              <h3>Evolucao por dia</h3>
            </div>
            <span className="badge info">30 dias</span>
          </div>

          {chartData.length > 0 ? (
            <div className="chart-bars">
              {chartData.map((item) => (
                <div key={item.date} className="chart-column">
                  <div className="chart-bar-track">
                    <div
                      className="chart-bar-fill"
                      style={{ height: `${(item.points / maxPoints) * 100}%` }}
                      title={`${item.points} pontos`}
                    />
                  </div>
                  <div className="chart-label">
                    <div className="chart-value">{item.points}</div>
                    <div>{item.date}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="muted">Sem dados ainda.</p>
          )}
        </article>

        <article className="list-card">
          <div className="flex-between">
            <div>
              <p className="eyebrow">Historico</p>
              <h3>Atividades recentes</h3>
            </div>
            <span className="badge">{transactions.length} itens</span>
          </div>

          <div className="stack">
            {transactions.slice(0, 10).map((transaction) => (
              <div key={transaction.id} className="notice">
                <div className="flex-between">
                  <strong>
                    {transaction.source_type === "ATTENDANCE" ? "Presença" : "Estudo"}
                  </strong>
                  <span className="badge">+{transaction.points}</span>
                </div>
                <p className="muted" style={{ marginBottom: 0 }}>
                  {transaction.reason}
                </p>
                <p className="table-note" style={{ marginBottom: 0 }}>
                  {new Date(transaction.created_at).toLocaleString("pt-BR")}
                </p>
              </div>
            ))}
          </div>
        </article>
      </div>
    </section>
  );
}