import { apiClient, type ApiEnvelope } from './client';

export interface LineItem {
  id: string; source_type: string; source_id: string; description: string; amount: number;
}
export interface Invoice {
  id: string; appointment_id: string; total_amount: number; status: string; line_items: LineItem[];
}

export const billingApi = {
  generate: (appointment_id: string) =>
    apiClient.post<ApiEnvelope<Invoice>>('/invoices', { appointment_id }).then(r => r.data.data),
  getByAppointment: (appointmentId: string) =>
    apiClient.get<ApiEnvelope<Invoice>>(`/invoices/appointment/${appointmentId}`).then(r => r.data.data),
  recordPayment: (invoiceId: string, amount: number, method: string) =>
    apiClient.post(`/invoices/${invoiceId}/payments`, { amount, method }),
};
