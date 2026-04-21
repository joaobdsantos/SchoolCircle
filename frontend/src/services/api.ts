import axios from "axios";


export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api",
  timeout: 10000,
});

// TODO: Add auth interceptors when real login and token refresh flows are implemented.
