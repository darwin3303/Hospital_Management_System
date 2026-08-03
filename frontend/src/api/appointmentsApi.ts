import { apiClient, type ApiEnvelope } from './client';

export interface Appointment {
  id: string; patient_id: string; doctor_id: string;
  scheduled_at: string; duration_minutes: number; status: string;
}

export const appointmentsApi = {
  book: (payload: { patient_id: string; doctor_id: string; scheduled_at: string; duration_minutes: number }) =>
    apiClient.post<ApiEnvelope<Appointment>>('/appointments', payload).then(r => r.data.data),
  list: (params: { doctor_id?: string; patient_id?: string; status?: string; page?: number; page_size?: number }) =>
    apiClient.get<ApiEnvelope<Appointment[]>>('/appointments', { params }).then(r => r.data),
  doctorQueue: (status = 'SCHEDULED') =>
    apiClient.get<ApiEnvelope<Appointment[]>>('/appointments', { params: { doctor_id: 'me', status } }).then(r => r.data.data),
  cancel: (id: string) => apiClient.put<ApiEnvelope<Appointment>>(`/appointments/${id}/cancel`).then(r => r.data.data),
  reschedule: (id: string, payload: { scheduled_at: string; duration_minutes?: number }) =>
    apiClient.put<ApiEnvelope<Appointment>>(`/appointments/${id}/reschedule`, payload).then(r => r.data.data),
  complete: (id: string) => apiClient.put<ApiEnvelope<Appointment>>(`/appointments/${id}/complete`).then(r => r.data.data),
  noShow: (id: string) => apiClient.put<ApiEnvelope<Appointment>>(`/appointments/${id}/no-show`).then(r => r.data.data),
};
