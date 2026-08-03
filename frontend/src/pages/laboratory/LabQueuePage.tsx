import { useEffect, useState } from 'react';
import { Typography, Table, Button, Modal, Input, message, Space } from 'antd';
import { laboratoryApi, type LabRequest } from '../../api/laboratoryApi';
import { StatusBadge } from '../../components/common/StatusBadge';

export function LabQueuePage() {
  const [items, setItems] = useState<LabRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [resultModal, setResultModal] = useState<LabRequest | null>(null);
  const [resultText, setResultText] = useState('');

  const load = () => {
    setLoading(true);
    laboratoryApi.queue().then(setItems).finally(() => setLoading(false));
  };
  useEffect(load, []);

  const onCollectSample = async (id: string) => {
    try {
      await laboratoryApi.collectSample(id);
      message.success('Sample collected');
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not update');
    }
  };

  const onEnterResult = async () => {
    if (!resultModal) return;
    try {
      await laboratoryApi.enterResult(resultModal.id, resultText);
      message.success('Result entered');
      setResultModal(null);
      setResultText('');
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not save result');
    }
  };

  const onGenerateReport = async (id: string) => {
    try {
      await laboratoryApi.generateReport(id);
      message.success('Report generated');
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not generate report');
    }
  };

  return (
    <div>
      <Typography.Title level={3}>Lab queue</Typography.Title>

      <Table
        rowKey="id"
        loading={loading}
        dataSource={items}
        columns={[
          { title: 'Test', dataIndex: 'test_name' },
          { title: 'Status', dataIndex: 'status', render: (s: string) => <StatusBadge status={s} /> },
          {
            title: 'Actions',
            render: (_, record: LabRequest) => (
              <Space>
                {record.status === 'REQUESTED' && (
                  <Button size="small" onClick={() => onCollectSample(record.id)}>
                    Collect sample
                  </Button>
                )}
                {record.status === 'SAMPLE_COLLECTED' && (
                  <Button size="small" onClick={() => setResultModal(record)}>
                    Enter result
                  </Button>
                )}
                {record.status === 'RESULT_ENTERED' && (
                  <Button size="small" type="primary" ghost onClick={() => onGenerateReport(record.id)}>
                    Generate report
                  </Button>
                )}
              </Space>
            ),
          },
        ]}
      />

      <Modal
        title="Enter result"
        open={!!resultModal}
        onOk={onEnterResult}
        onCancel={() => setResultModal(null)}
        okText="Save"
      >
        <Input.TextArea rows={4} value={resultText} onChange={(e) => setResultText(e.target.value)} />
      </Modal>
    </div>
  );
}
