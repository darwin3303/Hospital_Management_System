import { blue, neutral, semantic } from './tokens';

/**
 * Every status badge in the app (appointment, lab, invoice, admission)
 * resolves its colour through this map, so status meaning stays visually
 * consistent everywhere it appears.
 */
export const statusColors: Record<string, { bg: string; text: string }> = {
  // Appointments
  SCHEDULED: { bg: blue[50], text: blue[600] },
  COMPLETED: { bg: semantic.successBg, text: semantic.success },
  CANCELLED: { bg: neutral[100], text: neutral[600] },
  NO_SHOW: { bg: semantic.dangerBg, text: semantic.danger },

  // Lab requests
  REQUESTED: { bg: blue[50], text: blue[600] },
  SAMPLE_COLLECTED: { bg: semantic.warningBg, text: semantic.warning },
  RESULT_ENTERED: { bg: blue[100], text: blue[600] },
  REPORT_GENERATED: { bg: semantic.successBg, text: semantic.success },

  // Prescription / dispense
  PENDING: { bg: semantic.warningBg, text: semantic.warning },
  DISPENSED: { bg: semantic.successBg, text: semantic.success },

  // Invoices
  UNPAID: { bg: semantic.dangerBg, text: semantic.danger },
  PARTIALLY_PAID: { bg: semantic.warningBg, text: semantic.warning },
  PAID: { bg: semantic.successBg, text: semantic.success },

  // Admissions / leave
  ACTIVE: { bg: blue[50], text: blue[600] },
  DISCHARGED: { bg: neutral[100], text: neutral[600] },
  APPROVED: { bg: semantic.successBg, text: semantic.success },
  REJECTED: { bg: semantic.dangerBg, text: semantic.danger },
};

export function getStatusColor(status: string) {
  return statusColors[status] ?? { bg: neutral[100], text: neutral[600] };
}
