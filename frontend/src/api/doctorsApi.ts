import { apiClient, type ApiEnvelope } from './client';

export interface Doctor {
  id: string; employee_id: string; specialty: string; consultation_fee: number;
}
export interface AvailabilitySlot {
  id?: string; day_of_week: number; start_time: string; end_time: string;
}

export const doctorsApi = {
  create: (payload: { employee_id: string; specialty: string; consultation_fee: number; availability: AvailabilitySlot[] }) =>
    apiClient.post<ApiEnvelope<Doctor>>('/doctors', payload).then(r => r.data.data),
  list: () => apiClient.get<ApiEnvelope<Doctor[]>>('/doctors').then(r => r.data.data),
  get: (id: string) => apiClient.get<ApiEnvelope<Doctor>>(`/doctors/${id}`).then(r => r.data.data),
  listAvailability: (id: string) =>
    apiClient.get<ApiEnvelope<AvailabilitySlot[]>>(`/doctors/${id}/availability`).then(r => r.data.data),
  addAvailability: (id: string, slot: AvailabilitySlot) =>
    apiClient.post(`/doctors/${id}/availability`, slot),
};
