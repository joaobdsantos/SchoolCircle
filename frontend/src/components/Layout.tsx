import { Link, Outlet } from "react-router-dom";


export function Layout() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">MVP Base</p>
          <h1>School Circle</h1>
        </div>

        <nav className="app-nav">
          <Link to="/">Home</Link>
        </nav>
      </header>

      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}
