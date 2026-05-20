import React, { useState, useEffect } from 'react';
import { PieChart, Download, Printer, Users, Award, CheckCircle2, X } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../../services/api';

export default function AdminReports() {
  const [selectedMonth, setSelectedMonth] = useState("2026-03");
  const [stats, setStats] = useState({ total_employees: 0, completed_kpi: 0, projected_reward: 0, total_connections: 0 });
  const [report, setReport] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchData(); }, [selectedMonth]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, reportRes] = await Promise.all([
        api.get(`/admin/stats/${selectedMonth}`),
        api.get(`/admin/report/${selectedMonth}`)
      ]);
      setStats(statsRes.data);
      setReport(reportRes.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const exportCSV = () => {
    const headers = "Mã NV,Họ tên,Phòng ban,Tháng,Tiến độ,Tiền thưởng (VND)\n";
    const rows = report.map(r => `${r.emp_code},${r.full_name},${r.department},${selectedMonth},${r.count},${r.reward}`).join("\n");
    const csvContent = "data:text/csv;charset=utf-8,\uFEFF" + headers + rows;
    const link = document.createElement("a");
    link.setAttribute("href", encodeURI(csvContent));
    link.setAttribute("download", `BaoCao_CSB-Connection_${selectedMonth}.csv`);
    document.body.appendChild(link); link.click(); document.body.removeChild(link);
    toast.success("Đã xuất file CSV!");
  };

  const StatCard = ({ label, value, suffix, color }) => (
    <div className="card p-5 text-center">
      <p className="text-sm text-surface-500 mb-1">{label}</p>
      <p className={`text-2xl font-heading font-bold ${color}`}>{value} {suffix && <span className="text-sm text-surface-400 font-normal">{suffix}</span>}</p>
    </div>
  );

  return (
    <div className="p-5 md:p-8 flex-1 animate-fade-in">
      <div className="no-print mb-6 space-y-5">
        <div>
          <h1 className="text-2xl font-heading font-bold text-surface-800">Báo cáo kết nối</h1>
          <p className="text-sm text-surface-500 mt-1">Theo dõi tiến độ kết nối và phân bổ thưởng.</p>
        </div>

        <div className="card p-4 flex flex-col lg:flex-row gap-3 items-start lg:items-center">
          <div className="flex items-center gap-2">
            <label className="font-semibold text-surface-700 text-sm">Tháng:</label>
            <input type="month" value={selectedMonth} onChange={(e) => setSelectedMonth(e.target.value)}
              className="input-field py-2.5 w-48" />
          </div>
          <div className="flex-1" />
          <div className="flex gap-2">
            <button onClick={() => window.print()} className="btn-secondary text-xs flex items-center gap-1.5">
              <Printer className="w-4 h-4" /> In báo cáo
            </button>
            <button onClick={exportCSV} className="btn-primary text-xs flex items-center gap-1.5">
              <Download className="w-4 h-4" /> Xuất CSV
            </button>
          </div>
        </div>
      </div>

      {/* Print header */}
      <div className="print-only hidden text-center mb-8">
        <h1 className="text-2xl font-bold">BÁO CÁO KẾT NỐI CSB CONNECTION</h1>
        <p className="text-lg mt-2 text-gray-600">Tháng: {selectedMonth}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Tổng nhân viên" value={stats.total_employees} color="text-primary-600" />
        <StatCard label="Đạt chỉ tiêu" value={stats.completed_kpi} suffix="người" color="text-success-600" />
        <StatCard label="Tổng thưởng dự kiến" value={stats.projected_reward?.toLocaleString()} suffix="VNĐ" color="text-accent-600" />
        <StatCard label="Tổng kết nối" value={stats.total_connections} color="text-primary-600" />
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="bg-surface-50 px-5 py-4 border-b border-surface-200">
          <h3 className="font-heading font-bold text-surface-800 text-sm">Chi tiết theo nhân viên — {selectedMonth}</h3>
        </div>
        <div className="overflow-x-auto">
          {loading ? (
            <div className="py-16 flex justify-center"><div className="w-10 h-10 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div>
          ) : (
            <table className="w-full text-left min-w-[600px]">
              <thead>
                <tr className="bg-surface-50 text-surface-500 text-xs font-semibold border-b border-surface-200">
                  <th className="py-3.5 px-5">Mã NV</th>
                  <th className="py-3.5 px-5">Họ tên</th>
                  <th className="py-3.5 px-5">Phòng ban</th>
                  <th className="py-3.5 px-5 text-center">Tiến độ</th>
                  <th className="py-3.5 px-5 text-right">Thưởng (VNĐ)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100 text-sm">
                {report.map(r => (
                  <tr key={r.emp_code} className="hover:bg-surface-50 transition-colors">
                    <td className="py-3.5 px-5 text-surface-500">{r.emp_code}</td>
                    <td className="py-3.5 px-5 font-semibold text-surface-800">{r.full_name}</td>
                    <td className="py-3.5 px-5 text-surface-500">{r.department}</td>
                    <td className="py-3.5 px-5 text-center">
                      {r.has_won ? (
                        <span className="badge badge-success">✅ Đạt {r.count}</span>
                      ) : r.is_expired ? (
                        <span className="badge badge-danger">❌ Hết hạn {r.count}</span>
                      ) : (
                        <span className="badge badge-accent">⏳ Đang làm {r.count}</span>
                      )}
                    </td>
                    <td className="py-3.5 px-5 text-right font-semibold text-accent-600">
                      {r.reward > 0 ? r.reward.toLocaleString() : '0'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
