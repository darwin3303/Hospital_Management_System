import { useState } from 'react';
import { Typography, Input, Select, List, Card, Empty } from 'antd';
import { patientsApi, type Patient } from '../../api/patientsApi';
import { emrApi, type MedicalRecord } from '../../api/emrApi';

export function NursePatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [history, setHistory] = useState<MedicalRecord[]>([]);

  const onSearch = (q: string) => {
    if (q.length >= 2) patientsApi.search(q).then((r) => setPatients(r.data));
  };

  const onSelectPatient = (id: string) => {
    setSelectedPatientId(id);
    emrApi.getHistory(id).then(setHistory);
  };

  return (
    <div>
      <Typography.Title level={3}>Patient history</Typography.Title>
      <Typography.Text type="secondary">Read-only clinical history -- no editing controls on this screen.</Typography.Text>

      <div style={{ marginTop: 16, marginBottom: 24, maxWidth: 400 }}>
        <Select
          showSearch
          style={{ width: '100%' }}
          placeholder="Search patient by name or phone"
          filterOption={false}
          onSearch={onSearch}
          onChange={onSelectPatient}
          options={patients.map((p) => ({ value: p.id, label: `${p.first_name} ${p.last_name} (${p.phone})` }))}
        />
      </div>

      {!selectedPatientId && <Empty description="Search for a patient to view their history" />}

      {selectedPatientId && history.length === 0 && <Empty description="No medical records found" />}

      <List
        dataSource={history}
        renderItem={(record) => (
          <List.Item>
            <Card style={{ width: '100%' }}>
              <Typography.Text strong>Diagnosis:</Typography.Text> {record.diagnosis}
              <br />
              {record.notes && (
                <>
                  <Typography.Text strong>Notes:</Typography.Text> {record.notes}
                </>
              )}
            </Card>
          </List.Item>
        )}
      />
    </div>
  );
}
