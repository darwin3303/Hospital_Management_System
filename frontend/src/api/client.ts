import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

let accessToken: string | null = null;
let refreshPromise: Promise<string | null> | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getAccessToken() {
  return accessToken;
}

export const apiClient = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // sends the httpOnly refresh cookie automatically
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

async function refreshAccessToken(): Promise<string | null> {
  try {
    const response = await axios.get(`${API_BASE}/auth/refresh`, {
      withCredentials: true,
    });
    const newToken = response.data?.data?.access_token ?? null;
    setAccessToken(newToken);
    return newToken;
  } catch {
    setAccessToken(null);
    return null;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retried?: boolean };

    if (error.response?.status === 401 && original && !original._retried) {
      original._retried = true;

      // Coalesce concurrent 401s into a single refresh call.
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }
      const newToken = await refreshPromise;

      if (newToken) {
        original.headers = original.headers ?? {};
        original.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(original);
      }

      // Refresh failed -- session is truly over, send the user back to login.
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

/** Standard envelope every endpoint returns, per the API conventions. */
export interface ApiEnvelope<T> {
  success: boolean;
  data: T;
  meta?: { page: number; page_size: number; total: number };
}

export interface ApiErrorEnvelope {
  success: false;
  code: string;
  message: string;
  details: Record<string, unknown>;
}
