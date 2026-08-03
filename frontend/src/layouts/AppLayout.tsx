import { Layout, Menu, Avatar, Dropdown, Typography } from 'antd';
import {
  DashboardOutlined, TeamOutlined, ApartmentOutlined, MedicineBoxOutlined,
  CalendarOutlined, FileTextOutlined, ExperimentOutlined, ShoppingOutlined,
  DollarOutlined, UserOutlined, LogoutOutlined, IdcardOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Role } from '../constants/roles';
import { blue, neutral } from '../theme/tokens';

const { Sider, Header, Content } = Layout;

const navByRole: Record<string, { key: string; icon: React.ReactNode; label: string }[]> = {
  [Role.ADMIN]: [
    { key: '/admin/overview', icon: <DashboardOutlined />, label: 'Overview' },
    { key: '/admin/users', icon: <TeamOutlined />, label: 'Users' },
    { key: '/admin/departments', icon: <ApartmentOutlined />, label: 'Departments' },
    { key: '/admin/employees', icon: <IdcardOutlined />, label: 'Employees' },
    { key: '/admin/doctors', icon: <MedicineBoxOutlined />, label: 'Doctors' },
    { key: '/admin/reports', icon: <FileTextOutlined />, label: 'Reports' },
  ],
  [Role.RECEPTIONIST]: [
    { key: '/receptionist/patients', icon: <TeamOutlined />, label: 'Patients' },
    { key: '/receptionist/appointments', icon: <CalendarOutlined />, label: 'Appointments' },
  ],
  [Role.DOCTOR]: [
    { key: '/doctor/queue', icon: <CalendarOutlined />, label: 'My queue' },
  ],
  [Role.NURSE]: [
    { key: '/nurse/patients', icon: <TeamOutlined />, label: 'Patients' },
  ],
  [Role.LAB_STAFF]: [
    { key: '/laboratory/queue', icon: <ExperimentOutlined />, label: 'Lab queue' },
  ],
  [Role.PHARMACIST]: [
    { key: '/pharmacy/inventory', icon: <ShoppingOutlined />, label: 'Inventory' },
    { key: '/pharmacy/queue', icon: <MedicineBoxOutlined />, label: 'Dispense queue' },
  ],
  [Role.ACCOUNTANT]: [
    { key: '/billing/invoices', icon: <DollarOutlined />, label: 'Invoices' },
  ],
};

export function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  if (!user) return null;
  const items = navByRole[user.role] ?? [];

  const userMenuItems = [
    { key: 'logout', icon: <LogoutOutlined />, label: 'Log out' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={220} style={{ borderRight: `1px solid ${neutral[200]}` }}>
        <div style={{ padding: '20px 24px', fontWeight: 600, fontSize: 16, color: blue[600] }}>
          HMS
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={items}
          onClick={({ key }) => navigate(key)}
          style={{ border: 'none' }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: neutral[0],
            borderBottom: `1px solid ${neutral[200]}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            padding: '0 24px',
          }}
        >
          <Dropdown
            menu={{
              items: userMenuItems,
              onClick: ({ key }) => {
                if (key === 'logout') {
                  logout().then(() => navigate('/login'));
                }
              },
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
              <Avatar size={32} icon={<UserOutlined />} style={{ background: blue[100], color: blue[600] }} />
              <div style={{ lineHeight: 1.2 }}>
                <Typography.Text strong style={{ display: 'block', fontSize: 13 }}>
                  {user.username}
                </Typography.Text>
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  {user.role}
                </Typography.Text>
              </div>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ padding: 24, background: neutral[50] }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
