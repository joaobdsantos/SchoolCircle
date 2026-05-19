import { api } from "./api";
import { ACCESS_TOKEN_KEY } from "./auth";

export type AcademicProfilePayload = {
  education_level: string;
  is_independent: boolean;
  institution_name: string;
  course_name: string;
};

export type AcademicProfileResponse = AcademicProfilePayload | null;

function getAuthHeaders() {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function getAcademicProfile(): Promise<AcademicProfileResponse> {
  const response = await api.get<AcademicProfileResponse>("/academic-profile/", {
    headers: getAuthHeaders(),
  });
  return response.data;
}

export async function saveAcademicProfile(
  payload: AcademicProfilePayload,
): Promise<AcademicProfilePayload> {
  const response = await api.put<AcademicProfilePayload>("/academic-profile/", payload, {
    headers: getAuthHeaders(),
  });
  return response.data;
}
