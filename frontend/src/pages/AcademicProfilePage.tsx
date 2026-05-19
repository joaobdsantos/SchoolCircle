import { FormEvent, useEffect, useState } from "react";

import {
  getAcademicProfile,
  saveAcademicProfile,
} from "../services/academicProfile";

export function AcademicProfilePage() {
  const [educationLevel, setEducationLevel] = useState("");
  const [isIndependent, setIsIndependent] = useState(false);
  const [institutionName, setInstitutionName] = useState("");
  const [courseName, setCourseName] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    async function loadProfile() {
      try {
        setIsLoading(true);
        setError("");
        const profile = await getAcademicProfile();

        if (profile) {
          setEducationLevel(profile.education_level ?? "");
          setIsIndependent(profile.is_independent ?? false);
          setInstitutionName(profile.institution_name ?? "");
          setCourseName(profile.course_name ?? "");
        }
      } catch {
        setError("Nao foi possivel carregar o perfil academico.");
      } finally {
        setIsLoading(false);
      }
    }

    loadProfile();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!educationLevel.trim()) {
      setError("Preencha o grau de escolaridade.");
      return;
    }

    if (!isIndependent && (!institutionName.trim() || !courseName.trim())) {
      setError("Instituicao e curso sao obrigatorios para nao independente.");
      return;
    }

    try {
      setIsSubmitting(true);
      const payload = {
        education_level: educationLevel.trim(),
        is_independent: isIndependent,
        institution_name: isIndependent ? "" : institutionName.trim(),
        course_name: isIndependent ? "" : courseName.trim(),
      };

      const saved = await saveAcademicProfile(payload);
      setEducationLevel(saved.education_level);
      setIsIndependent(saved.is_independent);
      setInstitutionName(saved.institution_name);
      setCourseName(saved.course_name);
      setSuccess("Perfil academico salvo com sucesso.");
    } catch {
      setError("Nao foi possivel salvar o perfil academico.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="page-card">
      <h2>Perfil academico</h2>

      {isLoading ? (
        <p>Carregando...</p>
      ) : (
        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="education-level">Grau de escolaridade</label>
            <br />
            <input
              id="education-level"
              type="text"
              value={educationLevel}
              onChange={(event) => setEducationLevel(event.target.value)}
            />
          </div>

          <div style={{ marginTop: "0.75rem" }}>
            <label htmlFor="is-independent">Estudante independente</label>
            <input
              id="is-independent"
              type="checkbox"
              checked={isIndependent}
              onChange={(event) => {
                const checked = event.target.checked;
                setIsIndependent(checked);
                if (checked) {
                  setInstitutionName("");
                  setCourseName("");
                }
              }}
              style={{ marginLeft: "0.5rem" }}
            />
          </div>

          <div style={{ marginTop: "0.75rem" }}>
            <label htmlFor="institution-name">Instituicao</label>
            <br />
            <input
              id="institution-name"
              type="text"
              value={institutionName}
              onChange={(event) => setInstitutionName(event.target.value)}
              disabled={isIndependent}
            />
          </div>

          <div style={{ marginTop: "0.75rem" }}>
            <label htmlFor="course-name">Curso</label>
            <br />
            <input
              id="course-name"
              type="text"
              value={courseName}
              onChange={(event) => setCourseName(event.target.value)}
              disabled={isIndependent}
            />
          </div>

          {error ? <p style={{ color: "#b42318", marginTop: "0.75rem" }}>{error}</p> : null}
          {success ? <p style={{ color: "#0b6e4f", marginTop: "0.75rem" }}>{success}</p> : null}

          <button type="submit" style={{ marginTop: "1rem" }} disabled={isSubmitting}>
            {isSubmitting ? "Salvando..." : "Salvar"}
          </button>
        </form>
      )}
    </section>
  );
}
