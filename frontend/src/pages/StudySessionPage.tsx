import { useMemo, useState } from "react";

import { createStudySession } from "../services/study";

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const VALID_TYPES = ["image/jpeg", "image/png", "image/webp"];

function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result ?? ""));
    reader.onerror = () => reject(new Error("Falha ao ler arquivo."));
    reader.readAsDataURL(file);
  });
}

export function StudySessionPage() {
  const today = useMemo(() => new Date().toISOString().split("T")[0], []);
  const [studyDate, setStudyDate] = useState(today);
  const [description, setDescription] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [photoPreview, setPhotoPreview] = useState("");
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handlePhotoChange(event: React.ChangeEvent<HTMLInputElement>) {
    setError("");
    setMessage("");

    const file = event.target.files?.[0];
    if (!file) {
      setPhotoPreview("");
      setPhotoFile(null);
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError("Arquivo muito grande. Use no maximo 10MB.");
      event.target.value = "";
      return;
    }

    if (!VALID_TYPES.includes(file.type)) {
      setError("Formato invalido. Use JPG, PNG ou WEBP.");
      event.target.value = "";
      return;
    }

    const dataUrl = await fileToDataUrl(file);
    setPhotoPreview(dataUrl);
    setPhotoFile(file);
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");

    if (!studyDate || !description.trim() || !photoFile) {
      setError("Preencha a data, a descricao e a foto.");
      return;
    }

    if (description.trim().length < 10) {
      setError("A descricao precisa ter pelo menos 10 caracteres.");
      return;
    }

    if (studyDate > today) {
      setError("A data nao pode ser futura.");
      return;
    }

    try {
      setIsSubmitting(true);
      const session = await createStudySession({
        study_date: studyDate,
        content_description: [
          description.trim(),
          startTime || endTime ? `Horario: ${startTime || "--:--"} - ${endTime || "--:--"}` : "",
        ]
          .filter(Boolean)
          .join("\n"),
        photo_url: photoFile,
        start_time: startTime || undefined,
        end_time: endTime || undefined,
      });

      setMessage(`Sessao registrada com sucesso. +${session.points_granted} pontos.`);
      setStudyDate(today);
      setDescription("");
      setStartTime("");
      setEndTime("");
      setPhotoPreview("");
      setPhotoFile(null);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Erro ao registrar estudo.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="page-card stack">
      <div className="toolbar">
        <div>
          <p className="eyebrow">Estudo</p>
          <h2>Registrar sessão de estudo</h2>
        </div>
        <span className="badge info">+5 pontos</span>
      </div>

      {error ? <div className="notice error">{error}</div> : null}
      {message ? <div className="notice success">{message}</div> : null}

      <div className="flow-grid">
        <form onSubmit={handleSubmit} className="stack">
          <div className="grid-2">
            <div>
              <label htmlFor="study-date">Data de estudo</label>
              <input
                id="study-date"
                type="date"
                value={studyDate}
                max={today}
                onChange={(event) => setStudyDate(event.target.value)}
                required
              />
            </div>

            <div>
              <label htmlFor="study-photo">Foto</label>
              <input
                id="study-photo"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handlePhotoChange}
                required
              />
            </div>
          </div>

          <div className="grid-2">
            <div>
              <label htmlFor="start-time">Hora de inicio opcional</label>
              <input
                id="start-time"
                type="time"
                value={startTime}
                onChange={(event) => setStartTime(event.target.value)}
              />
            </div>

            <div>
              <label htmlFor="end-time">Hora de termino opcional</label>
              <input
                id="end-time"
                type="time"
                value={endTime}
                onChange={(event) => setEndTime(event.target.value)}
              />
            </div>
          </div>

          <div>
            <label htmlFor="content-description">Descricao do conteudo</label>
            <textarea
              id="content-description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Descreva o que foi estudado, temas e observacoes..."
              required
            />
          </div>

          <div className="form-actions">
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Registrando..." : "Registrar estudo"}
            </button>
          </div>
        </form>

        <div className="panel-card stack">
          <p className="eyebrow">Resumo</p>
          {photoPreview ? (
            <img className="preview-image" src={photoPreview} alt="Preview da foto" />
          ) : (
            <p className="muted">Escolha uma imagem para ver o preview da sessao.</p>
          )}

          <div className="notice">
            <strong>Regras</strong>
            <p className="muted" style={{ marginBottom: 0 }}>
              A descricao precisa ter pelo menos 10 caracteres. A foto deve ser JPG, PNG ou WEBP
              e ter ate 10MB.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}