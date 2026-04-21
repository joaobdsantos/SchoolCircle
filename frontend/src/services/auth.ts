import { api } from "./api";

type LoginPayload = {
  email: string;
  password: string;
};

type RegisterPayload = {
  name: string;
  email: string;
  password: string;
};

type RegisterResponse = {
  id: number;
  name: string;
  email: string;
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

export async function register(payload: RegisterPayload): Promise<RegisterResponse> {
  const response = await api.post<RegisterResponse>("/auth/register/", payload);
  return response.data;
}
