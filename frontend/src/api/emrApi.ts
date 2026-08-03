import { apiClient, type ApiEnvelope } from './client';

export interface MedicalRecord {
  id: string; appointment_id: string; doctor_id: string; patient_id: string;
  diagnosis: string; notes: string | null;
}
export interface PrescriptionItem {
  id: string; medicine_id: string; quantity: number; status: string;
}
export interface Prescription {
  id: string; medical_record_id: string; items: PrescriptionItem[];
}

export const emrApi = {
  createRecord: (payload: { appointment_id: string; diagnosis: string; notes?: string }) =>
    apiClient.post<ApiEnvelope<MedicalRecord>>('/medical-records', payload).then(r => r.data.data),
  getByAppointment: (appointmentId: string) =>
    apiClient.get<ApiEnvelope<MedicalRecord>>(`/medical-records/appointment/${appointmentId}`).then(r => r.data.data),
  getHistory: (patientId: string) =>
    apiClient.get<ApiEnvelope<MedicalRecord[]>>(`/medical-records/patient/${patientId}/history`).then(r => r.data.data),
  addAmendment: (recordId: string, amended_text: string) =>
    apiClient.post(`/medical-records/${recordId}/amendments`, { amended_text }),
  createPrescription: (recordId: string, items: { medicine_id: string; quantity: number; dosage_instructions?: string }[]) =>
    apiClient.post<ApiEnvelope<Prescription>>(`/medical-records/${recordId}/prescriptions`, { items }).then(r => r.data.data),
};
