import { useEffect, useState } from 'react';
import { Typography, Spin } from 'antd';
import { reportsApi } from '../../api/reportsApi';
import { MetricCard } from '../../components/common/MetricCard';

export function OverviewPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportsApi.overview().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin />;

  return (
    <div>
      <Typography.Title level={3}>Overview</Typography.Title>
      <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
        <MetricCard label="Total patients" value={data?.total_patients ?? 0} />
        <MetricCard label="Appointments today" value={data?.appointments_today ?? 0} />
        <MetricCard label="Revenue collected" value={`Rs ${data?.revenue?.total_collected ?? 0}`} />
        <MetricCard label="Outstanding" value={`Rs ${data?.revenue?.outstanding ?? 0}`} />
      </div>
    </div>
  );
}
