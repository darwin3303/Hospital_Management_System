import { useEffect, useState } from 'react';
import { Typography, Table, Button, Modal, Form, Input, Select, InputNumber, TimePicker, message, Space } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { doctorsApi, type Doctor } from '../../api/doctorsApi';
import { staffApi, type Employee } from '../../api/staffApi';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export function DoctorsPage() {
  const [items, setItems] = useState<Doctor[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const load = () => {
    setLoading(true);
    doctorsApi.list().then(setItems).finally(() => setLoading(false));
    staffApi.listEmployees().then((r) => setEmployees(r.data));
  };
  useEffect(load, []);

  const onCreate = async () => {
    const values = await form.validateFields();
    try {
      await doctorsApi.create({
        employee_id: values.employee_id,
        specialty: values.specialty,
        consultation_fee: values.consultation_fee,
        availability: (values.availability ?? []).map((slot: any) => ({
          day_of_week: slot.day_of_week,
          start_time: slot.range[0].format('HH:mm:ss'),
          end_time: slot.range[1].format('HH:mm:ss'),
        })),
      });
      message.success('Doctor profile created');
      setModalOpen(false);
      form.resetFields();
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not create doctor -- check the linked account has role DOCTOR');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>Doctors</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          Add doctor
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={loading}
        dataSource={items}
        columns={[
          { title: 'Specialty', dataIndex: 'specialty' },
          { title: 'Consultation fee', dataIndex: 'consultation_fee', render: (v: number) => `Rs ${v}` },
        ]}
      />

      <Modal
        title="Add doctor"
        open={modalOpen}
        onOk={onCreate}
        onCancel={() => setModalOpen(false)}
        okText="Create"
        width={560}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="employee_id"
            label="Employee (must be linked to a DOCTOR-role account)"
            rules={[{ required: true }]}
          >
            <Select
              options={employees.map((e) => ({
                value: e.id,
                label: `${e.first_name} ${e.last_name}${e.user_id ? '' : ' (no login linked)'}`,
              }))}
            />
          </Form.Item>
          <Form.Item name="specialty" label="Specialty" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="consultation_fee" label="Consultation fee" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>

          <Typography.Text strong>Working hours</Typography.Text>
          <Form.List name="availability">
            {(fields, { add, remove }) => (
              <>
                {fields.map((field) => (
                  <Space key={field.key} align="baseline" style={{ display: 'flex', marginTop: 8 }}>
                    <Form.Item name={[field.name, 'day_of_week']} rules={[{ required: true }]}>
                      <Select
                        style={{ width: 130 }}
                        placeholder="Day"
                        options={DAYS.map((d, i) => ({ value: i, label: d }))}
                      />
                    </Form.Item>
                    <Form.Item name={[field.name, 'range']} rules={[{ required: true }]}>
                      <TimePicker.RangePicker format="HH:mm" />
                    </Form.Item>
                    <MinusCircleOutlined onClick={() => remove(field.name)} />
                  </Space>
                ))}
                <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                  Add working hours slot
                </Button>
              </>
            )}
          </Form.List>
        </Form>
      </Modal>
    </div>
  );
}
