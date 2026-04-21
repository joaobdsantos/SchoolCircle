import { api } from "./api";

type LoginPayload = {
  email: string;
  password: string;
};

type LoginResponse = {
  access: string;
  refresh: string;
};

export const ACCESS_TOKEN_KEY = "access_token";
export const REFRESH_TOKEN_KEY = "refresh_token";

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>("/auth/login/", payload);
  return response.data;
}
