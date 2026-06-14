import { api } from "./api";

export type UpdateUserPayload = {
  name?: string;
  email?: string;
  new_password?: string;
  password: string;
};

export type UserProfileResponse = {
  id: string;
  name: string;
  email: string;
};

export async function updateUserProfile(
  payload: UpdateUserPayload,
): Promise<UserProfileResponse> {
  const response = await api.put<UserProfileResponse>("/auth/profile/", payload);
  return response.data;
}
