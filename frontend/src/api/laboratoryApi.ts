import { apiClient, type ApiEnvelope } from './client';

export interface LabRequest {
  id: string; medical_record_id: string; test_name: string;
  status: string; result_data: string | null;
}

export const laboratoryApi = {
  create: (payload: { medical_record_id: string; test_name: string }) =>
    apiClient.post<ApiEnvelope<LabRequest>>('/lab-requests', payload).then(r => r.data.data),
  queue: (status?: string) =>
    apiClient.get<ApiEnvelope<LabRequest[]>>('/lab-requests', { params: { status } }).then(r => r.data.data),
  listForRecord: (recordId: string) =>
    apiClient.get<ApiEnvelope<LabRequest[]>>(`/lab-requests/medical-record/${recordId}`).then(r => r.data.data),
  collectSample: (id: string) =>
    apiClient.put<ApiEnvelope<LabRequest>>(`/lab-requests/${id}/collect-sample`).then(r => r.data.data),
  enterResult: (id: string, result_data: string) =>
    apiClient.put<ApiEnvelope<LabRequest>>(`/lab-requests/${id}/enter-result`, { result_data }).then(r => r.data.data),
  generateReport: (id: string) =>
    apiClient.put<ApiEnvelope<LabRequest>>(`/lab-requests/${id}/generate-report`).then(r => r.data.data),
};
