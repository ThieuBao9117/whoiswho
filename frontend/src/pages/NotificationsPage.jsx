import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Bell, Users, Award, CheckCircle2, X, Clock, Calendar, Building2, Briefcase,
  Search, Heart, Sparkles, PartyPopper, UserPlus, HandshakeIcon, Star,
  CircleDot, Smile, Coffee
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../services/api';
import { getAvatarUrl } from '../utils/avatar';

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
      toast.success(accept ? '🎉 Kết nối thành công! Chúc mừng bạn đã có thêm đồng nghiệp mới!' : 'Đã từ chối yêu cầu');
      fetchPending();
    } catch { toast.error('Thao tác thất bại'); }
  };

  const filteredReceived = received.filter(c => {
    if (filterDept && c.new_hire?.department !== filterDept) return false;
    if (filterRole && c.new_hire?.role !== filterRole) return false;
    return true;
  });

  // Group by team/department for stats tab
  const byTeam = filteredReceived.reduce((acc, c) => {
    const key = c.new_hire?.department || 'Chưa phân phòng';
    if (!acc[key]) acc[key] = [];
    acc[key].push(c);
    return acc;
  }, {});

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

      {/* ===== PENDING ===== */}
      {tab === 'pending' && (
        <div className="card p-5 md:p-6">
          {/* Header thân thiện */}
          <div className="flex items-center gap-3 mb-5">
            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-accent-100 flex items-center justify-center">
                <Bell className="h-5 w-5 text-accent-500" />
              </div>
              {pending.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-accent-500 text-white text-[10px] font-bold w-5 h-5 flex items-center justify-center rounded-full animate-pulse">
                  {pending.length}
                </span>
              )}
            </div>
            <div>
              <h2 className="text-lg font-heading font-bold text-surface-800">Yêu cầu kết nối đến bạn</h2>
              <p className="text-sm text-surface-400 flex items-center gap-1">
                <Heart className="h-3.5 w-3.5 text-accent-400" />
                {pending.length > 0
                  ? `Đang có ${pending.length} kết nối chờ bạn nè 💌`
                  : 'Tất cả yêu cầu đã được xử lý rồi 😊'}
              </p>
            </div>
          </div>

          {loadingPending ? <Loader /> : pending.length === 0 ? (
            <div className="py-14 text-center">
              {/* Empty state thân thiện */}
              <div className="relative inline-block mb-4">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-100 to-accent-100 flex items-center justify-center mx-auto">
                  <Coffee className="h-10 w-10 text-primary-400" />
                </div>
                <Smile className="h-7 w-7 text-accent-400 absolute -bottom-1 -right-1 bg-white rounded-full p-0.5" />
              </div>
              <p className="text-surface-600 font-semibold text-base">Kết nối mới đang chờ bạn nè...</p>
              <p className="text-surface-400 text-sm mt-1.5">
                Không có yêu cầu nào — Tất cả yêu cầu đã được xử lý ✅
              </p>
              <Link to="/search" className="inline-flex items-center gap-2 mt-5 btn-primary text-sm px-5 py-2.5">
                <Search className="w-4 h-4" />
                Tìm đồng nghiệp để kết nối
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {pending.map(c => (
                <div key={c.id}
                  className="flex items-center gap-3 p-4 bg-gradient-to-r from-accent-50 to-primary-50 rounded-2xl border border-accent-100 hover:border-accent-200 transition-all shadow-sm">
                  {/* Avatar với ring động */}
                  <div className="relative flex-shrink-0">
                    <div className="w-14 h-14 rounded-full ring-2 ring-accent-300 ring-offset-1 overflow-hidden flex items-center justify-center">
                      <img
                        src={getAvatarUrl(c.new_hire?.photo, c.new_hire?.full_name)}
                        className="w-12 h-12 rounded-full object-cover" alt=""
                      />
                    </div>
                    <span className="absolute -bottom-0.5 -right-0.5 text-sm leading-none">👋</span>
                  </div>

                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-surface-800 truncate">{c.new_hire?.full_name}</p>
                    <div className="flex items-center gap-2 flex-wrap mt-0.5">
                      <span className="text-xs text-surface-400">{c.new_hire?.emp_code}</span>
                      {c.new_hire?.department && <span className="badge badge-primary text-[10px]">{c.new_hire.department}</span>}
                      {c.new_hire?.role && <span className="badge badge-neutral text-[10px]">{c.new_hire.role}</span>}
                    </div>
                    <p className="text-[11px] text-surface-400 mt-1 flex items-center gap-1">
                      <Clock className="h-3 w-3" /> Gửi lúc: {formatDate(c.created_at)}
                    </p>
                  </div>

                  <div className="flex flex-col gap-2 flex-shrink-0">
                    {/* Nút Đồng ý kết nối */}
                    <button
                      onClick={() => handleAction(c.id, true)}
                      className="flex items-center gap-1.5 px-3 py-2 bg-gradient-to-r from-primary-500 to-accent-500 text-white text-xs font-bold rounded-xl shadow-sm hover:shadow-md hover:scale-105 transition-all whitespace-nowrap">
                      <Heart className="h-3.5 w-3.5" />
                      Bạn đồng ý kết nối cùng nhau nhe
                    </button>
                    <button
                      onClick={() => handleAction(c.id, false)}
                      className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-medium text-surface-400 hover:text-danger-500 hover:bg-danger-50 rounded-xl transition-colors border border-surface-200">
                      <X className="h-3.5 w-3.5" /> Từ chối
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ===== ALL CONNECTIONS ===== */}
      {tab === 'all' && (
        <div className="card p-5 md:p-6">
          {/* Header vui */}
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
              <PartyPopper className="h-5 w-5 text-primary-500" />
            </div>
            <div>
              <h2 className="text-lg font-heading font-bold text-surface-800">Vòng tròn kết nối của bạn 🎉</h2>
              <p className="text-sm text-surface-400">
                Chúc mừng bạn đã có <strong className="text-primary-600">{allConnections.length}</strong> kết nối trong đại gia đình CS Bearing!
              </p>
            </div>
          </div>

          {loadingAll ? <Loader /> : allConnections.length === 0 ? (
              <div className="py-14 text-center">
              <div className="relative inline-block mb-4">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-100 to-accent-100 flex items-center justify-center mx-auto">
                  <Users className="h-10 w-10 text-primary-400" />
                </div>
                <Sparkles className="h-7 w-7 text-yellow-400 absolute -bottom-1 -right-1 bg-white rounded-full p-0.5" />
              </div>
              <p className="text-surface-600 font-bold text-base">Đại gia đình CS Bearing chờ kết nối cùng bạn ở đây nhe! 🌟</p>
              <p className="text-surface-400 text-sm mt-1.5">Hãy bắt đầu hành trình kết nối của bạn ngay hôm nay</p>
              <Link to="/search" className="btn-primary text-sm mt-5 inline-flex items-center gap-2 px-5 py-2.5">
                <Search className="w-4 h-4" /> Tìm đồng nghiệp ngay
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {allConnections.map((c, idx) => (
                <div key={c.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-surface-50 transition-colors">
                  <span className="text-xs font-bold text-surface-300 w-6 text-center">{idx + 1}</span>
                  <div className="relative">
                    <img src={getAvatarUrl(c.other_user?.photo, c.other_user?.full_name)}
                      className="w-10 h-10 rounded-full object-cover border-2 border-primary-100 flex-shrink-0" alt="" />
                    {c.status === 'ACCEPTED' && (
                      <CheckCircle2 className="h-4 w-4 text-success-500 absolute -bottom-0.5 -right-0.5 bg-white rounded-full" />
                    )}
                  </div>
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
                      {c.status === 'ACCEPTED' ? '✓ Đã kết nối' : c.status === 'PENDING' ? '⏳ Đang chờ' : '✗ Từ chối'}
                    </span>
                    <p className="text-[10px] text-surface-400 mt-1">{formatDate(c.responded_at || c.created_at)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ===== THỐNG KÊ (theo team) ===== */}
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
            <div className="card p-5 flex items-center justify-between bg-gradient-to-r from-primary-50 to-accent-50">
              <div>
                <p className="text-sm text-surface-500">Tổng lượt kết nối nhận được{filterMonth ? ` (${filterMonth})` : ''}</p>
                <p className="text-3xl font-heading font-bold text-primary-600 mt-1">{filteredReceived.length} <span className="text-base text-surface-400 font-normal">lượt</span></p>
              </div>
              <div className="w-14 h-14 rounded-2xl bg-primary-100 flex items-center justify-center">
                <Star className="h-7 w-7 text-primary-500" />
              </div>
            </div>
          )}

          {/* Theo team */}
          {!loadingReceived && filteredReceived.length > 0 && (
            <div className="card p-5">
              <h3 className="text-base font-bold text-surface-700 mb-4 flex items-center gap-2">
                <Building2 className="h-4 w-4 text-primary-500" />
                Thể hiện đây để chỉ team
              </h3>
              <div className="space-y-3">
                {Object.entries(byTeam)
                  .sort((a, b) => b[1].length - a[1].length)
                  .map(([dept, conns]) => (
                    <div key={dept} className="flex items-center gap-3">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium text-surface-700">{dept}</span>
                          <span className="text-xs font-bold text-primary-600">{conns.length} kết nối</span>
                        </div>
                        <div className="h-2 bg-surface-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-primary-500 to-accent-400 rounded-full transition-all duration-700"
                            style={{ width: `${(conns.length / filteredReceived.length) * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Danh sách */}
          <div className="card p-5 md:p-6">
            <h2 className="text-lg font-heading font-bold text-surface-800 mb-5 flex items-center gap-2">
              <Award className="h-5 w-5 text-success-500" /> Người đã kết nối với bạn
            </h2>
            {loadingReceived ? <Loader /> : filteredReceived.length === 0 ? (
              <div className="py-12 text-center">
                <div className="w-16 h-16 rounded-full bg-success-50 flex items-center justify-center mx-auto mb-3">
                  <Award className="h-8 w-8 text-success-300" />
                </div>
                <p className="text-surface-500 font-medium">Chưa có ai kết nối</p>
                <p className="text-surface-400 text-sm mt-1">Hãy chia sẻ QR code để mọi người kết nối với bạn nhé!</p>
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
                      <span className="badge badge-success text-[10px]">✓ Đã kết nối</span>
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
