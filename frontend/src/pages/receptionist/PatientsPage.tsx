import { useState } from 'react';
import { Typography, Input, Table, Button, Modal, Form, DatePicker, Select, message } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { patientsApi, type Patient } from '../../api/patientsApi';

export function PatientsPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const search = (q: string) => {
    setLoading(true);
    patientsApi.search(q).then((r) => setResults(r.data)).finally(() => setLoading(false));
  };

  const onCreate = async () => {
    const values = await form.validateFields();
    try {
      await patientsApi.register({
        ...values,
        date_of_birth: values.date_of_birth ? values.date_of_birth.format('YYYY-MM-DD') : null,
      });
      message.success('Patient registered');
      setModalOpen(false);
      form.resetFields();
      search(query);
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not register patient');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>Patients</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          Register patient
        </Button>
      </div>

      <Input.Search
        placeholder="Search by name or phone"
        enterButton={<SearchOutlined />}
        style={{ marginBottom: 16, maxWidth: 400 }}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onSearch={search}
      />

      <Table
        rowKey="id"
        loading={loading}
        dataSource={results}
        columns={[
          { title: 'First name', dataIndex: 'first_name' },
          { title: 'Last name', dataIndex: 'last_name' },
          { title: 'Phone', dataIndex: 'phone' },
          { title: 'Gender', dataIndex: 'gender' },
        ]}
      />

      <Modal title="Register patient" open={modalOpen} onOk={onCreate} onCancel={() => setModalOpen(false)} okText="Register">
        <Form form={form} layout="vertical">
          <Form.Item name="first_name" label="First name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="last_name" label="Last name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="Phone" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="date_of_birth" label="Date of birth">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="gender" label="Gender">
            <Select options={[{ value: 'MALE', label: 'Male' }, { value: 'FEMALE', label: 'Female' }, { value: 'OTHER', label: 'Other' }]} />
          </Form.Item>
          <Form.Item name="address" label="Address">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
