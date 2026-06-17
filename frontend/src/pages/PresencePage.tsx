import { useEffect, useMemo, useState } from "react";
import { isAxiosError } from "axios";

import { createAttendanceRecord, type AttendanceRecord } from "../services/attendance";
import { listGroups, type StudyGroup } from "../services/groups";

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

function collectApiMessages(data: unknown): string[] {
  if (!data) {
    return [];
  }

  if (typeof data === "string") {
    return [data];
  }

  if (Array.isArray(data)) {
    return data.flatMap(collectApiMessages);
  }

  if (typeof data === "object") {
    const errorData = data as Record<string, unknown>;
    const prioritizedMessages = [
      ...collectApiMessages(errorData.detail),
      ...collectApiMessages(errorData.non_field_errors),
    ];

    const fieldMessages = Object.entries(errorData)
      .filter(([field]) => field !== "detail" && field !== "non_field_errors")
      .flatMap(([, value]) => collectApiMessages(value));

    return [...prioritizedMessages, ...fieldMessages];
  }

  return [];
}

function getPresenceErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const messages = collectApiMessages(error.response?.data);
    if (messages.length > 0) {
      return messages.join(" ");
    }
  }

  return "Erro ao registrar presença. Tente novamente.";
}

export function PresencePage() {
  const today = useMemo(() => new Date().toISOString().split("T")[0], []);
  const [classDate, setClassDate] = useState(today);
  const [period, setPeriod] = useState<AttendanceRecord["period"]>("MORNING");
  const [sharedGroup, setSharedGroup] = useState("");
  const [photoPreview, setPhotoPreview] = useState("");
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [groups, setGroups] = useState<StudyGroup[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    async function loadGroups() {
      try {
        const data = await listGroups();
        setGroups(data);
      } catch {
        setGroups([]);
      }
    }

    loadGroups();
  }, []);

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

    if (!classDate || !period || !photoFile) {
      setError("Preencha a data, o periodo e a foto.");
      return;
    }

    if (classDate > today) {
      setError("A data nao pode ser futura.");
      return;
    }

    try {
      setIsSubmitting(true);
      const saved = await createAttendanceRecord({
        class_date: classDate,
        period,
        photo_url: photoFile,
        shared_group: sharedGroup || undefined,
      });

      setMessage(`Presenca registrada com sucesso. +${saved.points_granted} pontos.`);
      setClassDate(today);
      setPeriod("MORNING");
      setSharedGroup("");
      setPhotoPreview("");
      setPhotoFile(null);
    } catch (submitError) {
      setError(getPresenceErrorMessage(submitError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="page-card stack">
      <div className="toolbar">
        <div>
          <p className="eyebrow">Presença</p>
          <h2>Registrar presença com foto</h2>
        </div>
        <span className="badge">+10 pontos</span>
      </div>

      {error ? <div className="notice error">{error}</div> : null}
      {message ? <div className="notice success">{message}</div> : null}

      <div className="flow-grid">
        <form onSubmit={handleSubmit} className="stack">
          <div className="grid-2">
            <div>
              <label htmlFor="presence-date">Data da aula</label>
              <input
                id="presence-date"
                type="date"
                value={classDate}
                max={today}
                onChange={(event) => setClassDate(event.target.value)}
                required
              />
            </div>

            <div>
              <label htmlFor="presence-period">Periodo</label>
              <select
                id="presence-period"
                value={period}
                onChange={(event) => setPeriod(event.target.value as AttendanceRecord["period"])}
                required
              >
                <option value="MORNING">Manha</option>
                <option value="AFTERNOON">Tarde</option>
                <option value="NIGHT">Noite</option>
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="presence-group">Grupo compartilhado opcional</label>
            <select
              id="presence-group"
              value={sharedGroup}
              onChange={(event) => setSharedGroup(event.target.value)}
            >
              <option value="">Sem grupo</option>
              {groups.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="presence-photo">Foto</label>
            <input
              id="presence-photo"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handlePhotoChange}
              required
            />
          </div>

          <div className="form-actions">
            <button type="submit" disabled={isSubmitting || loading}>
              {isSubmitting ? "Registrando..." : "Registrar presença"}
            </button>
          </div>
        </form>

        <div className="panel-card stack">
          <p className="eyebrow">Preview</p>
          {photoPreview ? (
            <img className="preview-image" src={photoPreview} alt="Preview da foto" />
          ) : (
            <p className="muted">Escolha uma imagem JPG, PNG ou WEBP para ver o preview.</p>
          )}
          <div className="notice">
            <strong>Validações</strong>
            <p className="muted" style={{ marginBottom: 0 }}>
              A data nao pode ser futura, a foto e o periodo sao obrigatorios e o arquivo deve ter
              ate 10MB.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
