import { apiClient, type ApiEnvelope } from './client';

export interface Department { id: string; name: string; }
export interface Employee {
  id: string; user_id: string | null; department_id: string;
  first_name: string; last_name: string; phone: string | null; hired_at: string;
}

export const staffApi = {
  createDepartment: (name: string) =>
    apiClient.post<ApiEnvelope<Department>>('/staff/departments', { name }).then(r => r.data.data),
  listDepartments: () =>
    apiClient.get<ApiEnvelope<Department[]>>('/staff/departments').then(r => r.data.data),
  createEmployee: (payload: Partial<Employee>) =>
    apiClient.post<ApiEnvelope<Employee>>('/staff/employees', payload).then(r => r.data.data),
  listEmployees: (page = 1, page_size = 20) =>
    apiClient.get<ApiEnvelope<Employee[]>>('/staff/employees', { params: { page, page_size } }).then(r => r.data),
  markAttendance: (employee_id: string, status = 'PRESENT') =>
    apiClient.post('/staff/attendance', { employee_id, status }),
  requestLeave: (payload: { employee_id: string; start_date: string; end_date: string; reason?: string }) =>
    apiClient.post('/staff/leave', payload),
  decideLeave: (leaveId: string, approve: boolean) =>
    apiClient.put(`/staff/leave/${leaveId}/decision`, { approve }),
  listLeaveForEmployee: (employeeId: string) =>
    apiClient.get<ApiEnvelope<any[]>>(`/staff/leave/${employeeId}`).then(r => r.data.data),
};
