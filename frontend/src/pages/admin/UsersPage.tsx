import { useEffect, useState } from 'react';
import { Typography, Table, Button, Modal, Form, Input, Select, Switch, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { authApi, type User } from '../../api/authApi';
import { Role } from '../../constants/roles';

export function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const load = () => {
    setLoading(true);
    authApi.listUsers().then((r) => setUsers(r.data)).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const onCreate = async () => {
    const values = await form.validateFields();
    try {
      await authApi.createUser(values);
      message.success('User created');
      setModalOpen(false);
      form.resetFields();
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not create user');
    }
  };

  const onToggleStatus = async (user: User) => {
    try {
      await authApi.setUserStatus(user.id, !user.is_active);
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not update status');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>Users</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          Create user
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={loading}
        dataSource={users}
        columns={[
          { title: 'Username', dataIndex: 'username' },
          { title: 'Role', dataIndex: 'role' },
          {
            title: 'Active',
            dataIndex: 'is_active',
            render: (active: boolean, record: User) => (
              <Switch checked={active} onChange={() => onToggleStatus(record)} />
            ),
          },
        ]}
      />

      <Modal
        title="Create user"
        open={modalOpen}
        onOk={onCreate}
        onCancel={() => setModalOpen(false)}
        okText="Create"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="username" label="Username" rules={[{ required: true, min: 3 }]}>
            <Input />
          </Form.Item>
          <Form.Item name="password" label="Password" rules={[{ required: true, min: 8 }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item name="role" label="Role" rules={[{ required: true }]}>
            <Select options={Object.values(Role).map((r) => ({ value: r, label: r }))} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
