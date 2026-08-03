import { useState } from 'react';
import { Typography, Input, Button, Card, Table, Modal, InputNumber, Select, message, Space, Empty } from 'antd';
import { billingApi, type Invoice } from '../../api/billingApi';
import { StatusBadge } from '../../components/common/StatusBadge';

export function InvoicesPage() {
  const [appointmentId, setAppointmentId] = useState('');
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [paymentModalOpen, setPaymentModalOpen] = useState(false);
  const [amount, setAmount] = useState<number | null>(null);
  const [method, setMethod] = useState('CASH');

  const onLoadOrGenerate = async () => {
    try {
      const existing = await billingApi.getByAppointment(appointmentId);
      setInvoice(existing);
    } catch {
      try {
        const generated = await billingApi.generate(appointmentId);
        setInvoice(generated);
        message.success('Invoice generated');
      } catch (err: any) {
        message.error(err?.response?.data?.message ?? 'Could not load or generate invoice');
      }
    }
  };

  const onRecordPayment = async () => {
    if (!invoice || amount == null) return;
    try {
      await billingApi.recordPayment(invoice.id, amount, method);
      message.success('Payment recorded');
      setPaymentModalOpen(false);
      const refreshed = await billingApi.getByAppointment(appointmentId);
      setInvoice(refreshed);
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Payment could not be recorded');
    }
  };

  return (
    <div>
      <Typography.Title level={3}>Invoices</Typography.Title>

      <Space style={{ marginBottom: 24 }}>
        <Input
          placeholder="Appointment ID"
          value={appointmentId}
          onChange={(e) => setAppointmentId(e.target.value)}
          style={{ width: 320 }}
        />
        <Button type="primary" onClick={onLoadOrGenerate}>
          Load / generate invoice
        </Button>
      </Space>

      {!invoice && <Empty description="Enter an appointment ID to view or generate its invoice" />}

      {invoice && (
        <Card
          title={`Invoice`}
          extra={<StatusBadge status={invoice.status} />}
        >
          <Table
            rowKey="id"
            dataSource={invoice.line_items}
            pagination={false}
            columns={[
              { title: 'Type', dataIndex: 'source_type' },
              { title: 'Description', dataIndex: 'description' },
              { title: 'Amount', dataIndex: 'amount', render: (v: number) => `Rs ${v}` },
            ]}
          />
          <div style={{ marginTop: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography.Title level={4} style={{ margin: 0 }}>
              Total: Rs {invoice.total_amount}
            </Typography.Title>
            <Button type="primary" onClick={() => setPaymentModalOpen(true)}>
              Record payment
            </Button>
          </div>
        </Card>
      )}

      <Modal
        title="Record payment"
        open={paymentModalOpen}
        onOk={onRecordPayment}
        onCancel={() => setPaymentModalOpen(false)}
        okText="Record"
      >
        <div style={{ marginBottom: 12 }}>
          <Typography.Text>Amount</Typography.Text>
          <InputNumber style={{ width: '100%' }} min={0} value={amount} onChange={setAmount} />
        </div>
        <div>
          <Typography.Text>Method</Typography.Text>
          <Select
            style={{ width: '100%' }}
            value={method}
            onChange={setMethod}
            options={[
              { value: 'CASH', label: 'Cash' },
              { value: 'CARD', label: 'Card' },
              { value: 'INSURANCE', label: 'Insurance' },
            ]}
          />
        </div>
      </Modal>
    </div>
  );
}
