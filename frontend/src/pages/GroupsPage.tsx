import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  createGroup,
  listGroups,
  type StudyGroup,
} from "../services/groups";

export function GroupsPage() {
  const navigate = useNavigate();
  const [groups, setGroups] = useState<StudyGroup[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    async function loadGroups() {
      try {
        setLoading(true);
        const data = await listGroups();
        setGroups(data);
      } catch {
        setError("Nao foi possivel carregar os grupos.");
      } finally {
        setLoading(false);
      }
    }

    loadGroups();
  }, []);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!name.trim()) {
      setError("Informe o nome do grupo.");
      return;
    }

    try {
      setIsCreating(true);
      const created = await createGroup({
        name: name.trim(),
        description: description.trim(),
      });

      setGroups((current) => [created, ...current]);
      setName("");
      setDescription("");
      setSuccess("Grupo criado com sucesso.");
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Nao foi possivel criar o grupo.");
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <section className="stack">
      <div className="toolbar">
        <div>
          <p className="eyebrow">Grupos</p>
          <h2>Listar e criar grupos</h2>
        </div>
        <Link to="/invites" className="secondary-button">
          Ver convites
        </Link>
      </div>

      <div className="flow-grid">
        <form className="page-card stack" onSubmit={handleSubmit}>
          <div>
            <p className="eyebrow">Novo grupo</p>
            <h3>Criar um grupo</h3>
          </div>

          {error ? <div className="notice error">{error}</div> : null}
          {success ? <div className="notice success">{success}</div> : null}

          <div>
            <label htmlFor="group-name">Nome</label>
            <input
              id="group-name"
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Grupo de estudos"
              required
            />
          </div>

          <div>
            <label htmlFor="group-description">Descricao</label>
            <textarea
              id="group-description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Objetivo, turma, materia..."
            />
          </div>

          <div className="form-actions">
            <button type="submit" disabled={isCreating}>
              {isCreating ? "Criando..." : "Criar grupo"}
            </button>
          </div>
        </form>

        <div className="page-card stack">
          <div className="flex-between">
            <div>
              <p className="eyebrow">Lista</p>
              <h3>Seus grupos</h3>
            </div>
            <span className="badge">{groups.length}</span>
          </div>

          {loading ? <p className="muted">Carregando...</p> : null}

          <div className="stack">
            {groups.map((group) => (
              <article key={group.id} className="group-card stack">
                <div className="flex-between">
                  <div>
                    <h4 style={{ margin: 0 }}>{group.name}</h4>
                    <p className="muted" style={{ marginBottom: 0 }}>
                      {group.description || "Sem descricao."}
                    </p>
                  </div>
                  <span className="badge">#{group.id.slice(0, 6)}</span>
                </div>

                <div className="segment">
                  <button type="button" className="secondary-button" onClick={() => navigate(`/groups/${group.id}/ranking`)}>
                    Ver ranking
                  </button>
                  <button type="button" className="ghost-button" onClick={() => navigate(`/groups/${group.id}/members`)}>
                    Ver membros
                  </button>
                </div>
              </article>
            ))}

            {!loading && groups.length === 0 ? <p className="muted">Nenhum grupo encontrado.</p> : null}
          </div>
        </div>
      </div>
    </section>
  );
}