/**
 * Raw colour palette. Every colour used anywhere in the app should trace
 * back to a value defined here -- change a value in this one file and it
 * propagates everywhere, rather than hunting through components.
 */

export const blue = {
  50: '#F0F9FF',   // lightest tint -- subtle backgrounds, hover states
  100: '#E0F2FE',  // light fills -- selected row backgrounds
  200: '#BAE6FD',  // soft accents -- badges, secondary highlights
  400: '#7DD3FC',  // mid tone -- borders on accent elements, chart bars
  600: '#0284C7',  // primary brand blue -- buttons, active nav, links
} as const;

export const neutral = {
  0: '#FFFFFF',
  50: '#F8FAFC',
  100: '#F1F5F9',
  200: '#E2E8F0',
  400: '#94A3B8',
  600: '#475569',
  800: '#1E293B',
  900: '#0F172A',
} as const;

export const semantic = {
  success: '#16A34A',
  successBg: '#F0FDF4',
  warning: '#D97706',
  warningBg: '#FFFBEB',
  danger: '#DC2626',
  dangerBg: '#FEF2F2',
} as const;

export const radii = {
  sm: 6,
  md: 8,
  lg: 12,
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
} as const;
