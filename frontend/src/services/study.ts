import { api } from "./api";

export type StudySessionPayload = {
  study_date: string;
  content_description: string;
  photo_url: File;
  start_time?: string;
  end_time?: string;
};

export type StudySessionRecord = StudySessionPayload & {
  id: string;
  user: string;
  registered_at: string;
  is_valid: boolean;
  points_granted: number;
};

export async function createStudySession(payload: StudySessionPayload): Promise<StudySessionRecord> {
  const formData = new FormData();
  formData.append("study_date", payload.study_date);
  formData.append("content_description", payload.content_description);
  formData.append("photo_url", payload.photo_url);

  if (payload.start_time) {
    formData.append("start_time", payload.start_time);
  }

  if (payload.end_time) {
    formData.append("end_time", payload.end_time);
  }

  const response = await api.post<StudySessionRecord>("/study-sessions/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}
