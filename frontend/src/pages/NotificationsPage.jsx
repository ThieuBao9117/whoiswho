import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bell, Users, Award, CheckCircle2, X, Clock, Calendar, Building2, Briefcase, Search } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../services/api';

export default function NotificationsPage({ onNotifCountChange }) {
  const [tab, setTab] = useState('pending');
  const [pending, setPending] = useState([]);
  const [received, setReceived] = useState([]);
  const [allConnections, setAllConnections] = useState([]);
  const [loadingPending, setLoadingPending] = useState(true);
  const [loadingReceived, setLoadingReceived] = useState(true);
  const [loadingAll, setLoadingAll] = useState(true);
  const [filterMonth, setFilterMonth] = useState('');
  const [filterDept, setFilterDept] = useState('');
  const [filterRole, setFilterRole] = useState('');

  const fetchPending = async () => {
    setLoadingPending(true);
    try { const res = await api.get('/connections/incoming'); setPending(res.data); if (onNotifCountChange) onNotifCountChange(res.data.length); }
    catch {} finally { setLoadingPending(false); }
  };
  const fetchReceived = async () => {
    setLoadingReceived(true);
    try { const params = {}; if (filterMonth) params.month = filterMonth; const res = await api.get('/connections/received', { params }); setReceived(res.data); }
    catch {} finally { setLoadingReceived(false); }
  };
  const fetchAll = async () => {
    setLoadingAll(true);
    try { const res = await api.get('/connections/all'); setAllConnections(res.data); }
    catch {} finally { setLoadingAll(false); }
  };

  useEffect(() => { fetchPending(); }, []);
  useEffect(() => { if (tab === 'received') fetchReceived(); }, [tab, filterMonth]);
  useEffect(() => { if (tab === 'all') fetchAll(); }, [tab]);

  const handleAction = async (id, accept) => {
    try {
      await api.put(`/connections/${id}?accept=${accept}`);
      toast.success(accept ? 'Đã chấp nhận kết nối!' : 'Đã từ chối');
      fetchPending();
    } catch { toast.error('Thao tác thất bại'); }
  };

  const filteredReceived = received.filter(c => {
    if (filterDept && c.new_hire?.department !== filterDept) return false;
    if (filterRole && c.new_hire?.role !== filterRole) return false;
    return true;
  });

  const depts = [...new Set(received.map(c => c.new_hire?.department).filter(Boolean))];
  const roles = [...new Set(received.map(c => c.new_hire?.role).filter(Boolean))];

  const formatDate = (iso) => {
    if (!iso) return '--';
    const d = new Date(iso);
    return `${d.getDate().toString().padStart(2,'0')}/${(d.getMonth()+1).toString().padStart(2,'0')}/${d.getFullYear()}`;
  };

  const tabBtn = (key, label, icon, count, color) => (
    <button onClick={() => setTab(key)}
      className={`flex-1 py-3 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-1.5 ${tab === key ? `${color} text-white shadow-md` : 'text-surface-500 hover:bg-surface-100'}`}>
      {icon} {label}
      {count > 0 && <span className={`text-[10px] px-1.5 py-0.5 rounded-md ${tab === key ? 'bg-white/20' : 'bg-surface-200'}`}>{count}</span>}
    </button>
  );

  const Loader = () => <div className="py-16 flex justify-center"><div className="w-10 h-10 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div>;

  return (
    <div className="animate-fade-in space-y-5 pb-8">
      {/* Tabs */}
      <div className="card p-2 flex gap-2">
        {tabBtn('pending', 'Chờ duyệt', <Bell className="h-4 w-4" />, pending.length, 'bg-accent-500')}
        {tabBtn('all', 'Đã kết nối', <Users className="h-4 w-4" />, allConnections.length, 'bg-primary-600')}
        {tabBtn('received', 'Thống kê', <Award className="h-4 w-4" />, 0, 'bg-success-600')}
      </div>

      {/* PENDING */}
      {tab === 'pending' && (
        <div className="card p-5 md:p-6">
          <h2 className="text-lg font-heading font-bold text-surface-800 mb-5 flex items-center gap-2">
            <Bell className="h-5 w-5 text-accent-500" /> Yêu cầu kết nối đến bạn
          </h2>
          {loadingPending ? <Loader /> : pending.length === 0 ? (
            <div className="py-16 text-center">
              <CheckCircle2 className="h-12 w-12 text-surface-300 mx-auto mb-3" />
              <p className="text-surface-500 font-medium">Không có yêu cầu nào</p>
              <p className="text-surface-400 text-sm mt-1">Tất cả yêu cầu đã được xử lý</p>
            </div>
          ) : (
            <div className="space-y-3">
              {pending.map(c => (
                <div key={c.id} className="flex items-center gap-3 p-4 bg-surface-50 rounded-xl hover:bg-surface-100 transition-colors">
                  <img src={c.new_hire?.photo || `https://i.pravatar.cc/150?u=${c.new_hire?.emp_code}`}
                    className="w-12 h-12 rounded-full object-cover border-2 border-accent-200 flex-shrink-0" alt="" />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-surface-800 truncate">{c.new_hire?.full_name}</p>
                    <div className="flex items-center gap-2 flex-wrap mt-0.5">
                      <span className="text-xs text-surface-400">{c.new_hire?.emp_code}</span>
                      {c.new_hire?.department && <span className="badge badge-primary text-[10px]">{c.new_hire.department}</span>}
                    </div>
                    <p className="text-[11px] text-surface-400 mt-1">Gửi lúc: {formatDate(c.created_at)}</p>
                  </div>
                  <div className="flex gap-2 flex-shrink-0">
                    <button onClick={() => handleAction(c.id, false)} className="btn-danger text-xs px-3 py-1.5">Từ chối</button>
                    <button onClick={() => handleAction(c.id, true)} className="btn-success text-xs px-3 py-1.5">Chấp nhận</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ALL CONNECTIONS */}
      {tab === 'all' && (
        <div className="card p-5 md:p-6">
          <h2 className="text-lg font-heading font-bold text-surface-800 mb-5 flex items-center gap-2">
            <Users className="h-5 w-5 text-primary-500" /> Danh sách kết nối
          </h2>
          {loadingAll ? <Loader /> : allConnections.length === 0 ? (
            <div className="py-16 text-center">
              <Users className="h-12 w-12 text-surface-300 mx-auto mb-3" />
              <p className="text-surface-500 font-medium">Chưa có kết nối nào</p>
              <Link to="/search" className="btn-primary text-sm mt-4 inline-flex items-center gap-2">
                <Search className="w-4 h-4" /> Tìm đồng nghiệp
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {allConnections.map((c, idx) => (
                <div key={c.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-surface-50 transition-colors">
                  <span className="text-xs font-bold text-surface-300 w-6 text-center">{idx + 1}</span>
                  <img src={c.other_user?.photo || `https://i.pravatar.cc/150?u=${c.other_user?.emp_code}`}
                    className="w-10 h-10 rounded-full object-cover border border-surface-200 flex-shrink-0" alt="" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-surface-800 text-sm truncate">{c.other_user?.full_name}</p>
                    <div className="flex items-center gap-2 flex-wrap mt-0.5">
                      <span className="text-[11px] text-surface-400">{c.other_user?.emp_code}</span>
                      {c.other_user?.department && <span className="badge badge-primary text-[10px]">{c.other_user.department}</span>}
                      {c.other_user?.role && <span className="badge badge-neutral text-[10px]">{c.other_user.role}</span>}
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className={`badge text-[10px] ${c.status === 'ACCEPTED' ? 'badge-success' : c.status === 'PENDING' ? 'badge-accent' : 'badge-danger'}`}>
                      {c.status === 'ACCEPTED' ? 'Đã kết nối' : c.status === 'PENDING' ? 'Đang chờ' : 'Từ chối'}
                    </span>
                    <p className="text-[10px] text-surface-400 mt-1">{formatDate(c.responded_at || c.created_at)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* RECEIVED / STATS */}
      {tab === 'received' && (
        <div className="space-y-5">
          {/* Filters */}
          <div className="card p-4 flex flex-col sm:flex-row gap-3">
            <div className="flex items-center gap-2 flex-1">
              <Calendar className="h-4 w-4 text-surface-400 flex-shrink-0" />
              <input type="month" value={filterMonth} onChange={e => setFilterMonth(e.target.value)}
                className="input-field py-2.5 text-sm" />
            </div>
            <div className="flex items-center gap-2 flex-1">
              <Building2 className="h-4 w-4 text-surface-400 flex-shrink-0" />
              <select value={filterDept} onChange={e => setFilterDept(e.target.value)} className="input-field py-2.5 text-sm">
                <option value="">Tất cả phòng ban</option>
                {depts.map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
            <div className="flex items-center gap-2 flex-1">
              <Briefcase className="h-4 w-4 text-surface-400 flex-shrink-0" />
              <select value={filterRole} onChange={e => setFilterRole(e.target.value)} className="input-field py-2.5 text-sm">
                <option value="">Tất cả chức danh</option>
                {roles.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            {(filterMonth || filterDept || filterRole) && (
              <button onClick={() => { setFilterMonth(''); setFilterDept(''); setFilterRole(''); }}
                className="text-sm text-danger-500 font-medium flex items-center gap-1 px-3">
                <X className="h-3.5 w-3.5" /> Xóa
              </button>
            )}
          </div>

          {/* Summary */}
          {!loadingReceived && (
            <div className="card p-5 flex items-center justify-between">
              <div>
                <p className="text-sm text-surface-500">Tổng lượt kết nối nhận được{filterMonth ? ` (${filterMonth})` : ''}</p>
                <p className="text-3xl font-heading font-bold text-primary-600 mt-1">{filteredReceived.length} <span className="text-base text-surface-400 font-normal">lượt</span></p>
              </div>
            </div>
          )}

          {/* List */}
          <div className="card p-5 md:p-6">
            <h2 className="text-lg font-heading font-bold text-surface-800 mb-5 flex items-center gap-2">
              <Award className="h-5 w-5 text-success-500" /> Người đã kết nối với bạn
            </h2>
            {loadingReceived ? <Loader /> : filteredReceived.length === 0 ? (
              <div className="py-12 text-center">
                <Award className="h-12 w-12 text-surface-300 mx-auto mb-3" />
                <p className="text-surface-500 font-medium">Chưa có ai kết nối</p>
              </div>
            ) : (
              <div className="space-y-2">
                {filteredReceived.map((c, idx) => (
                  <div key={c.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-surface-50 transition-colors">
                    <span className="text-xs font-bold text-surface-300 w-6 text-center">{idx + 1}</span>
                    <img src={c.new_hire?.photo || `https://i.pravatar.cc/150?u=${c.new_hire?.emp_code}`}
                      className="w-10 h-10 rounded-full object-cover border border-surface-200 flex-shrink-0" alt="" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-surface-800 text-sm truncate">{c.new_hire?.full_name}</p>
                      <div className="flex items-center gap-2 flex-wrap mt-0.5">
                        <span className="text-[11px] text-surface-400">{c.new_hire?.emp_code}</span>
                        {c.new_hire?.department && <span className="badge badge-primary text-[10px]">{c.new_hire.department}</span>}
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <span className="badge badge-success text-[10px]">Đã kết nối</span>
                      <p className="text-[10px] text-surface-400 mt-1">{formatDate(c.responded_at)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
