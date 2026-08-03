import { Tag } from 'antd';
import { getStatusColor } from '../../theme/statusColors';

export function StatusBadge({ status }: { status: string }) {
  const { bg, text } = getStatusColor(status);
  return (
    <Tag style={{ background: bg, color: text, border: 'none', borderRadius: 6 }}>
      {status.replace(/_/g, ' ')}
    </Tag>
  );
}
