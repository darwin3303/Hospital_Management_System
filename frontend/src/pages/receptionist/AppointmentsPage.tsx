import { useEffect, useState } from 'react';
import { Typography, Table, Button, Modal, Form, Select, DatePicker, InputNumber, message, Space } from 'antd';
import { CopyOutlined, PlusOutlined } from '@ant-design/icons';
import { appointmentsApi, type Appointment } from '../../api/appointmentsApi';
import { doctorsApi, type Doctor } from '../../api/doctorsApi';
import { patientsApi, type Patient } from '../../api/patientsApi';
import { staffApi, type Employee } from '../../api/staffApi';
import { StatusBadge } from '../../components/common/StatusBadge';

export function AppointmentsPage() {
  const [items, setItems] = useState<Appointment[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [patientQuery, setPatientQuery] = useState('');
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const load = () => {
    setLoading(true);
    appointmentsApi.list({}).then((r) => setItems(r.data)).finally(() => setLoading(false));
    doctorsApi.list().then(setDoctors);
    staffApi.listEmployees().then((r) => setEmployees(r.data));
  };
  useEffect(load, []);

  const onSearchPatient = (q: string) => {
    setPatientQuery(q);
    if (q.length >= 2) patientsApi.search(q).then((r) => setPatients(r.data));
  };

  const copyToClipboard = async (value: string) => {
    if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(value);
      message.success('Appointment ID copied');
      return;
    }
    message.warning('Clipboard access is not available in this browser');
  };

  const onCreate = async () => {
    const values = await form.validateFields();
    try {
      const appointment = await appointmentsApi.book({
        patient_id: values.patient_id,
        doctor_id: values.doctor_id,
        scheduled_at: values.scheduled_at.toISOString(),
        duration_minutes: values.duration_minutes ?? 30,
      });

      // Clipboard copy is best-effort only -- never let it block success handling.
      try {
        if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
          await navigator.clipboard.writeText(appointment.id);
          message.success('Appointment booked and ID copied');
        } else {
          message.success('Appointment booked');
        }
      } catch {
        message.success('Appointment booked (clipboard copy failed -- copy the ID manually from the table)');
      }

      setModalOpen(false);
      form.resetFields();
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not book appointment');
    }
  };

  const onCancel = (appointmentId: string) => {
    Modal.confirm({
      title: 'Cancel this appointment?',
      content: 'This cannot be undone.',
      okText: 'Yes, cancel it',
      okType: 'danger',
      onOk: async () => {
        try {
          await appointmentsApi.cancel(appointmentId);
          message.success('Appointment cancelled');
          load();
        } catch (err: any) {
          message.error(err?.response?.data?.message ?? 'Could not cancel appointment');
        }
      },
    });
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>Appointments</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          Book appointment
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={loading}
        dataSource={items}
        columns={[
          { title: 'Appointment ID', dataIndex: 'id', render: (id: string) => (
            <Space>
              <span>{id}</span>
              <Button size="small" type="text" icon={<CopyOutlined />} onClick={() => copyToClipboard(id)} />
            </Space>
          ) },
          { title: 'Scheduled at', dataIndex: 'scheduled_at', render: (v: string) => new Date(v).toLocaleString() },
          { title: 'Duration (min)', dataIndex: 'duration_minutes' },
          { title: 'Status', dataIndex: 'status', render: (s: string) => <StatusBadge status={s} /> },
          {
            title: 'Actions',
            render: (_, record: Appointment) => (
              record.status === 'SCHEDULED' ? (
                <Button size="small" danger onClick={() => onCancel(record.id)}>
                  Cancel
                </Button>
              ) : null
            ),
          },
        ]}
      />

      <Modal title="Book appointment" open={modalOpen} onOk={onCreate} onCancel={() => setModalOpen(false)} okText="Book">
        <Form form={form} layout="vertical">
          <Form.Item name="patient_id" label="Patient" rules={[{ required: true }]}>
            <Select
              showSearch
              filterOption={false}
              onSearch={onSearchPatient}
              placeholder="Search patient by name or phone"
              options={patients.map((p) => ({ value: p.id, label: `${p.first_name} ${p.last_name} (${p.phone})` }))}
            />
          </Form.Item>
          <Form.Item name="doctor_id" label="Doctor" rules={[{ required: true }]}>
            <Select
              options={doctors.map((doctor) => {
                const employee = employees.find((entry) => entry.id === doctor.employee_id);
                const doctorName = employee ? `${employee.first_name} ${employee.last_name}` : 'Unknown doctor';
                return { value: doctor.id, label: `${doctorName} (${doctor.specialty})` };
              })}
            />
          </Form.Item>
          <Form.Item name="scheduled_at" label="Date and time" rules={[{ required: true }]}>
            <DatePicker showTime style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="duration_minutes" label="Duration (minutes)" initialValue={30}>
            <InputNumber style={{ width: '100%' }} min={5} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}