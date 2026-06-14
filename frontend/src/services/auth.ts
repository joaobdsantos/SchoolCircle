import { publicApi, refreshAccessTokenRequest } from "./api";
export {
  ACCESS_TOKEN_KEY,
  clearSession,
  DISPLAY_NAME_KEY,
  REFRESH_TOKEN_KEY,
} from "./session";

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
  id: string;
  name: string;
  email: string;
};

type LoginResponse = {
  access: string;
  refresh: string;
};

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const response = await publicApi.post<LoginResponse>("/auth/login/", payload);
  return response.data;
}

export async function register(payload: RegisterPayload): Promise<RegisterResponse> {
  const response = await publicApi.post<RegisterResponse>("/auth/register/", payload);
  return response.data;
}

export async function refreshAccessToken(): Promise<string> {
  return refreshAccessTokenRequest();
}
