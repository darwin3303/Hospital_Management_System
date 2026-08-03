import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/queryClient';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './routes/ProtectedRoute';
import { AppLayout } from './layouts/AppLayout';
import { themeConfig } from './theme/themeConfig';
import { Role, roleHomeRoute } from './constants/roles';

import { LoginPage } from './pages/auth/LoginPage';
import { OverviewPage } from './pages/admin/OverviewPage';
import { UsersPage } from './pages/admin/UsersPage';
import { DepartmentsPage } from './pages/admin/DepartmentsPage';
import { EmployeesPage } from './pages/admin/EmployeesPage';
import { DoctorsPage } from './pages/admin/DoctorsPage';
import { ReportsPage } from './pages/admin/ReportsPage';
import { PatientsPage as ReceptionistPatientsPage } from './pages/receptionist/PatientsPage';
import { AppointmentsPage } from './pages/receptionist/AppointmentsPage';
import { DoctorQueuePage } from './pages/doctor/DoctorQueuePage';
import { NursePatientsPage } from './pages/nurse/NursePatientsPage';
import { LabQueuePage } from './pages/laboratory/LabQueuePage';
import { InventoryPage } from './pages/pharmacy/InventoryPage';
import { DispenseQueuePage } from './pages/pharmacy/DispenseQueuePage';
import { InvoicesPage } from './pages/billing/InvoicesPage';

function RootRedirect() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={roleHomeRoute[user.role] ?? '/login'} replace />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<RootRedirect />} />

      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        {/* Admin */}
        <Route
          path="/admin/overview"
          element={<ProtectedRoute allowedRoles={[Role.ADMIN]}><OverviewPage /></ProtectedRoute>}
        />
        <Route
          path="/admin/users"
          element={<ProtectedRoute allowedRoles={[Role.ADMIN]}><UsersPage /></ProtectedRoute>}
        />
        <Route
          path="/admin/departments"
          element={<ProtectedRoute allowedRoles={[Role.ADMIN]}><DepartmentsPage /></ProtectedRoute>}
        />
        <Route
          path="/admin/employees"
          element={<ProtectedRoute allowedRoles={[Role.ADMIN]}><EmployeesPage /></ProtectedRoute>}
        />
        <Route
          path="/admin/doctors"
          element={<ProtectedRoute allowedRoles={[Role.ADMIN]}><DoctorsPage /></ProtectedRoute>}
        />
        <Route
          path="/admin/reports"
          element={<ProtectedRoute allowedRoles={[Role.ADMIN]}><ReportsPage /></ProtectedRoute>}
        />

        {/* Receptionist */}
        <Route
          path="/receptionist/patients"
          element={<ProtectedRoute allowedRoles={[Role.RECEPTIONIST, Role.ADMIN]}><ReceptionistPatientsPage /></ProtectedRoute>}
        />
        <Route
          path="/receptionist/appointments"
          element={<ProtectedRoute allowedRoles={[Role.RECEPTIONIST, Role.ADMIN]}><AppointmentsPage /></ProtectedRoute>}
        />

        {/* Doctor */}
        <Route
          path="/doctor/queue"
          element={<ProtectedRoute allowedRoles={[Role.DOCTOR]}><DoctorQueuePage /></ProtectedRoute>}
        />

        {/* Nurse */}
        <Route
          path="/nurse/patients"
          element={<ProtectedRoute allowedRoles={[Role.NURSE]}><NursePatientsPage /></ProtectedRoute>}
        />

        {/* Laboratory */}
        <Route
          path="/laboratory/queue"
          element={<ProtectedRoute allowedRoles={[Role.LAB_STAFF, Role.ADMIN]}><LabQueuePage /></ProtectedRoute>}
        />

        {/* Pharmacy */}
        <Route
          path="/pharmacy/inventory"
          element={<ProtectedRoute allowedRoles={[Role.PHARMACIST, Role.ADMIN]}><InventoryPage /></ProtectedRoute>}
        />
        <Route
          path="/pharmacy/queue"
          element={<ProtectedRoute allowedRoles={[Role.PHARMACIST, Role.ADMIN]}><DispenseQueuePage /></ProtectedRoute>}
        />

        {/* Billing */}
        <Route
          path="/billing/invoices"
          element={<ProtectedRoute allowedRoles={[Role.ACCOUNTANT, Role.ADMIN]}><InvoicesPage /></ProtectedRoute>}
        />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider theme={themeConfig}>
        <AuthProvider>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </AuthProvider>
      </ConfigProvider>
    </QueryClientProvider>
  );
}
