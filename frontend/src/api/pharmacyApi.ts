import { apiClient, type ApiEnvelope } from './client';
import type { PrescriptionItem } from './emrApi';

export interface Medicine {
  id: string; name: string; unit_price: number; quantity_in_stock: number; expiry_date: string;
}

export const pharmacyApi = {
  addMedicine: (payload: Omit<Medicine, 'id'>) =>
    apiClient.post<ApiEnvelope<Medicine>>('/pharmacy/medicines', payload).then(r => r.data.data),
  listMedicines: () =>
    apiClient.get<ApiEnvelope<Medicine[]>>('/pharmacy/medicines').then(r => r.data.data),
  pendingPrescriptions: () =>
    apiClient.get<ApiEnvelope<PrescriptionItem[]>>('/pharmacy/prescriptions/pending').then(r => r.data.data),
  dispense: (prescription_item_id: string, quantity: number) =>
    apiClient.post('/pharmacy/dispense', { prescription_item_id, quantity }),
};