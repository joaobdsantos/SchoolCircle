import { Link } from "react-router-dom";


export function NotFoundPage() {
  return (
    <section className="page-card">
      <p className="eyebrow">404</p>
      <h2>Página não encontrada</h2>
      <p>Esta rota ainda não existe no MVP inicial.</p>
      <Link to="/">Voltar para a home</Link>
    </section>
  );
}
