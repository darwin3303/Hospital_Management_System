import { useState } from 'react';
import { Form, Input, Button, Card, Typography, Alert } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { roleHomeRoute } from '../../constants/roles';
import { blue, neutral } from '../../theme/tokens';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const onFinish = async (values: { username: string; password: string }) => {
    setError(null);
    setSubmitting(true);
    try {
      const user = await login(values.username, values.password);
      navigate(roleHomeRoute[user.role] ?? '/');
    } catch (err: any) {
      setError(err?.response?.data?.message ?? 'Login failed. Check your credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: neutral[50],
      }}
    >
      <Card style={{ width: 380, borderRadius: 12 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Typography.Title level={3} style={{ color: blue[600], marginBottom: 4 }}>
            Hospital Management System
          </Typography.Title>
          <Typography.Text type="secondary">Sign in to continue</Typography.Text>
        </div>

        {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}

        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item name="username" label="Username" rules={[{ required: true }]}>
            <Input size="large" autoFocus />
          </Form.Item>
          <Form.Item name="password" label="Password" rules={[{ required: true }]}>
            <Input.Password size="large" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" size="large" block loading={submitting}>
              Sign in
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
