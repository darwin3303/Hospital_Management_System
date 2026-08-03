import { useEffect, useState } from 'react';
import { Typography, Table, Button, Modal, InputNumber, message } from 'antd';
import { pharmacyApi, type Medicine } from '../../api/pharmacyApi';
import type { PrescriptionItem } from '../../api/emrApi';
import { StatusBadge } from '../../components/common/StatusBadge';

export function DispenseQueuePage() {
  const [items, setItems] = useState<PrescriptionItem[]>([]);
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [loading, setLoading] = useState(false);
  const [dispenseModal, setDispenseModal] = useState<PrescriptionItem | null>(null);
  const [dispenseQuantity, setDispenseQuantity] = useState<number>(1);

  const load = () => {
    setLoading(true);
    pharmacyApi.pendingPrescriptions().then(setItems).finally(() => setLoading(false));
    pharmacyApi.listMedicines().then(setMedicines);
  };
  useEffect(load, []);

  const medicineName = (medicineId: string) =>
    medicines.find((m) => m.id === medicineId)?.name ?? medicineId;

  const openDispenseModal = (item: PrescriptionItem) => {
    setDispenseModal(item);
    setDispenseQuantity(item.quantity); // defaults to the prescribed quantity, editable
  };

  const onConfirmDispense = async () => {
    if (!dispenseModal) return;
    try {
      await pharmacyApi.dispense(dispenseModal.id, dispenseQuantity);
      message.success('Medicine dispensed');
      setDispenseModal(null);
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.message ?? 'Could not dispense');
    }
  };

  return (
    <div>
      <Typography.Title level={3}>Dispense queue</Typography.Title>

      <Table
        rowKey="id"
        loading={loading}
        dataSource={items}
        columns={[
          { title: 'Medicine', dataIndex: 'medicine_id', render: (id: string) => medicineName(id) },
          { title: 'Prescribed quantity', dataIndex: 'quantity' },
          { title: 'Status', dataIndex: 'status', render: (s: string) => <StatusBadge status={s} /> },
          {
            title: 'Actions',
            render: (_, record: PrescriptionItem) => (
              <Button size="small" type="primary" ghost onClick={() => openDispenseModal(record)}>
                Dispense
              </Button>
            ),
          },
        ]}
      />

      <Modal
        title="Confirm dispense"
        open={!!dispenseModal}
        onOk={onConfirmDispense}
        onCancel={() => setDispenseModal(null)}
        okText="Dispense"
      >
        {dispenseModal && (
          <>
            <p>
              Medicine: <strong>{medicineName(dispenseModal.medicine_id)}</strong>
              <br />
              Prescribed quantity: <strong>{dispenseModal.quantity}</strong>
            </p>
            <Typography.Text>Quantity to dispense</Typography.Text>
            <InputNumber
              style={{ width: '100%' }}
              min={1}
              max={dispenseModal.quantity}
              value={dispenseQuantity}
              onChange={(value) => setDispenseQuantity(value ?? 1)}
            />
          </>
        )}
      </Modal>
    </div>
  );
}