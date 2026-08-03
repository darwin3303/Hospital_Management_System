import { apiClient, type ApiEnvelope } from './client';

export interface User {
  id: string;
  username: string;
  role: string;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  user: User;
}

export const authApi = {
  login: (username: string, password: string) =>
    apiClient
      .post<ApiEnvelope<LoginResponse>>('/auth/login', { username, password })
      .then((r) => r.data.data),

  refresh: () =>
    apiClient
      .get<ApiEnvelope<{ access_token: string }>>('/auth/refresh')
      .then((r) => r.data.data),

  logout: () => apiClient.post('/auth/logout'),

  changePassword: (old_password: string, new_password: string) =>
    apiClient.post('/auth/change-password', { old_password, new_password }),

  createUser: (payload: { username: string; password: string; role: string }) =>
    apiClient.post<ApiEnvelope<User>>('/users', payload).then((r) => r.data.data),

  listUsers: (page = 1, page_size = 20) =>
    apiClient
      .get<ApiEnvelope<User[]>>('/users', { params: { page, page_size } })
      .then((r) => r.data),

  setUserStatus: (userId: string, is_active: boolean) =>
    apiClient
      .put<ApiEnvelope<User>>(`/users/${userId}/status`, { is_active })
      .then((r) => r.data.data),
};
