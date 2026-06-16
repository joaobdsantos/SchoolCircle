import axios, {
  AxiosError,
  InternalAxiosRequestConfig,
} from "axios";

import {
  clearSession,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
} from "./session";


type RetryableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

type RefreshTokenResponse = {
  access: string;
};

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";


export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const publicApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const multipartHeaders = {
  "Content-Type": "multipart/form-data",
};

export async function refreshAccessTokenRequest(): Promise<string> {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    clearSession();
    throw new Error("Refresh token not found.");
  }

  try {
    const response = await publicApi.post<RefreshTokenResponse>(
      "/auth/token/refresh/",
      { refresh: refreshToken },
    );
    setAccessToken(response.data.access);
    return response.data.access;
  } catch (error) {
    clearSession();
    throw error;
  }
}

function isRefreshTokenRequest(url?: string): boolean {
  return Boolean(url?.includes("/auth/token/refresh/"));
}

function redirectToLogin(): void {
  if (window.location.pathname !== "/login") {
    window.location.assign("/login");
  }
}

api.interceptors.request.use((config) => {
  const accessToken = getAccessToken();

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined;

    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      isRefreshTokenRequest(originalRequest.url)
    ) {
      return Promise.reject(error);
    }

    if (!getRefreshToken()) {
      clearSession();
      redirectToLogin();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      const accessToken = await refreshAccessTokenRequest();
      originalRequest.headers.Authorization = `Bearer ${accessToken}`;
      return api(originalRequest);
    } catch (refreshError) {
      clearSession();
      redirectToLogin();
      return Promise.reject(refreshError);
    }
  },
);
