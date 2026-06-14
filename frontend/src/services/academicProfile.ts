import { api } from "./api";

export type AcademicProfilePayload = {
  education_level: string;
  is_independent: boolean;
  institution_name: string;
  course_name: string;
};

export type AcademicProfileResponse = AcademicProfilePayload | null;

export async function getAcademicProfile(): Promise<AcademicProfileResponse> {
  const response = await api.get<AcademicProfileResponse>("/academic-profile/");
  return response.data;
}

export async function saveAcademicProfile(
  payload: AcademicProfilePayload,
): Promise<AcademicProfilePayload> {
  const response = await api.put<AcademicProfilePayload>("/academic-profile/", payload);
  return response.data;
}
