import { neutral } from '../../theme/tokens';

export function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div
      style={{
        background: neutral[0],
        border: `1px solid ${neutral[200]}`,
        borderRadius: 12,
        padding: '16px 20px',
        flex: 1,
      }}
    >
      <div style={{ fontSize: 13, color: neutral[600], marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 600, color: neutral[900] }}>{value}</div>
    </div>
  );
}
