import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { Search, Users, CheckCircle2, Clock, Filter, X, Building2, ChevronDown, ChevronRight, UserPlus, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../services/api';
import { getAvatarUrl } from '../utils/avatar';

const PAGE_SIZE = 1000;

const CONN_STATUS = {
  ACCEPTED: { label: 'Đã kết nối', cls: 'badge-success', icon: <CheckCircle2 className="w-3.5 h-3.5" /> },
  PENDING:  { label: 'Đang chờ',   cls: 'badge-accent',  icon: <Clock className="w-3.5 h-3.5" /> },
  REJECTED: { label: 'Đã từ chối', cls: 'badge-danger',  icon: <X className="w-3.5 h-3.5" /> },
  none:     { label: 'Kết nối',    cls: '',               icon: null },
};

export default function SearchPage() {
  const [employees, setEmployees] = useState([]);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [skip, setSkip] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [filterOpts, setFilterOpts] = useState({ entities:[], divisions:[], departments:[], teams:[], parts:[], positions:[], roles:[] });
  const [showFilters, setShowFilters] = useState(false);
  const [collapsedDepts, setCollapsedDepts] = useState({});
  const location = useLocation();

  const [searchTerm, setSearchTerm] = useState('');
  const [filterEntity, setFilterEntity] = useState('');
  const [filterDiv, setFilterDiv] = useState('');
  const [filterDept, setFilterDept] = useState('');
  const [filterTeam, setFilterTeam] = useState('');
  const [filterPart, setFilterPart] = useState('');
  const [filterPos, setFilterPos] = useState('');

  // Build params object from current filters
  const buildParams = useCallback((skipVal = 0) => {
    const params = { skip: skipVal, limit: PAGE_SIZE };
    if (searchTerm)   params.name = searchTerm;
    if (filterEntity) params.entity = filterEntity;
    if (filterDiv)    params.division = filterDiv;
    if (filterDept)   params.department = filterDept;
    if (filterTeam)   params.team = filterTeam;
    if (filterPart)   params.part = filterPart;
    if (filterPos)    params.position = filterPos;
    return params;
  }, [searchTerm, filterEntity, filterDiv, filterDept, filterTeam, filterPart, filterPos]);

  useEffect(() => {
    api.get('/connectors/filters').then(r => setFilterOpts(r.data)).catch(() => {});
  }, []);

  // Reset and fetch fresh when filters change
  const fetchConnectors = useCallback(async (silent = false) => {
    if (!silent) {
      setLoading(true);
      setSkip(0);
    }
    try {
      const res = await api.get('/connectors/search', { params: buildParams(0) });
      const data = res.data;
      setEmployees(data.items || []);
      setTotal(data.total || 0);
      setHasMore(data.has_more || false);
      if (!silent) setSkip(PAGE_SIZE);
    } catch {
      if (!silent) toast.error('Không thể tải danh sách nhân sự');
    } finally {
      if (!silent) setLoading(false);
    }
  }, [buildParams]);

  // Load more (append)
  const loadMore = async () => {
    if (loadingMore || !hasMore) return;
    setLoadingMore(true);
    try {
      const res = await api.get('/connectors/search', { params: buildParams(skip) });
      const data = res.data;
      setEmployees(prev => [...prev, ...(data.items || [])]);
      setHasMore(data.has_more || false);
      setSkip(s => s + PAGE_SIZE);
    } catch {
      toast.error('Không thể tải thêm');
    } finally {
      setLoadingMore(false);
    }
  };

  // Refetch on location change
  useEffect(() => { fetchConnectors(false); }, [location.key, fetchConnectors]);

  // Refetch on filter/search change (debounced)
  useEffect(() => {
    const t = setTimeout(() => fetchConnectors(false), 300);
    return () => clearTimeout(t);
  }, [searchTerm, filterEntity, filterDiv, filterDept, filterTeam, filterPart, filterPos, fetchConnectors]);

  // Auto-refresh connection statuses every 10s (without resetting pagination)
  useEffect(() => {
    const interval = setInterval(() => fetchConnectors(true), 10000);
    return () => clearInterval(interval);
  }, [fetchConnectors]);

  const handleInvite = async (emp) => {
    try {
      await api.post('/connections/invite', { connector_id: emp.id });
      setEmployees(prev => prev.map(e => e.id === emp.id ? { ...e, conn_status: 'PENDING' } : e));
      toast.success(`Đã gửi yêu cầu kết nối đến ${emp.full_name}!`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Gửi yêu cầu thất bại');
    }
  };

  const hasFilter = filterEntity || filterDiv || filterDept || filterTeam || filterPart || filterPos;
  const clearFilters = () => { setFilterEntity(''); setFilterDiv(''); setFilterDept(''); setFilterTeam(''); setFilterPart(''); setFilterPos(''); };

  const toggleDept = (dept) => {
    setCollapsedDepts(prev => ({ ...prev, [dept]: !prev[dept] }));
  };

  const normalizeDeptGroup = (deptStr) => {
    if (!deptStr) return 'Chưa phân phòng';
    const s = deptStr.trim().toUpperCase();
    
    const prodWords = [
      'AS/AT/PA/COAT', 'TECHNICIAN', 'BORING', 'TURNING', 'COATING', 
      'ASEEMBLY', 'ASSEMBLY', 'TEAM LEADER', 'PACKING', 'AFTERTREATMENT', 
      'IH-GEAR', 'MACHINING', 'GEAR', 'IH', 'DRILLING',
      'ENGINEERING & MANAGEMENT', 'SCHEDULING'
    ];
    if (prodWords.some(w => s.includes(w))) return 'Production';
    if (/\bGC\b/.test(s)) return 'Production';
    if (/\bMI\b/.test(s)) return 'IT';
    if (s.includes('ACCOUNT')) return 'Finance';
    
    return deptStr;
  };

  // Group employees by department
  const grouped = {};
  employees.forEach(emp => {
    let rawDept = emp.part || emp.department || 'Chưa phân phòng';
    const dept = normalizeDeptGroup(rawDept);
    
    if (!grouped[dept]) grouped[dept] = [];
    grouped[dept].push(emp);
  });
  const sortedDepts = Object.keys(grouped).sort((a, b) => {
    if (a === 'Chưa phân phòng') return 1;
    if (b === 'Chưa phân phòng') return -1;
    return grouped[b].length - grouped[a].length;
  });

  const totalConnected = employees.filter(e => e.conn_status === 'ACCEPTED').length;
  const totalPending = employees.filter(e => e.conn_status === 'PENDING').length;

  const SelectFilter = ({ value, onChange, options, placeholder }) => (
    <select value={value} onChange={e => onChange(e.target.value)}
      className="input-field py-2.5 text-sm appearance-none cursor-pointer pr-8 bg-white">
      <option value="">{placeholder}</option>
      {options.map(o => <option key={o} value={o}>{o}</option>)}
    </select>
  );

  const DEPT_COLORS = [
    'bg-blue-500', 'bg-emerald-500', 'bg-amber-500', 'bg-purple-500',
    'bg-rose-500', 'bg-teal-500', 'bg-indigo-500', 'bg-orange-500',
    'bg-cyan-500', 'bg-pink-500', 'bg-lime-500', 'bg-violet-500',
  ];

  return (
    <div className="animate-fade-in space-y-5 pb-8">
      {/* Header */}
      <div className="card p-5 md:p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-heading font-bold text-surface-800 flex items-center gap-2">
            <Users className="w-6 h-6 text-primary-500" />
            Tìm kiếm đồng nghiệp
          </h2>
          <button onClick={() => setShowFilters(v => !v)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${showFilters || hasFilter ? 'bg-primary-600 text-white' : 'bg-surface-100 text-surface-600 hover:bg-surface-200'}`}>
            <Filter className="w-4 h-4" />
            Bộ lọc {hasFilter && <span className="bg-white/20 text-xs px-1.5 py-0.5 rounded-md">ON</span>}
          </button>
        </div>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3.5 top-3.5 h-5 w-5 text-surface-400" />
          <input type="text" placeholder="Tìm theo tên nhân viên..."
            value={searchTerm} onChange={e => setSearchTerm(e.target.value)}
            className="input-field pl-11 text-base"
          />
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="bg-surface-50 rounded-xl p-4 space-y-3 animate-slide-down border border-surface-200">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <SelectFilter value={filterEntity} onChange={setFilterEntity} options={filterOpts.entities} placeholder="Tất cả công ty" />
              <SelectFilter value={filterDiv} onChange={setFilterDiv} options={filterOpts.divisions} placeholder="Tất cả khối" />
              <SelectFilter value={filterDept} onChange={setFilterDept} options={filterOpts.departments} placeholder="Tất cả phòng ban" />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <SelectFilter value={filterTeam} onChange={setFilterTeam} options={filterOpts.teams} placeholder="Tất cả nhóm" />
              <SelectFilter value={filterPart} onChange={setFilterPart} options={filterOpts.parts} placeholder="Tất cả tổ" />
              <SelectFilter value={filterPos} onChange={setFilterPos} options={filterOpts.positions} placeholder="Tất cả chức danh" />
            </div>
            {hasFilter && (
              <button onClick={clearFilters} className="text-sm text-danger-500 hover:text-danger-600 flex items-center gap-1 font-medium">
                <X className="w-4 h-4" /> Xóa bộ lọc
              </button>
            )}
          </div>
        )}

        {/* Summary */}
        {!loading && (
          <div className="flex flex-wrap items-center gap-4 text-sm mt-3">
            <span className="text-surface-500">
              Hiển thị: <strong className="text-surface-800">{employees.length}</strong>
              {total > 0 && <span className="text-surface-400"> / {total} người</span>}
            </span>
            <span className="text-surface-300">|</span>
            <span className="text-success-600 flex items-center gap-1"><CheckCircle2 className="w-4 h-4" /> Đã kết nối: <strong>{totalConnected}</strong></span>
            <span className="text-surface-300">|</span>
            <span className="text-accent-600 flex items-center gap-1"><Clock className="w-4 h-4" /> Đang chờ: <strong>{totalPending}</strong></span>
          </div>
        )}
      </div>

      {/* Results grouped by department */}
      {loading && employees.length === 0 ? (
        <div className="py-20 flex justify-center">
          <div className="w-10 h-10 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
        </div>
      ) : sortedDepts.length > 0 ? (
        <div className="space-y-4">
          {sortedDepts.map((dept, deptIdx) => {
            const emps = grouped[dept];
            const isCollapsed = collapsedDepts[dept];
            const colorClass = DEPT_COLORS[deptIdx % DEPT_COLORS.length];
            const connectedInDept = emps.filter(e => e.conn_status === 'ACCEPTED').length;

            return (
              <div key={dept} className="card overflow-hidden animate-slide-up" style={{ animationDelay: `${deptIdx * 50}ms` }}>
                {/* Department header */}
                <button onClick={() => toggleDept(dept)}
                  className="w-full flex items-center gap-3 px-5 py-4 hover:bg-surface-50 transition-colors text-left">
                  <div className={`w-10 h-10 ${colorClass} rounded-xl flex items-center justify-center flex-shrink-0`}>
                    <Building2 className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-heading font-bold text-surface-800 truncate">{dept}</h3>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className="text-sm text-surface-500">{emps.length} nhân viên</span>
                      {connectedInDept > 0 && (
                        <span className="badge badge-success text-[11px]">
                          <CheckCircle2 className="w-3 h-3 mr-1" />{connectedInDept} đã kết nối
                        </span>
                      )}
                    </div>
                  </div>
                  {isCollapsed ? <ChevronRight className="w-5 h-5 text-surface-400" /> : <ChevronDown className="w-5 h-5 text-surface-400" />}
                </button>

                {/* Employee list */}
                {!isCollapsed && (
                  <div className="border-t border-surface-100">
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-0 divide-y sm:divide-y-0 divide-surface-100">
                      {emps.map(emp => {
                        const cs = emp.conn_status || 'none';
                        const statusConf = CONN_STATUS[cs] || CONN_STATUS.none;
                        return (
                          <div key={emp.id} className="flex items-center gap-3 p-4 hover:bg-surface-50 transition-colors sm:border-r sm:border-b border-surface-100 last:border-r-0">
                            <img src={getAvatarUrl(emp.photo, emp.full_name)}
                              className="w-11 h-11 rounded-full object-cover border-2 border-surface-200 flex-shrink-0" alt="" />
                            <div className="flex-1 min-w-0">
                              <h4 className="font-semibold text-surface-800 text-sm truncate">{emp.full_name}</h4>
                              <p className="text-xs text-surface-400 mt-0.5">{emp.emp_code}</p>
                              {(emp.position || emp.role) && (
                                <span className="badge badge-neutral text-[10px] mt-1">{emp.position || emp.role}</span>
                              )}
                            </div>
                            <div className="flex-shrink-0">
                              {cs === 'ACCEPTED' ? (
                                <span className="badge badge-success text-[11px] gap-1">{statusConf.icon} Đã kết nối</span>
                              ) : cs === 'PENDING' ? (
                                <span className="badge badge-accent text-[11px] gap-1">{statusConf.icon} Đang chờ</span>
                              ) : cs === 'REJECTED' ? (
                                <span className="badge badge-danger text-[11px] gap-1">Đã từ chối</span>
                              ) : (
                                <button onClick={() => handleInvite(emp)}
                                  className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1">
                                  <UserPlus className="w-3.5 h-3.5" /> Kết nối
                                </button>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            );
          })}

          {/* Load More Button */}
          {hasMore && (
            <div className="flex flex-col items-center gap-2 py-4">
              <p className="text-sm text-surface-400">
                Đang hiển thị <strong className="text-surface-600">{employees.length}</strong> / <strong className="text-surface-600">{total}</strong> nhân viên
              </p>
              <button
                onClick={loadMore}
                disabled={loadingMore}
                className="flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-all shadow-sm hover:shadow-md"
              >
                {loadingMore ? (
                  <><Loader2 className="w-4 h-4 animate-spin" /> Đang tải...</>
                ) : (
                  <><Users className="w-4 h-4" /> Tải thêm {Math.min(PAGE_SIZE, total - employees.length)} người</>
                )}
              </button>
            </div>
          )}

          {/* All loaded indicator */}
          {!hasMore && total > PAGE_SIZE && (
            <div className="text-center py-3 text-sm text-surface-400">
              ✅ Đã hiển thị tất cả <strong>{total}</strong> nhân viên
            </div>
          )}
        </div>
      ) : (
        <div className="card py-20 text-center">
          <Users className="w-14 h-14 text-surface-300 mx-auto mb-4" />
          <p className="text-surface-500 text-lg font-medium">Không tìm thấy nhân viên</p>
          {hasFilter && <button onClick={clearFilters} className="mt-3 btn-secondary text-sm">Xóa bộ lọc</button>}
        </div>
      )}
    </div>
  );
}
