import { api } from "./api";
import { ACCESS_TOKEN_KEY } from "./auth";

export type UpdateUserPayload = {
  name?: string;
  email?: string;
  new_password?: string;
  password: string;
};

export type UserProfileResponse = {
  id: number;
  name: string;
  email: string;
};

function getAuthHeaders() {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function updateUserProfile(
  payload: UpdateUserPayload,
): Promise<UserProfileResponse> {
  const response = await api.put<UserProfileResponse>("/auth/profile/", payload, {
    headers: getAuthHeaders(),
  });
  return response.data;
}
