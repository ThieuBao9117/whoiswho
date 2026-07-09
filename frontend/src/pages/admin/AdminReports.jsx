import React, { useState, useEffect } from 'react';
import { PieChart, Download, Printer, Users, Award, CheckCircle2, X, Eye, Clock, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../../services/api';

export default function AdminReports() {
  const [selectedMonth, setSelectedMonth] = useState("2026-03");
  const [stats, setStats] = useState({ total_employees: 0, completed_kpi: 0, projected_reward: 0, total_connections: 0 });
  const [report, setReport] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  // History Modal State
  const [selectedEmp, setSelectedEmp] = useState(null);
  const [historyData, setHistoryData] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  const openHistoryModal = async (emp) => {
    setSelectedEmp(emp);
    setHistoryLoading(true);
    setHistoryData(null);
    try {
      const res = await api.get(`/admin/report/${emp.emp_code}/history`);
      setHistoryData(res.data);
    } catch (err) {
      toast.error('Không thể lấy chi tiết kết nối');
      setSelectedEmp(null);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      const res = await api.post('/admin/trigger-sync');
      toast.success(res.data.message || 'Bắt đầu đồng bộ...');
    } catch (err) {
      toast.error('Lỗi khi kích hoạt đồng bộ');
    } finally {
      // It might run in background, so we just release the button immediately
      setSyncing(false);
    }
  };

  useEffect(() => { fetchData(); }, [selectedMonth]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, reportRes] = await Promise.all([
        api.get(`/admin/stats/${selectedMonth}`),
        api.get(`/admin/report/${selectedMonth}`)
      ]);
      setReport(reportRes.data);
      setStats({
        ...statsRes.data,
        completed_kpi: reportRes.data.filter(r => r.has_won).length,
        projected_reward: reportRes.data.reduce((sum, r) => sum + r.reward, 0)
      });
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const exportExcel = async () => {
    try {
      toast.loading("Đang xuất file Excel...", { id: "export" });
      const res = await api.get(`/admin/report/${selectedMonth}/export`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Chi_Tiet_Nguoi_Thang_Cuoc_${selectedMonth}.xlsx`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast.success("Xuất file Excel thành công!", { id: "export" });
    } catch (err) {
      toast.error("Lỗi khi xuất file Excel", { id: "export" });
    }
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
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-heading font-bold text-surface-800">Báo cáo kết nối</h1>
            <p className="text-sm text-surface-500 mt-1">Theo dõi tiến độ kết nối và phân bổ thưởng.</p>
          </div>
          <button onClick={handleSync} disabled={syncing} className="btn-primary text-sm flex items-center gap-2 px-4 py-2">
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Đang kích hoạt...' : 'Đồng bộ từ HRM'}
          </button>
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
            <button onClick={exportExcel} className="btn-primary text-xs flex items-center gap-1.5">
              <Download className="w-4 h-4" /> Xuất Excel
            </button>
          </div>
        </div>
      </div>

      {/* Print header */}
      <div className="print-only hidden text-center mb-8">
        <h1 className="text-2xl font-bold">BÁO CÁO KẾT NỐI WHO IS WHO</h1>
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
                  <th className="py-3.5 px-5 text-center">Hành động</th>
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
                    <td className="py-3.5 px-5 text-center">
                      <button onClick={() => openHistoryModal(r)} className="btn-secondary text-xs px-2 py-1 flex items-center gap-1 mx-auto">
                        <Eye className="w-3.5 h-3.5" /> Chi tiết
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* History Modal */}
      {selectedEmp && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-surface-900/40 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-xl animate-slide-up">
            <div className="p-5 border-b border-surface-200 flex items-center justify-between bg-surface-50 rounded-t-2xl">
              <div>
                <h3 className="font-heading font-bold text-lg text-surface-800">Chi tiết kết nối</h3>
                <p className="text-sm text-surface-500 mt-0.5">{selectedEmp.full_name} ({selectedEmp.emp_code})</p>
              </div>
              <button onClick={() => setSelectedEmp(null)} className="p-2 hover:bg-surface-200 rounded-full text-surface-500 transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-5 overflow-y-auto flex-1">
              {historyLoading ? (
                <div className="py-20 flex justify-center"><div className="w-8 h-8 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div>
              ) : historyData ? (
                <div className="space-y-6">
                  {/* Progress overview */}
                  <div className="bg-surface-50 p-4 rounded-xl border border-surface-200 flex justify-between items-center">
                    <div>
                      <p className="text-sm text-surface-500">Tiến độ hiện tại</p>
                      <p className="font-heading font-bold text-xl text-surface-800">
                        {historyData.progress.current} / {historyData.progress.target}
                      </p>
                    </div>
                    <div>
                      {historyData.progress.has_won ? (
                        <span className="badge badge-success px-3 py-1 text-sm">✅ Đạt chỉ tiêu</span>
                      ) : historyData.progress.is_expired ? (
                        <span className="badge badge-danger px-3 py-1 text-sm">❌ Đã hết hạn</span>
                      ) : (
                        <span className="badge badge-accent px-3 py-1 text-sm">⏳ Còn {historyData.progress.days_remaining} ngày</span>
                      )}
                    </div>
                  </div>

                  {/* Connection list */}
                  <div>
                    <h4 className="font-semibold text-surface-800 mb-3 flex items-center gap-2">
                      <Users className="w-4 h-4 text-primary-500" />
                      Lịch sử kết nối ({historyData.history.length})
                    </h4>
                    {historyData.history.length === 0 ? (
                      <p className="text-center py-6 text-surface-400 text-sm">Chưa có hoạt động kết nối nào.</p>
                    ) : (
                      <div className="space-y-3">
                        {historyData.history.map(h => (
                          <div key={h.connection_id} className="flex items-center justify-between p-3 border border-surface-200 rounded-xl hover:bg-surface-50 transition-colors">
                            <div className="flex items-center gap-3">
                              <img src={h.other_person.photo || `https://i.pravatar.cc/150?u=${h.other_person.emp_code}`} className="w-10 h-10 rounded-full object-cover border border-surface-200" alt="" />
                              <div>
                                <p className="font-semibold text-surface-800 text-sm">{h.other_person.full_name}</p>
                                <p className="text-xs text-surface-500 mt-0.5">{h.other_person.department} • {h.direction === 'sent' ? 'Đã gửi yêu cầu' : 'Nhận yêu cầu'}</p>
                              </div>
                            </div>
                            <div className="text-right">
                              {h.status === 'ACCEPTED' ? (
                                <span className="badge badge-success text-[10px]"><CheckCircle2 className="w-3 h-3 mr-1" /> Chấp nhận</span>
                              ) : h.status === 'PENDING' ? (
                                <span className="badge badge-accent text-[10px]"><Clock className="w-3 h-3 mr-1" /> Đang chờ</span>
                              ) : (
                                <span className="badge badge-danger text-[10px]"><X className="w-3 h-3 mr-1" /> Từ chối</span>
                              )}
                              <p className="text-[10px] text-surface-400 mt-1">
                                {new Date(h.created_at).toLocaleString('vi-VN')}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
