import { useEffect, useState } from 'react';
import { Typography, Tabs, Table } from 'antd';
import { reportsApi } from '../../api/reportsApi';
import { StatusBadge } from '../../components/common/StatusBadge';

export function ReportsPage() {
  const [patients, setPatients] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<any[]>([]);
  const [pharmacy, setPharmacy] = useState<any[]>([]);
  const [laboratory, setLaboratory] = useState<any[]>([]);
  const [staff, setStaff] = useState<any[]>([]);

  useEffect(() => {
    reportsApi.patients().then(setPatients);
    reportsApi.appointments().then(setAppointments);
    reportsApi.pharmacy().then(setPharmacy);
    reportsApi.laboratory().then(setLaboratory);
    reportsApi.staff().then(setStaff);
  }, []);

  return (
    <div>
      <Typography.Title level={3}>Reports</Typography.Title>
      <Tabs
        items={[
          {
            key: 'patients',
            label: 'Patients',
            children: (
              <Table
                rowKey="id"
                dataSource={patients}
                columns={[
                  { title: 'First name', dataIndex: 'first_name' },
                  { title: 'Last name', dataIndex: 'last_name' },
                  { title: 'Phone', dataIndex: 'phone' },
                ]}
              />
            ),
          },
          {
            key: 'appointments',
            label: 'Appointments',
            children: (
              <Table
                rowKey="id"
                dataSource={appointments}
                columns={[
                  { title: 'Scheduled at', dataIndex: 'scheduled_at' },
                  { title: 'Status', dataIndex: 'status', render: (s: string) => <StatusBadge status={s} /> },
                ]}
              />
            ),
          },
          {
            key: 'pharmacy',
            label: 'Pharmacy',
            children: (
              <Table
                rowKey="medicine_name"
                dataSource={pharmacy}
                columns={[
                  { title: 'Medicine', dataIndex: 'medicine_name' },
                  { title: 'Stock', dataIndex: 'quantity_in_stock' },
                ]}
              />
            ),
          },
          {
            key: 'laboratory',
            label: 'Laboratory',
            children: (
              <Table
                rowKey="test_name"
                dataSource={laboratory}
                columns={[
                  { title: 'Test', dataIndex: 'test_name' },
                  { title: 'Status', dataIndex: 'status', render: (s: string) => <StatusBadge status={s} /> },
                ]}
              />
            ),
          },
          {
            key: 'staff',
            label: 'Staff',
            children: (
              <Table
                rowKey="employee_id"
                dataSource={staff}
                columns={[
                  { title: 'First name', dataIndex: 'first_name' },
                  { title: 'Last name', dataIndex: 'last_name' },
                ]}
              />
            ),
          },
        ]}
      />
    </div>
  );
}
