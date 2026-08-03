import { apiClient, type ApiEnvelope } from './client';

export interface Patient {
  id: string; first_name: string; last_name: string; phone: string;
  date_of_birth: string | null; gender: string | null; address: string | null;
}

export const patientsApi = {
  register: (payload: Omit<Patient, 'id'>) =>
    apiClient.post<ApiEnvelope<Patient>>('/patients', payload).then(r => r.data.data),
  search: (query: string, page = 1, page_size = 20) =>
    apiClient.get<ApiEnvelope<Patient[]>>('/patients/search', { params: { query, page, page_size } }).then(r => r.data),
  get: (id: string) => apiClient.get<ApiEnvelope<Patient>>(`/patients/${id}`).then(r => r.data.data),
  update: (id: string, payload: Partial<Patient>) =>
    apiClient.put<ApiEnvelope<Patient>>(`/patients/${id}`, payload).then(r => r.data.data),
};
