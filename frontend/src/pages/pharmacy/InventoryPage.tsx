import { useEffect, useState } from 'react';
import { Typography, Table, Button, Modal, Form, Input, InputNumber, DatePicker, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { pharmacyApi, type Medicine } from '../../api/pharmacyApi';

export function InventoryPage() {
  const [items, setItems] = useState<Medicine[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const load = () => {
    setLoading(true);
    pharmacyApi.listMedicines().then(setItems).finally(() => setLoading(false));
  };
  useEffect(load, []);

  const onCreate = async () => {
    const values = await form.validateFields();
    try {
      await pharmacyApi.addMedicine({
        ...values,
        expiry_date: values.expiry_date.format('YYYY-MM-DD'),
      });
      message.success('Medicine added');
      setModalOpen(false);
      form.resetFields();
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not add medicine');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>Inventory</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          Add medicine
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={loading}
        dataSource={items}
        columns={[
          { title: 'Name', dataIndex: 'name' },
          { title: 'Unit price', dataIndex: 'unit_price', render: (v: number) => `Rs ${v}` },
          { title: 'Stock', dataIndex: 'quantity_in_stock' },
          { title: 'Expiry', dataIndex: 'expiry_date' },
        ]}
      />

      <Modal title="Add medicine" open={modalOpen} onOk={onCreate} onCancel={() => setModalOpen(false)} okText="Add">
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="unit_price" label="Unit price" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>
          <Form.Item name="quantity_in_stock" label="Quantity in stock" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>
          <Form.Item name="expiry_date" label="Expiry date" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
