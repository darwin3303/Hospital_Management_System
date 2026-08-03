export const Role = {
  ADMIN: 'ADMIN',
  RECEPTIONIST: 'RECEPTIONIST',
  DOCTOR: 'DOCTOR',
  NURSE: 'NURSE',
  LAB_STAFF: 'LAB_STAFF',
  PHARMACIST: 'PHARMACIST',
  ACCOUNTANT: 'ACCOUNTANT',
} as const;

export type RoleType = (typeof Role)[keyof typeof Role];

export const roleHomeRoute: Record<string, string> = {
  ADMIN: '/admin/overview',
  RECEPTIONIST: '/receptionist/patients',
  DOCTOR: '/doctor/queue',
  NURSE: '/nurse/patients',
  LAB_STAFF: '/laboratory/queue',
  PHARMACIST: '/pharmacy/queue',
  ACCOUNTANT: '/billing/invoices',
};
