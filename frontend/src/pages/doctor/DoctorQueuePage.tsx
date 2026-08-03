import { useEffect, useState } from 'react';
import { Typography, Table, Button, Drawer, Form, Input, InputNumber, message, Space, Divider, Select } from 'antd';
import { appointmentsApi, type Appointment } from '../../api/appointmentsApi';
import { emrApi } from '../../api/emrApi';
import { laboratoryApi } from '../../api/laboratoryApi';
import { pharmacyApi, type Medicine } from '../../api/pharmacyApi';
import { StatusBadge } from '../../components/common/StatusBadge';
import { blue } from '../../theme/tokens';

export function DoctorQueuePage() {
  const [items, setItems] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<Appointment | null>(null);
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [prescriptionItems, setPrescriptionItems] = useState<Array<{ medicine_id: string; quantity: number; dosage_instructions: string }>>([
    { medicine_id: '', quantity: 1, dosage_instructions: '' },
  ]);
  const [labRequests, setLabRequests] = useState<Array<{ test_name: string }>>([{ test_name: '' }]);
  const [form] = Form.useForm();

  const load = () => {
    setLoading(true);
    appointmentsApi.doctorQueue('SCHEDULED').then(setItems).finally(() => setLoading(false));
  };
  useEffect(load, []);
  useEffect(() => {
    pharmacyApi.listMedicines().then(setMedicines);
  }, []);

  useEffect(() => {
    if (!selected) {
      setPrescriptionItems([{ medicine_id: '', quantity: 1, dosage_instructions: '' }]);
      setLabRequests([{ test_name: '' }]);
    }
  }, [selected]);

  const addPrescriptionItem = () => {
    setPrescriptionItems([...prescriptionItems, { medicine_id: '', quantity: 1, dosage_instructions: '' }]);
  };

  const updatePrescriptionItem = (index: number, field: 'medicine_id' | 'quantity' | 'dosage_instructions', value: string | number | null) => {
    const next = [...prescriptionItems];
    next[index] = { ...next[index], [field]: value ?? '' } as typeof next[number];
    setPrescriptionItems(next);
  };

  const removePrescriptionItem = (index: number) => {
    setPrescriptionItems(prescriptionItems.filter((_, itemIndex) => itemIndex !== index));
  };

  const addLabRequest = () => {
    setLabRequests([...labRequests, { test_name: '' }]);
  };

  const updateLabRequest = (index: number, value: string) => {
    const next = [...labRequests];
    next[index] = { test_name: value };
    setLabRequests(next);
  };

  const removeLabRequest = (index: number) => {
    setLabRequests(labRequests.filter((_, itemIndex) => itemIndex !== index));
  };

  const onDocument = async () => {
    if (!selected) return;
    const values = await form.validateFields();
    try {
      const record = await emrApi.createRecord({
        appointment_id: selected.id,
        diagnosis: values.diagnosis,
        notes: values.notes,
      });

      const prescriptionPayload = prescriptionItems
        .filter((item) => item.medicine_id)
        .map((item) => ({
          medicine_id: item.medicine_id,
          quantity: item.quantity,
          dosage_instructions: item.dosage_instructions || undefined,
        }));

      if (prescriptionPayload.length) {
        await emrApi.createPrescription(record.id, prescriptionPayload);
      }

      const labPayload = labRequests.filter((item) => item.test_name.trim()).map((item) => item.test_name.trim());
      for (const testName of labPayload) {
        await laboratoryApi.create({ medical_record_id: record.id, test_name: testName });
      }

      message.success('Medical record and related orders saved');
      form.resetFields();
      setPrescriptionItems([{ medicine_id: '', quantity: 1, dosage_instructions: '' }]);
      setLabRequests([{ test_name: '' }]);
      setSelected(null);
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not save record');
    }
  };

  const onComplete = async (appointmentId: string) => {
    try {
      await appointmentsApi.complete(appointmentId);
      message.success('Appointment marked completed');
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Complete this appointment\'s medical record first');
    }
  };

  return (
    <div>
      <Typography.Title level={3}>My queue</Typography.Title>

      <Table
        rowKey="id"
        loading={loading}
        dataSource={items}
        columns={[
          { title: 'Scheduled at', dataIndex: 'scheduled_at', render: (v: string) => new Date(v).toLocaleString() },
          { title: 'Status', dataIndex: 'status', render: (s: string) => <StatusBadge status={s} /> },
          {
            title: 'Actions',
            render: (_, record: Appointment) => (
              <Space>
                <Button size="small" type="primary" ghost onClick={() => setSelected(record)}>
                  Document visit
                </Button>
                <Button size="small" onClick={() => onComplete(record.id)}>
                  Mark completed
                </Button>
              </Space>
            ),
          },
        ]}
      />

      <Drawer
        title="Document consultation"
        open={!!selected}
        onClose={() => setSelected(null)}
        width={420}
        extra={
          <Button type="primary" style={{ background: blue[600] }} onClick={onDocument}>
            Save
          </Button>
        }
      >
        <Form form={form} layout="vertical">
          <Form.Item name="diagnosis" label="Diagnosis" rules={[{ required: true }]}>
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="notes" label="Notes">
            <Input.TextArea rows={4} />
          </Form.Item>

          <Divider />
          <Typography.Text strong>Prescription</Typography.Text>
          {prescriptionItems.map((item, index) => (
            <Space key={index} direction="vertical" style={{ width: '100%', marginTop: 8 }}>
              <Select
                placeholder="Select medicine"
                options={medicines.map((medicine) => ({ value: medicine.id, label: `${medicine.name} (${medicine.quantity_in_stock} in stock)` }))}
                value={item.medicine_id || undefined}
                onChange={(value) => updatePrescriptionItem(index, 'medicine_id', value)}
              />
              <InputNumber min={1} value={item.quantity} style={{ width: '100%' }} onChange={(value) => updatePrescriptionItem(index, 'quantity', value ?? 1)} />
              <Input
                placeholder="Dosage instructions"
                value={item.dosage_instructions}
                onChange={(event) => updatePrescriptionItem(index, 'dosage_instructions', event.target.value)}
              />
              {prescriptionItems.length > 1 && (
                <Button type="link" danger onClick={() => removePrescriptionItem(index)}>
                  Remove
                </Button>
              )}
            </Space>
          ))}
          <Button type="dashed" style={{ marginTop: 8 }} onClick={addPrescriptionItem}>
            Add medicine
          </Button>

          <Divider />
          <Typography.Text strong>Lab requests</Typography.Text>
          {labRequests.map((item, index) => (
            <Space key={index} style={{ width: '100%', marginTop: 8 }}>
              <Input
                placeholder="Test name"
                value={item.test_name}
                onChange={(event) => updateLabRequest(index, event.target.value)}
              />
              {labRequests.length > 1 && (
                <Button type="link" danger onClick={() => removeLabRequest(index)}>
                  Remove
                </Button>
              )}
            </Space>
          ))}
          <Button type="dashed" style={{ marginTop: 8 }} onClick={addLabRequest}>
            Add lab test
          </Button>
        </Form>
      </Drawer>
    </div>
  );
}
