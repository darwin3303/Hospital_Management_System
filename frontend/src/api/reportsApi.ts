import { apiClient, type ApiEnvelope } from './client';

export const reportsApi = {
  overview: () => apiClient.get<ApiEnvelope<any>>('/reports/overview').then(r => r.data.data),
  patients: () => apiClient.get<ApiEnvelope<any[]>>('/reports/patients').then(r => r.data.data),
  appointments: (status?: string) =>
    apiClient.get<ApiEnvelope<any[]>>('/reports/appointments', { params: { status } }).then(r => r.data.data),
  revenue: () => apiClient.get<ApiEnvelope<any>>('/reports/revenue').then(r => r.data.data),
  pharmacy: () => apiClient.get<ApiEnvelope<any[]>>('/reports/pharmacy').then(r => r.data.data),
  laboratory: (status?: string) =>
    apiClient.get<ApiEnvelope<any[]>>('/reports/laboratory', { params: { status } }).then(r => r.data.data),
  staff: () => apiClient.get<ApiEnvelope<any[]>>('/reports/staff').then(r => r.data.data),
};
