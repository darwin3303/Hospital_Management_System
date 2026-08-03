import { useEffect, useState } from 'react';
import { Typography, Table, Button, Modal, Form, Input, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { staffApi, type Department } from '../../api/staffApi';

export function DepartmentsPage() {
  const [items, setItems] = useState<Department[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const load = () => {
    setLoading(true);
    staffApi.listDepartments().then(setItems).finally(() => setLoading(false));
  };
  useEffect(load, []);

  const onCreate = async () => {
    const values = await form.validateFields();
    try {
      await staffApi.createDepartment(values.name);
      message.success('Department created');
      setModalOpen(false);
      form.resetFields();
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not create department');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>Departments</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          Add department
        </Button>
      </div>

      <Table rowKey="id" loading={loading} dataSource={items} columns={[{ title: 'Name', dataIndex: 'name' }]} />

      <Modal title="Add department" open={modalOpen} onOk={onCreate} onCancel={() => setModalOpen(false)} okText="Create">
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Department name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
