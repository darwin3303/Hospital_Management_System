import { apiClient, type ApiEnvelope } from './client';

export interface Admission {
  id: string; patient_id: string; status: string; ward: string | null; bed_number: string | null;
}

export const inpatientApi = {
  admit: (payload: { patient_id: string; appointment_id?: string; ward?: string; bed_number?: string }) =>
    apiClient.post<ApiEnvelope<Admission>>('/admissions', payload).then(r => r.data.data),
  get: (id: string) => apiClient.get<ApiEnvelope<Admission>>(`/admissions/${id}`).then(r => r.data.data),
  discharge: (id: string, discharge_medical_record_id: string) =>
    apiClient.put<ApiEnvelope<Admission>>(`/admissions/${id}/discharge`, { discharge_medical_record_id }).then(r => r.data.data),
};
