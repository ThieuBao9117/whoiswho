import React, { useState, useEffect } from 'react';
import { Settings } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../../services/api';

export default function AdminTargets() {
  const [selectedMonth, setSelectedMonth] = useState("2026-03");
  const [target, setTarget] = useState({
    period_str: "2026-03", operator_required: 5, leader_required: 2,
    pl_required: 1, tm_required: 1, gd_required: 0, reward_amount: 200000
  });

  useEffect(() => { fetchTarget(); }, [selectedMonth]);

  const fetchTarget = async () => {
    try { const res = await api.get(`/targets/${selectedMonth}`); setTarget(res.data); }
    catch (err) { console.error(err); }
  };

  const handleSave = async () => {
    try { await api.post('/targets/', target); toast.success(`Đã lưu chỉ tiêu tháng ${selectedMonth}`); }
    catch { toast.error("Không thể lưu"); }
  };

  const NumberInput = ({ label, value, field }) => (
    <div className="bg-surface-50 rounded-xl p-4">
      <label className="text-sm font-medium text-surface-600 block mb-2">{label}</label>
      <input type="number" value={value}
        onChange={(e) => setTarget({ ...target, [field]: parseInt(e.target.value) || 0 })}
        className="input-field text-lg font-semibold" />
    </div>
  );

  return (
    <div className="p-5 md:p-8 flex-1 animate-fade-in">
      <h1 className="text-2xl font-heading font-bold text-surface-800 mb-6">Thiết lập chỉ tiêu</h1>
      <div className="card p-6 md:p-8 max-w-2xl">
        {/* Month picker */}
        <div className="bg-primary-50 rounded-xl p-4 mb-6 flex flex-col sm:flex-row sm:items-center gap-3">
          <label className="font-semibold text-primary-700 text-sm">Tháng áp dụng:</label>
          <input type="month" value={selectedMonth} onChange={(e) => setSelectedMonth(e.target.value)}
            className="input-field py-2.5 flex-1 sm:max-w-[200px]" />
        </div>

        {/* Required scans */}
        <h2 className="text-lg font-heading font-bold text-surface-800 mb-4 flex items-center gap-2">
          <span className="w-7 h-7 bg-primary-100 text-primary-600 rounded-lg flex items-center justify-center text-sm font-bold">1</span>
          Số lượt quét yêu cầu
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          <NumberInput label="Công nhân (Operator)" value={target.operator_required} field="operator_required" />
          <NumberInput label="Trưởng ca (Leader)" value={target.leader_required} field="leader_required" />
          <NumberInput label="Trưởng bộ phận (Part Leader)" value={target.pl_required} field="pl_required" />
          <NumberInput label="Trưởng nhóm (Team Manager)" value={target.tm_required} field="tm_required" />
          <div className="sm:col-span-2 bg-accent-50 rounded-xl p-4 border border-accent-200">
            <label className="text-sm font-medium text-accent-700 block mb-2">Giám đốc (GD) — Thưởng thêm</label>
            <input type="number" value={target.gd_required}
              onChange={(e) => setTarget({ ...target, gd_required: parseInt(e.target.value) || 0 })}
              className="input-field text-lg font-semibold" />
          </div>
        </div>

        {/* Reward */}
        <h2 className="text-lg font-heading font-bold text-surface-800 mb-4 flex items-center gap-2">
          <span className="w-7 h-7 bg-accent-100 text-accent-600 rounded-lg flex items-center justify-center text-sm font-bold">2</span>
          Mức thưởng
        </h2>
        <div className="bg-accent-50 rounded-xl p-4 mb-8 border border-accent-200">
          <label className="text-sm font-medium text-accent-700 block mb-2">Tiền thưởng (VNĐ)</label>
          <div className="relative">
            <input type="number" value={target.reward_amount}
              onChange={(e) => setTarget({ ...target, reward_amount: parseFloat(e.target.value) || 0 })}
              className="input-field text-2xl font-bold pr-16" />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 font-semibold text-accent-600">VNĐ</span>
          </div>
        </div>

        <button onClick={handleSave} className="btn-primary w-full py-3.5 text-base">
          💾 Lưu chỉ tiêu tháng {selectedMonth}
        </button>
      </div>
    </div>
  );
}
