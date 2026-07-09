import React, { useState, useEffect } from 'react';
import { UserCheck, CheckCircle2, X, Users, TrendingUp, Clock, Eye, ChevronUp, ChevronDown } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../../services/api';

export default function AdminConnections() {
  const [tab, setTab] = useState('progress'); // 'progress' | 'pending'
  const [connections, setConnections] = useState([]);
  const [report, setReport] = useState([]);
  const [stats, setStats] = useState({ total_employees: 0, total_connections: 0 });
  const [loading, setLoading] = useState(true);
  const [reportLoading, setReportLoading] = useState(true);
  const [selectedEmp, setSelectedEmp] = useState(null);
  const [historyData, setHistoryData] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [sortField, setSortField] = useState('current');
  const [sortDir, setSortDir] = useState('desc');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchIncoming();
    fetchReport();
  }, []);

  const fetchIncoming = async () => {
    setLoading(true);
    try { const res = await api.get('/connections/incoming'); setConnections(res.data); }
    catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const fetchReport = async () => {
    setReportLoading(true);
    try {
      const [reportRes, statsRes] = await Promise.all([
        api.get('/admin/report'),
        api.get('/admin/stats/all'),
      ]);
      setReport(reportRes.data);
      setStats(statsRes.data);
    } catch (err) { console.error(err); }
    finally { setReportLoading(false); }
  };

  const handleAction = async (id, accept) => {
    try {
      await api.put(`/connections/${id}?accept=${accept}`);
      toast.success(accept ? 'Đã chấp nhận kết nối' : 'Đã từ chối kết nối');
      fetchIncoming();
    } catch { toast.error('Thao tác thất bại'); }
  };

  const openHistory = async (emp) => {
    setSelectedEmp(emp);
    setHistoryLoading(true);
    setHistoryData(null);
    try {
      const res = await api.get(`/admin/report/${emp.emp_code}/history`);
      setHistoryData(res.data);
    } catch { toast.error('Không thể lấy chi tiết'); setSelectedEmp(null); }
    finally { setHistoryLoading(false); }
  };

  const handleSort = (field) => {
    if (sortField === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortField(field); setSortDir('desc'); }
  };

  const parseCount = (r) => {
    if (typeof r.count === 'string' && r.count.includes('/')) return parseInt(r.count.split('/')[0]);
    return parseInt(r.count) || 0;
  };

  const sortedReport = [...report]
    .filter(r => !search || r.full_name?.toLowerCase().includes(search.toLowerCase()) || r.emp_code?.toLowerCase().includes(search.toLowerCase()) || r.department?.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      let va, vb;
      if (sortField === 'current') { va = parseCount(a); vb = parseCount(b); }
      else if (sortField === 'name') { va = a.full_name; vb = b.full_name; }
      else if (sortField === 'dept') { va = a.department; vb = b.department; }
      else { va = a[sortField]; vb = b[sortField]; }
      if (va < vb) return sortDir === 'asc' ? -1 : 1;
      if (va > vb) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });

  const SortIcon = ({ field }) => {
    if (sortField !== field) return <span className="opacity-30 ml-1">↕</span>;
    return sortDir === 'asc' ? <ChevronUp className="inline w-3.5 h-3.5 ml-1" /> : <ChevronDown className="inline w-3.5 h-3.5 ml-1" />;
  };

  const wonCount = report.filter(r => r.has_won).length;
  const expiredCount = report.filter(r => r.is_expired && !r.has_won).length;
  const inProgressCount = report.filter(r => !r.has_won && !r.is_expired).length;

  return (
    <div className="p-5 md:p-8 flex-1 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-heading font-bold text-surface-800">Quản lý kết nối</h1>
          <p className="text-sm text-surface-500 mt-1">Theo dõi tiến độ kết nối của tất cả nhân viên</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => { fetchIncoming(); fetchReport(); }} className="btn-secondary text-sm flex items-center gap-2 px-3 py-2">
            🔄 Làm mới
          </button>
        </div>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-primary-600">{stats.total_employees || report.length}</div>
          <div className="text-xs text-surface-500 mt-1">Tổng nhân viên</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-success-600">{wonCount}</div>
          <div className="text-xs text-surface-500 mt-1">✅ Đạt chỉ tiêu</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-accent-600">{inProgressCount}</div>
          <div className="text-xs text-surface-500 mt-1">⏳ Đang kết nối</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-danger-600">{expiredCount}</div>
          <div className="text-xs text-surface-500 mt-1">❌ Hết hạn</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-5 border-b border-surface-200">
        <button
          onClick={() => setTab('progress')}
          className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors ${tab === 'progress' ? 'border-primary-500 text-primary-600' : 'border-transparent text-surface-500 hover:text-surface-700'}`}
        >
          <TrendingUp className="inline w-4 h-4 mr-1.5" />Tiến độ nhân viên
        </button>
        <button
          onClick={() => setTab('pending')}
          className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors ${tab === 'pending' ? 'border-primary-500 text-primary-600' : 'border-transparent text-surface-500 hover:text-surface-700'}`}
        >
          <UserCheck className="inline w-4 h-4 mr-1.5" />Chờ duyệt
          {connections.length > 0 && <span className="ml-1.5 bg-danger-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">{connections.length}</span>}
        </button>
      </div>

      {/* Tab: Tiến độ */}
      {tab === 'progress' && (
        <div className="card overflow-hidden">
          <div className="p-4 border-b border-surface-100 flex items-center gap-3">
            <input
              type="text"
              placeholder="Tìm theo tên, mã NV, phòng ban..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="input-field py-2 text-sm flex-1 max-w-xs"
            />
            <span className="text-xs text-surface-400">{sortedReport.length} nhân viên</span>
          </div>
          <div className="overflow-x-auto">
            {reportLoading ? (
              <div className="py-16 flex justify-center">
                <div className="w-10 h-10 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
              </div>
            ) : (
              <table className="w-full text-left min-w-[640px]">
                <thead>
                  <tr className="bg-surface-50 text-surface-500 text-xs font-semibold border-b border-surface-200">
                    <th className="py-3.5 px-4">#</th>
                    <th className="py-3.5 px-4 cursor-pointer hover:text-primary-600" onClick={() => handleSort('name')}>
                      Nhân viên <SortIcon field="name" />
                    </th>
                    <th className="py-3.5 px-4 cursor-pointer hover:text-primary-600" onClick={() => handleSort('dept')}>
                      Phòng ban <SortIcon field="dept" />
                    </th>
                    <th className="py-3.5 px-4 text-center cursor-pointer hover:text-primary-600" onClick={() => handleSort('current')}>
                      Tiến độ <SortIcon field="current" />
                    </th>
                    <th className="py-3.5 px-4 text-center">Trạng thái</th>
                    <th className="py-3.5 px-4 text-center">Chi tiết</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-100 text-sm">
                  {sortedReport.length === 0 ? (
                    <tr><td colSpan="6" className="py-16 text-center text-surface-400">Không có dữ liệu</td></tr>
                  ) : sortedReport.map((r, idx) => {
                    const current = parseCount(r);
                    const parts = typeof r.count === 'string' && r.count.includes('/') ? r.count.split('/') : [current, 30];
                    const target = parseInt(parts[1]) || 30;
                    const pct = Math.min(100, Math.round((current / target) * 100));

                    return (
                      <tr key={r.emp_code} className="hover:bg-surface-50 transition-colors">
                        <td className="py-3.5 px-4 text-surface-400 text-xs font-mono">{idx + 1}</td>
                        <td className="py-3.5 px-4">
                          <div className="font-semibold text-surface-800">{r.full_name}</div>
                          <div className="text-xs text-surface-400">{r.emp_code}</div>
                        </td>
                        <td className="py-3.5 px-4 text-surface-500 text-xs">{r.department}</td>
                        <td className="py-3.5 px-4">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-surface-100 rounded-full h-2 min-w-[60px]">
                              <div
                                className={`h-2 rounded-full transition-all ${r.has_won ? 'bg-success-500' : r.is_expired ? 'bg-danger-400' : 'bg-primary-500'}`}
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                            <span className="text-xs font-bold text-surface-600 whitespace-nowrap">{current}/{target}</span>
                          </div>
                        </td>
                        <td className="py-3.5 px-4 text-center">
                          {r.has_won ? (
                            <span className="badge badge-success text-[11px]">✅ Đạt</span>
                          ) : r.is_expired ? (
                            <span className="badge badge-danger text-[11px]">❌ Hết hạn</span>
                          ) : (
                            <span className="badge badge-accent text-[11px]">⏳ {r.days_remaining}d</span>
                          )}
                        </td>
                        <td className="py-3.5 px-4 text-center">
                          <button onClick={() => openHistory(r)} className="btn-secondary text-xs px-2.5 py-1.5 flex items-center gap-1 mx-auto">
                            <Eye className="w-3.5 h-3.5" /> Xem
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* Tab: Chờ duyệt */}
      {tab === 'pending' && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            {loading ? (
              <div className="py-16 flex justify-center"><div className="w-10 h-10 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div>
            ) : (
              <table className="w-full text-left min-w-[500px]">
                <thead>
                  <tr className="bg-surface-50 text-surface-500 text-xs font-semibold border-b border-surface-200">
                    <th className="py-4 px-5">Nhân viên</th>
                    <th className="py-4 px-5 text-center">Trạng thái</th>
                    <th className="py-4 px-5 text-right">Thao tác</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-100 text-sm">
                  {connections.length > 0 ? connections.map(c => (
                    <tr key={c.id} className="hover:bg-surface-50 transition-colors">
                      <td className="py-4 px-5">
                        <div className="flex items-center gap-3">
                          <img src={c.new_hire.photo || `https://i.pravatar.cc/150?u=${c.new_hire.id}`} className="w-10 h-10 rounded-full border border-surface-200 object-cover" alt="" />
                          <div>
                            <div className="font-semibold text-surface-800">{c.new_hire.full_name}</div>
                            <div className="text-xs text-surface-400">{c.new_hire.emp_code} • {c.new_hire.department}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-5 text-center"><span className="badge badge-accent">Chờ duyệt</span></td>
                      <td className="py-4 px-5 text-right">
                        <div className="flex justify-end gap-2">
                          <button onClick={() => handleAction(c.id, false)} className="btn-danger text-xs px-3 py-1.5">Từ chối</button>
                          <button onClick={() => handleAction(c.id, true)} className="btn-success text-xs px-3 py-1.5">Chấp nhận</button>
                        </div>
                      </td>
                    </tr>
                  )) : (
                    <tr><td colSpan="3" className="py-16 text-center text-surface-400">Không có yêu cầu nào đang chờ</td></tr>
                  )}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* History Modal */}
      {selectedEmp && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-surface-900/40 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-xl">
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
                <div className="space-y-5">
                  {/* Progress bar */}
                  <div className="bg-surface-50 p-4 rounded-xl border border-surface-200">
                    <div className="flex justify-between items-center mb-3">
                      <div>
                        <p className="text-xs text-surface-500 mb-0.5">Tiến độ kết nối</p>
                        <p className="font-bold text-xl text-surface-800">
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
                    <div className="bg-surface-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all ${historyData.progress.has_won ? 'bg-success-500' : historyData.progress.is_expired ? 'bg-danger-400' : 'bg-primary-500'}`}
                        style={{ width: `${Math.min(100, Math.round(historyData.progress.current / historyData.progress.target * 100))}%` }}
                      />
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
                      <div className="space-y-2">
                        {historyData.history.map(h => (
                          <div key={h.connection_id} className="flex items-center justify-between p-3 border border-surface-200 rounded-xl hover:bg-surface-50 transition-colors">
                            <div className="flex items-center gap-3">
                              <img src={h.other_person.photo || `https://i.pravatar.cc/150?u=${h.other_person.emp_code}`} className="w-9 h-9 rounded-full object-cover border border-surface-200" alt="" />
                              <div>
                                <p className="font-semibold text-surface-800 text-sm">{h.other_person.full_name}</p>
                                <p className="text-xs text-surface-500 mt-0.5">{h.other_person.department} • {h.direction === 'sent' ? '↗ Đã gửi' : '↙ Nhận'}</p>
                              </div>
                            </div>
                            <div className="text-right shrink-0">
                              {h.status === 'ACCEPTED' ? (
                                <span className="badge badge-success text-[10px]"><CheckCircle2 className="w-3 h-3 mr-1" />Chấp nhận</span>
                              ) : h.status === 'PENDING' ? (
                                <span className="badge badge-accent text-[10px]"><Clock className="w-3 h-3 mr-1" />Đang chờ</span>
                              ) : (
                                <span className="badge badge-danger text-[10px]"><X className="w-3 h-3 mr-1" />Từ chối</span>
                              )}
                              <p className="text-[10px] text-surface-400 mt-1">{new Date(h.created_at).toLocaleString('vi-VN')}</p>
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
