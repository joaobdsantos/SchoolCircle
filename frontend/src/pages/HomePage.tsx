const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";


export function HomePage() {
  return (
    <section className="page-card">
      <p className="eyebrow">Projeto Inicial</p>
      <h2>Base pronta para evoluir o MVP</h2>
      <p>
        Este frontend foi criado apenas como estrutura mínima com Vite, React,
        TypeScript, React Router e Axios.
      </p>
      <p>
        Endpoint de infraestrutura esperado: <code>{apiUrl}/health/</code>
      </p>

      <div className="todo-box">
        <strong>TODOs futuros</strong>
        <p>Adicionar login, rotas protegidas e páginas reais do produto.</p>
      </div>
    </section>
  );
}
