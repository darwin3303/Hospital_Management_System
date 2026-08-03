import { useEffect, useState } from 'react';
import { Typography, Table, Button, Modal, Form, Input, Select, DatePicker, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { staffApi, type Department, type Employee } from '../../api/staffApi';
import { authApi, type User } from '../../api/authApi';

export function EmployeesPage() {
  const [items, setItems] = useState<Employee[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const load = () => {
    setLoading(true);
    staffApi.listEmployees().then((r) => setItems(r.data)).finally(() => setLoading(false));
    staffApi.listDepartments().then(setDepartments);
    authApi.listUsers().then((r) => setUsers(r.data));
  };
  useEffect(load, []);

  const onCreate = async () => {
    const values = await form.validateFields();
    try {
      await staffApi.createEmployee({
        ...values,
        hired_at: values.hired_at ? values.hired_at.format('YYYY-MM-DD') : undefined,
      });
      message.success('Employee created');
      setModalOpen(false);
      form.resetFields();
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not create employee');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>Employees</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          Add employee
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={loading}
        dataSource={items}
        columns={[
          { title: 'First name', dataIndex: 'first_name' },
          { title: 'Last name', dataIndex: 'last_name' },
          { title: 'Phone', dataIndex: 'phone' },
          { title: 'Hired', dataIndex: 'hired_at' },
          { title: 'Linked user', dataIndex: 'user_id', render: (v: string | null) => v ?? '—' },
        ]}
      />

      <Modal title="Add employee" open={modalOpen} onOk={onCreate} onCancel={() => setModalOpen(false)} okText="Create">
        <Form form={form} layout="vertical">
          <Form.Item name="first_name" label="First name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="last_name" label="Last name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="Phone">
            <Input />
          </Form.Item>
          <Form.Item name="department_id" label="Department" rules={[{ required: true }]}>
            <Select options={departments.map((d) => ({ value: d.id, label: d.name }))} />
          </Form.Item>
          <Form.Item name="user_id" label="Linked login account (optional)">
            <Select
              allowClear
              options={users.map((u) => ({ value: u.id, label: `${u.username} (${u.role})` }))}
            />
          </Form.Item>
          <Form.Item name="hired_at" label="Hired date" initialValue={dayjs()}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
