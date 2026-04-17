import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate, useNavigate } from 'react-router-dom';
import {
  Bell, Search, Award, Users, QrCode, CheckCircle2, CircleDashed, Check,
  X, ScanLine, Camera, LayoutDashboard, Settings, UserCheck, Shield, Lock, User, PieChart, Download, Printer
} from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { BrowserMultiFormatReader } from '@zxing/browser';
import toast, { Toaster } from 'react-hot-toast';
import api from './services/api';

// ----------------------
// DATA MOCKUP
// ----------------------
const currentUser = {
  id: "EMP-2026-001",
  name: "Minh Trần",
  joinDate: "01/03/2026",
  avatar: "https://i.pravatar.cc/150?u=EMP-2026-001",
  qrPayload: JSON.stringify({ id: "EMP-2026-001", name: "Minh Trần", role: "New Hire" })
};

const mockConnectionsList = [
  { id: 1, name: "Nguyễn Văn A", dept: "Kinh doanh", role: "Staff", avatar: "https://i.pravatar.cc/150?u=EMP-001", status: "none", code: "EMP-001" },
  { id: 2, name: "Trần Thị B", dept: "Marketing", role: "TL", avatar: "https://i.pravatar.cc/150?u=EMP-002", status: "none", code: "EMP-002" },
  { id: 3, name: "Lê Văn C", dept: "Kỹ thuật", role: "Operator", avatar: "https://i.pravatar.cc/150?u=EMP-003", status: "none", code: "EMP-003" },
];

const mockLeaderboard = [
  { id: 1, name: "Nguyễn Lê Quân", avatar: "https://i.pravatar.cc/150?u=EMP-Q", dept: "IT", score: 45, isTop: true },
  { id: 2, name: "Trần Anh Vũ", avatar: "https://i.pravatar.cc/150?u=EMP-V", dept: "Marketing", score: 38 },
  { id: 3, name: "Lý Hạ Thu", avatar: "https://i.pravatar.cc/150?u=EMP-T", dept: "HR", score: 32 },
  { id: 4, name: "Mai Trọng", avatar: "https://i.pravatar.cc/150?u=EMP-M", dept: "Sales", score: 25 },
  { id: 5, name: "Phạm Hà", avatar: "https://i.pravatar.cc/150?u=EMP-H", dept: "Tech", score: 20 },
  { id: 6, name: "Võ Khoa", avatar: "https://i.pravatar.cc/150?u=EMP-K", dept: "Ops", score: 15 },
  { id: 7, name: "Đào Bích", avatar: "https://i.pravatar.cc/150?u=EMP-B", dept: "Legal", score: 10 },
];

// ----------------------
// LOGIN PAGE
// ----------------------
function LoginPage({ onLogin }) {
  const [loading, setLoading] = useState(false);
  const [empId, setEmpId] = useState("EMP-2026-001");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', empId);
      formData.append('password', 'password123'); // Default password for MVP context

      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const { access_token } = response.data;
      localStorage.setItem('csb_token', access_token);

      const userRes = await api.get('/auth/me');
      const userData = userRes.data;

      // Map backend schema to frontend expectation
      const mappedUser = {
        id: userData.employee_profile?.emp_code || userData.username,
        name: userData.employee_profile?.full_name || userData.username,
        isAdmin: userData.is_staff || false,
        profile: userData.employee_profile
      };

      onLogin(mappedUser);
      navigate('/');
      toast.success(mappedUser.isAdmin ? 'Truy cập với Quyền Admin HR!' : 'Đăng nhập thành công! Chào mừng trở lại.', {
        style: { borderRadius: '16px', fontWeight: 'bold' }
      });
    } catch (err) {
      console.error(err);
      toast.error('Ghi danh thất bại. Vui lòng kiểm tra lại tài khoản.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="absolute top-0 right-0 w-72 h-72 bg-brand-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 -translate-y-1/2 translate-x-1/3"></div>
      <div className="absolute bottom-0 left-0 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 translate-y-1/3 -translate-x-1/3"></div>

      <div className="glass w-full max-w-md p-8 md:p-10 rounded-[2.5rem] relative z-10 shadow-2xl animate-fade-in border border-white/60">
        <div className="flex flex-col items-center mb-10">
          <div className="p-3 mb-6 scale-110">
            <img src="/logo.png" className="h-14 w-auto object-contain" alt="CSB Logo" />
          </div>
          <h1 className="text-3xl font-black text-gray-800 tracking-tight text-center">Connection</h1>
          <p className="text-gray-500 font-medium mt-2 text-center text-sm uppercase tracking-widest italic">Mạng lưới kết nối đội ngũ CSB</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-bold text-gray-600 block px-1">Tài khoản nhân viên</label>
            <div className="relative">
              <User className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Thêm chữ 'admin' ở tên để lấy quyền HR"
                required
                value={empId}
                onChange={(e) => setEmpId(e.target.value)}
                className="w-full pl-12 pr-4 py-3.5 rounded-2xl border border-gray-200 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/20 bg-white/50 backdrop-blur-sm outline-none transition-all text-gray-800 font-bold"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-bold text-gray-600 block px-1">Mật khẩu</label>
            <div className="relative">
              <Lock className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
              <input
                type="password"
                placeholder="••••••••"
                required
                defaultValue="password123"
                className="w-full pl-12 pr-4 py-3.5 rounded-2xl border border-gray-200 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/20 bg-white/50 backdrop-blur-sm outline-none transition-all font-bold tracking-widest text-gray-800"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-black py-4 rounded-2xl shadow-[0_8px_20px_rgb(2,132,199,0.25)] hover:shadow-[0_12px_25px_rgb(2,132,199,0.35)] hover:-translate-y-1 transition-all flex justify-center items-center mt-4"
          >
            {loading ? "Đang chui vào..." : "ĐĂNG NHẬP"}
          </button>
        </form>
      </div>
    </div>
  );
}

// ----------------------
// NAVBARS
// ----------------------
function MobileBottomNav({ onLogout }) {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;
  if (location.pathname === '/tv' || location.pathname === '/login') return null;

  if (location.pathname.startsWith('/admin')) {
    return (
      <div className="fixed bottom-0 left-0 right-0 glass border-t border-brand-100 z-50 md:hidden pb-safe shadow-2xl">
        <div className="flex justify-around items-center p-3 animate-slide-up">
          <Link to="/admin/connections" className={`flex flex-col items-center flex-1 ${isActive('/admin/connections') ? 'text-brand-600 font-bold' : 'text-gray-400'}`}>
            <UserCheck className="h-6 w-6" />
            <span className="text-[10px] mt-1">Nối kết</span>
          </Link>
          <Link to="/tv" target="_blank" className="flex flex-col items-center flex-1 text-gray-400">
            <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center -mt-2">
              <LayoutDashboard className="h-6 w-6" />
            </div>
          </Link>
          <Link to="/admin/targets" className={`flex flex-col items-center flex-1 ${isActive('/admin/targets') ? 'text-brand-600 font-bold' : 'text-gray-400'}`}>
            <Settings className="h-6 w-6" />
            <span className="text-[10px] mt-1">Cấu hình</span>
          </Link>
          <Link to="/admin/reports" className={`flex flex-col items-center flex-1 ${isActive('/admin/reports') ? 'text-brand-600 font-bold' : 'text-gray-400'}`}>
            <PieChart className="h-6 w-6" />
            <span className="text-[10px] mt-1">Báo cáo</span>
          </Link>
          <button onClick={onLogout} className="flex flex-col items-center flex-1 text-red-400">
            <X className="h-6 w-6" />
            <span className="text-[10px] mt-1">Thoát</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 glass border-t border-brand-100 z-50 md:hidden pb-safe shadow-2xl">
      <div className="flex justify-around items-center p-3 relative h-16">
        <Link to="/" className={`flex flex-col items-center w-1/5 ${isActive('/') ? 'text-brand-600 font-bold scale-110' : 'text-gray-400'} transition-all`}>
          <Award className="h-6 w-6" />
          <span className="text-[10px] mt-1">Tiến độ</span>
        </Link>
        <Link to="/search" className={`flex flex-col items-center w-1/5 ${isActive('/search') ? 'text-brand-600 font-bold scale-110' : 'text-gray-400'} transition-all`}>
          <Search className="h-6 w-6" />
          <span className="text-[10px] mt-1">Khám phá</span>
        </Link>
        <div className="w-1/5 flex justify-center items-center relative">
          <Link to="/qr" className="absolute -top-8 group z-10 w-16 h-16 bg-brand-500 text-white rounded-full flex items-center justify-center shadow-[0_8px_20px_rgb(3,105,161,0.4)] border-4 border-white active:scale-95 transition-all">
            <ScanLine className="h-8 w-8" />
          </Link>
        </div>
        <Link to="/rewards" className={`flex flex-col items-center w-1/5 relative ${isActive('/rewards') ? 'text-brand-600 font-bold scale-110' : 'text-gray-400'} transition-all`}>
          <Bell className="h-6 w-6" />
          <span className="text-[10px] mt-1">T.báo</span>
        </Link>
        <button onClick={onLogout} className="flex flex-col items-center w-1/5 text-gray-400 cursor-pointer active:scale-95 transition-all">
          <X className="h-6 w-6 text-red-500" />
          <span className="text-[10px] mt-1 text-red-500">Thoát</span>
        </button>
      </div>
    </div>
  );
}

function DesktopNavbar({ onLogout, user }) {
  const location = useLocation();
  if (location.pathname === '/tv' || location.pathname.startsWith('/admin') || location.pathname === '/login') return null;

  return (
    <nav className="glass sticky top-0 z-50 px-6 py-4 hidden md:flex items-center justify-between shadow-sm">
      <div className="flex items-center space-x-3">
        <img src="/logo.png" className="h-10 w-auto" alt="Logo" />
        <span className="text-xl font-black text-gray-800 tracking-tighter">
          CSB-Connection
        </span>
      </div>
      <div className="flex items-center space-x-8">
        <Link to="/" className="text-gray-600 hover:text-brand-600 font-medium transition-colors">Bảng tiến độ</Link>
        <Link to="/search" className="text-gray-600 hover:text-brand-600 font-medium transition-colors">Tìm kết nối</Link>
        <Link to="/qr" className="bg-brand-50 text-brand-600 px-4 py-2 rounded-full hover:bg-brand-100 font-bold transition-colors flex items-center gap-2">
          <ScanLine className="h-4 w-4" /> Quét QR
        </Link>
        <Link to="/tv" target="_blank" className="text-gray-600 hover:text-brand-600 font-medium transition-colors">TV Board</Link>

        {user?.isAdmin && (
          <Link to="/admin/connections" className="bg-gradient-to-r from-brand-600 to-brand-400 text-white px-4 py-2 rounded-full hover:shadow-lg font-bold transition-all shadow-sm">
            Công Cụ Quản Trị HR
          </Link>
        )}

        <div className="h-8 w-px bg-gray-200"></div>

        <div className="flex items-center space-x-3 bg-white px-3 py-1.5 rounded-full border border-gray-100 shadow-sm cursor-pointer hover:shadow-md transition-shadow group relative">
          <img src={user?.profile?.photo || "https://i.pravatar.cc/150?u=EMP-001"} alt="avatar" className="h-8 w-8 rounded-full border border-gray-100 object-cover" />
          <span className="font-semibold text-gray-700 text-sm hidden lg:block">{user?.name} ▼</span>
          <div className="absolute top-full mt-2 right-0 bg-white border border-gray-100 shadow-lg rounded-xl w-32 hidden group-hover:flex flex-col overflow-hidden">
            <button onClick={onLogout} className="px-4 py-3 text-sm font-bold text-red-500 hover:bg-red-50 text-left w-full">Đăng xuất</button>
          </div>
        </div>
      </div>
    </nav>
  );
}

// ----------------------
// SEARCH PAGE
// ----------------------
function SearchPage() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeDept, setActiveDept] = useState("Mọi phòng ban");

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchConnectors();
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm, activeDept]);

  const fetchConnectors = async () => {
    setLoading(true);
    try {
      const params = {};
      if (searchTerm) params.name = searchTerm;
      if (activeDept !== "Mọi phòng ban") params.department = activeDept;

      const res = await api.get('/connectors/search', { params });
      setEmployees(res.data);
    } catch (err) {
      console.error(err);
      toast.error("Không thể tải danh sách nhân sự");
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (emp) => {
    try {
      await api.post('/connections/invite', { connector_id: emp.id });
      toast.success(`Đã gửi yêu cầu kết nối đến ${emp.full_name}!`, {
        icon: '📨',
        style: { borderRadius: '12px', background: '#f0f9ff', color: '#0369a1' }
      });
    } catch (err) {
      toast.error(err.response?.data?.detail || "Gửi yêu cầu thất bại");
    }
  };

  const departments = ["Mọi phòng ban", "Kinh doanh", "Marketing", "Kỹ thuật", "IT", "HR"];

  return (
    <div className="animate-fade-in space-y-6 pb-24 md:pb-8">
      <div className="glass rounded-3xl p-6 md:p-8">
        <h2 className="text-2xl font-black text-gray-800 mb-6 font-display uppercase tracking-tight">Kế nối đồng nghiệp CSB</h2>
        <div className="bg-gray-50/50 p-2 rounded-2xl border border-gray-100 flex flex-col md:flex-row gap-2 mb-8">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-3.5 h-5 w-5 text-brand-400" />
            <input
              type="text"
              placeholder="Gõ tên nhân viên cần tìm..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl border-none focus:ring-2 focus:ring-brand-400 bg-white shadow-sm text-gray-700 font-medium"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={activeDept}
              onChange={(e) => setActiveDept(e.target.value)}
              className="flex-1 py-3 px-4 rounded-xl border-none focus:ring-2 focus:ring-brand-400 bg-white shadow-sm font-medium"
            >
              {departments.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
        </div>

        <h3 className="font-bold text-gray-500 mb-4 px-2 tracking-wide text-sm uppercase">Kết quả tìm kiếm</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading ? (
            <div className="col-span-full py-10 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-brand-500 mx-auto"></div>
            </div>
          ) : employees.length > 0 ? (
            employees.map(user => (
              <div key={user.id} className="bg-white p-5 rounded-3xl border border-brand-50 shadow-sm hover:shadow-lg transition-all flex flex-col items-center text-center group">
                <div className="relative mb-4">
                  <img src={user.photo || `https://i.pravatar.cc/150?u=${user.id}`} className="w-20 h-20 rounded-full border-4 border-white shadow-md object-cover" alt="emp" />
                  <div className="absolute -bottom-2 right-0 bg-brand-100 text-brand-700 text-[10px] font-black px-2 py-0.5 rounded-full border-2 border-white uppercase">{user.role || 'Staff'}</div>
                </div>
                <h4 className="font-bold text-gray-900 text-lg leading-tight mb-1">{user.full_name}</h4>
                <p className="text-gray-500 text-xs font-bold uppercase tracking-tighter mb-6">{user.department}</p>

                <button onClick={() => handleInvite(user)} className="w-full py-2.5 rounded-xl bg-brand-50 text-brand-600 hover:bg-brand-600 hover:text-white font-bold transition-all shadow-sm flex items-center justify-center gap-2">
                  <Users className="w-4 h-4" /> Kết nối ngay
                </button>
              </div>
            ))
          ) : (
            <div className="col-span-full py-20 text-center">
              <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-400 font-bold">Không tìm thấy đồng nghiệp nào</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ----------------------
// QR CODE PAGE
// ----------------------
function QRCodeScanPage({ user }) {
  const [scanActive, setScanActive] = useState(false);
  const videoRef = useRef(null);

  useEffect(() => {
    let reader = null;
    if (scanActive && videoRef.current) {
      reader = new BrowserMultiFormatReader();
      reader.decodeFromVideoDevice(null, videoRef.current, async (result, err) => {
        if (result && result.text) {
          try {
            // QR Payload is usually the employee ID or JSON
            let connectorId = result.text;
            let connectorName = "đồng nghiệp";

            try {
              const data = JSON.parse(result.text);
              connectorId = data.id || data.emp_code;
              connectorName = data.name || data.full_name;
            } catch (e) { }

            await api.post('/connections/invite', { connector_id: connectorId });

            toast.success(
              <div className="flex flex-col">
                <span className="font-bold text-lg">Đã gửi yêu cầu kết nối!</span>
                <span className="text-sm">Vui lòng chờ {connectorName} duyệt yêu cầu để nhận thưởng KPI nhé.</span>
              </div>,
              { duration: 5000, style: { background: '#0284c7', color: 'white', borderRadius: '16px' } }
            );
          } catch (e) {
            console.error(e);
            toast.error(e.response?.data?.detail || "Không thể thực hiện kết nối qua QR");
          }
          setScanActive(false);
          reader.reset();
        }
      });
    }
    return () => { if (reader) reader.reset(); };
  }, [scanActive]);

  const qrValue = JSON.stringify({
    id: user?.profile?.id,
    emp_code: user?.id,
    name: user?.name
  });

  return (
    <div className="animate-fade-in max-w-md mx-auto space-y-6 pb-32">
      <div className="glass rounded-[2rem] p-8 flex flex-col items-center text-center relative overflow-hidden shadow-2xl">
        <div className="absolute top-0 w-full h-32 bg-gradient-to-br from-brand-400 to-brand-600 left-0"></div>
        <img src={user?.profile?.photo || "https://i.pravatar.cc/150?u=ME"} className="w-24 h-24 rounded-full border-4 border-white shadow-lg z-10 relative mt-4 mb-4 object-cover" alt="me" />
        <h2 className="text-2xl font-black text-gray-800 tracking-tight">{user?.name}</h2>
        <p className="text-brand-500 font-bold mb-8">{user?.id}</p>

        <div className="bg-white p-4 rounded-3xl shadow-sm border border-brand-50 mb-6">
          <QRCodeSVG value={qrValue} size={200} level="H" fgColor="#0369a1" />
        </div>
        <p className="text-sm font-medium text-gray-400 px-4 leading-relaxed">Đưa mã này cho đồng nghiệp quét hoặc quét mã của họ để tạo kết nối mới!</p>
      </div>

      <div className="glass rounded-[2rem] p-6 text-center">
        {!scanActive ? (
          <div>
            <div className="w-20 h-20 bg-brand-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-brand-100">
              <Camera className="w-10 h-10 text-brand-500" />
            </div>
            <h3 className="font-black text-xl text-gray-800 mb-2">Thêm kết nối mới</h3>
            <button
              onClick={() => setScanActive(true)}
              className="w-full bg-brand-500 hover:bg-brand-600 text-white font-bold py-4 rounded-2xl shadow-lg transition-colors flex items-center justify-center gap-2"
            >
              <ScanLine className="w-5 h-5" /> Mở Camera Quét QR
            </button>
          </div>
        ) : (
          <div className="relative">
            <div className="rounded-3xl overflow-hidden border-4 border-brand-200 shadow-inner bg-black aspect-square relative">
              <video autoPlay muted playsInline ref={videoRef} className="w-full h-full object-cover" />
              <div className="absolute inset-0 border-[40px] border-black/40 pointer-events-none"></div>
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 border-2 border-brand-400 rounded-3xl animate-pulse"></div>
            </div>
            <button
              onClick={() => setScanActive(false)}
              className="mt-6 font-bold text-gray-500 bg-gray-100 hover:bg-gray-200 px-6 py-3 rounded-xl transition-colors"
            >
              Hủy bỏ quét
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ----------------------
// NEW HIRE DASHBOARD
// ----------------------
function ProgressBar({ label, current, max, isComplete }) {
  const percentage = Math.min((current / max) * 100, 100);
  return (
    <div className="mb-5 last:mb-0">
      <div className="flex justify-between items-end mb-2">
        <span className="text-sm font-semibold text-gray-700">{label}</span>
        <span className="text-sm font-bold flex items-center gap-1">
          <span className={isComplete ? "text-brand-600" : "text-gray-600"}>{current}</span>
          <span className="text-gray-400">/ {max}</span>
        </span>
      </div>
      <div className="w-full bg-brand-50/50 rounded-full h-3 overflow-hidden border border-brand-50">
        <div className={`h-3 rounded-full ${isComplete ? 'bg-gradient-to-r from-brand-400 to-brand-500' : 'bg-gradient-to-r from-gray-300 to-gray-400'}`} style={{ width: `${percentage}%` }}></div>
      </div>
    </div>
  );
}

function Dashboard({ user }) {
  const [myConnections, setMyConnections] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [connRes, leaderRes] = await Promise.all([
          api.get('/connections/my'),
          api.get('/admin/leaderboard')
        ]);
        setMyConnections(connRes.data);
        setLeaderboard(leaderRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  const getCount = (role) => myConnections.filter(c => c.status === 'ACCEPTED' && c.connector?.role?.includes(role)).length;

  const stats = [
    { label: "Operator", current: getCount("Operator"), max: 5 },
    { label: "Leader", current: getCount("Leader"), max: 2 },
    { label: "Part Leader", current: getCount("Part Leader"), max: 1 },
    { label: "Team Manager", current: getCount("Team Manager"), max: 1 },
    { label: "Giám Đốc (GD)", current: getCount("GD"), max: 0 },
  ];

  const totalAccepted = myConnections.filter(c => c.status === 'ACCEPTED').length;
  const isEligibleForReward = totalAccepted >= 9; // MVP Logic: 5+2+1+1

  return (
    <div className="animate-fade-in space-y-6 md:space-y-8 pb-24 md:pb-8">
      {user?.isAdmin && (
        <div className="bg-gradient-to-r from-brand-600 to-blue-500 rounded-2xl p-4 text-white flex justify-between items-center shadow-lg md:hidden">
          <div>
            <h3 className="font-bold text-lg">Bạn có quyền quản trị</h3>
            <p className="text-sm opacity-90">Truy cập bộ công cụ dành cho HR</p>
          </div>
          <Link to="/admin" className="bg-white text-brand-600 font-bold px-4 py-2 rounded-xl shadow-sm text-sm">Vào Admin</Link>
        </div>
      )}
      <div className="glass rounded-3xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6 overflow-hidden relative shadow-xl">
        <div className="absolute top-0 right-0 w-64 h-64 bg-brand-100 rounded-full mix-blend-multiply filter blur-3xl opacity-50 -translate-y-1/2 translate-x-1/3"></div>
        <div className="flex items-center gap-5 z-10 w-full md:w-auto">
          <div className="relative">
            <img src={user?.profile?.photo || "https://i.pravatar.cc/150?u=EMP-2026-001"} alt="Profile" className="w-20 h-20 md:w-24 md:h-24 rounded-[2rem] border-4 border-white shadow-lg object-cover" />
            <div className="absolute -bottom-1 -right-1 bg-brand-500 text-white p-1.5 rounded-xl shadow-lg border-2 border-white">
              <CheckCircle2 className="h-4 w-4" />
            </div>
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-black text-gray-800 tracking-tight leading-tight">Xin chào, {user?.name}! 👋</h1>
            <div className="flex items-center gap-3 mt-1.5">
              <span className="bg-brand-50 text-brand-600 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider">{user?.profile?.department || "CÔNG NHÂN"}</span>
              <span className="text-gray-400 font-bold text-sm">Gia nhập: {user?.profile?.join_date || "01/03/2026"}</span>
            </div>
          </div>
        </div>

        <div className="flex gap-4 md:gap-6 z-10 w-full md:w-auto">
          <div className="bg-white/40 backdrop-blur-md p-4 md:p-5 rounded-[2rem] flex-1 md:flex-none md:min-w-[120px] text-center shadow-sm border border-white/60">
            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1 leading-none">Cần thêm</p>
            <p className="text-3xl font-black text-brand-600 tracking-tighter">{Math.max(0, 9 - totalAccepted)}</p>
          </div>
          <div className="bg-gradient-to-br from-brand-600 to-brand-500 p-4 md:p-5 rounded-[2rem] flex-1 md:flex-none md:min-w-[120px] text-center shadow-lg shadow-brand-500/20 text-white scale-105">
            <p className="text-[10px] font-black opacity-80 uppercase tracking-widest mb-1 leading-none">Thưởng nóng</p>
            <p className="text-xl font-black tracking-tight">{isEligibleForReward ? '500,000' : '0'} <span className="text-[10px]">đ</span></p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 md:gap-8">
        <div className="md:col-span-8 space-y-6">
          <div className="glass rounded-3xl p-6 md:p-8 shadow-sm border border-brand-50 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-2 h-full bg-brand-500"></div>
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-black text-gray-800 uppercase tracking-tight">Nhiệm Vụ Kỷ Lục Tháng</h2>
              <span className="bg-brand-100 text-brand-700 font-black px-4 py-2 rounded-xl text-xs border border-brand-200 shadow-sm">THÁNG 03/2026</span>
            </div>

            {loading ? (
              <div className="flex justify-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-brand-500"></div>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 gap-x-12 gap-y-6">
                {stats.map((stat, i) => (
                  <ProgressBar
                    key={i}
                    label={stat.label}
                    current={stat.current}
                    max={stat.max}
                    isComplete={stat.max > 0 && stat.current >= stat.max}
                  />
                ))}
              </div>
            )}

            <Link to="/search" className="mt-10 w-full py-4 bg-gray-50 text-gray-600 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-brand-50 hover:text-brand-600 transition-all border border-transparent hover:border-brand-100 uppercase text-sm font-display">
              <Users className="h-5 w-5" /> Kết nối thêm đồng nghiệp mới ngay
            </Link>
          </div>
        </div>

        <div className="md:col-span-4 space-y-6">
          <div className="glass rounded-[2rem] p-6 border border-gray-50">
            <h3 className="font-black text-gray-800 mb-6 flex items-center gap-2 uppercase text-xs tracking-widest">
              <LayoutDashboard className="h-5 w-5 text-brand-500" /> Bảng Vinh Danh
            </h3>
            <div className="space-y-5">
              {leaderboard.slice(0, 5).map((person, idx) => (
                <div key={person.id} className="flex items-center justify-between group">
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-black ${idx === 0 ? 'text-yellow-500 font-display text-lg' : idx === 1 ? 'text-gray-400' : 'text-gray-300'}`}>0{idx + 1}</span>
                    <img src={person.avatar} className="w-10 h-10 rounded-xl object-cover shadow-sm" alt={person.name} />
                    <div>
                      <h4 className="text-sm font-bold text-gray-700 leading-tight group-hover:text-brand-600 transition-colors">{person.name}</h4>
                      <p className="text-[10px] text-gray-400 font-bold uppercase">{person.dept}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-black text-brand-600">{person.score}</span>
                    <p className="text-[8px] text-gray-400 font-black uppercase">KPI</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-[2rem] p-6 text-white overflow-hidden relative shadow-xl">
            <div className="absolute top-0 right-0 w-32 h-32 bg-brand-500/20 rounded-full blur-3xl"></div>
            <h3 className="font-bold text-lg mb-2 relative z-10 font-display">Mẹo kết nối</h3>
            <p className="text-sm text-gray-400 relative z-10 leading-relaxed italic">Hãy chủ động quét mã QR của các <b>Sếp</b> và <b>Quản lý</b> để hoàn thiện bộ chỉ tiêu sớm nhất và nhận thưởng!</p>
            <Link to="/qr" className="mt-4 flex items-center gap-2 text-brand-400 font-black text-sm tracking-wide group relative z-10 active:scale-95 transition-all">
              THỬ NGAY <ScanLine className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------
// TV DASHBOARD
// ----------------------
function TVDashboard() {
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const res = await api.get('/admin/leaderboard');
        setLeaderboard(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchLeaderboard();
    const interval = setInterval(fetchLeaderboard, 30000); // 30s refresh
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 bg-[#061025] overflow-hidden flex flex-col animate-fade-in z-[100]">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-brand-900/30 via-[#061025] to-[#061025]"></div>
      <div className="p-8 z-10 flex justify-between items-center relative border-b border-white/5 bg-white/5 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <img src="/logo.png" className="h-16 w-auto" alt="Logo" />
          <div>
            <h1 className="text-4xl font-black text-white tracking-wider">CSB-CONNECTION</h1>
            <p className="text-brand-300 text-lg font-bold">Bảng Xếp Hạng Kết Nối Hệ Thống</p>
          </div>
        </div>
      </div>
      <div className="flex-1 relative overflow-hidden">
        {leaderboard.length > 0 ? leaderboard.map((user, index) => {
          const isTop = user.isTop;
          const topPos = isTop ? '50%' : `${15 + Math.random() * 60}%`;
          const leftPos = isTop ? '50%' : `${10 + Math.random() * 80}%`;
          return (
            <div key={user.id} className={`absolute transition-all duration-1000 origin-center -translate-x-1/2 -translate-y-1/2 ${isTop ? 'animate-pulse-glow z-50' : (index % 2 === 0 ? 'animate-float' : 'animate-float-reverse z-10')}`} style={{ top: topPos, left: leftPos }}>
              <div className={`relative rounded-full glass-dark flex flex-col items-center justify-center p-2 ${isTop ? 'w-80 h-80 border-4 border-brand-400' : 'w-40 h-40 border-2 border-brand-700/50'}`}>
                <img src={user.avatar || `https://i.pravatar.cc/150?u=${user.id}`} className={`rounded-full object-cover border-2 shadow-lg ${isTop ? 'w-32 h-32 border-brand-400 mb-4 bg-brand-900' : 'w-16 h-16 border-white/30 mb-2 bg-brand-900'}`} alt="avatar" />
                <h3 className={`font-black text-center text-white ${isTop ? 'text-2xl mb-1' : 'text-sm'}`}>{user.name}</h3>
                <div className={`bg-white/10 rounded-full flex items-center justify-center ${isTop ? 'px-6 py-2' : 'px-3 py-1'}`}>
                  <span className={`font-black text-brand-400 ${isTop ? 'text-3xl' : 'text-sm'}`}>{user.score}</span>
                  <Award className={`text-yellow-400 ml-2 ${isTop ? 'w-6 h-6' : 'w-3 h-3'}`} />
                </div>
              </div>
            </div>
          );
        }) : (
          <div className="h-full flex items-center justify-center text-white/20 text-4xl font-black uppercase tracking-widest">
            Chưa có dữ liệu kết nối
          </div>
        )}
      </div>
    </div>
  );
}

// ----------------------
// ADMIN HR PORTAL
// ----------------------
function AdminSidebar({ onLogout }) {
  return (
    <div className="bg-white w-64 border-r border-gray-100 flex-shrink-0 flex flex-col hidden md:flex z-50 shadow-xl">
      <div className="p-6 border-b border-gray-100 flex flex-col items-center gap-3">
        <img src="/logo.png" className="h-12 w-auto" alt="logo" />
        <span className="text-xl font-black text-gray-800 tracking-tighter uppercase">CSB Admin</span>
      </div>
      <div className="p-4 flex-1">
        <Link to="/admin/connections" className="flex items-center gap-3 px-4 py-3 rounded-xl font-bold text-gray-500 hover:bg-gray-50"><UserCheck className="w-5 h-5" /> Quản lý Kết Nối</Link>
        <Link to="/admin/targets" className="flex items-center gap-3 px-4 py-3 rounded-xl font-bold text-gray-500 hover:bg-gray-50"><Settings className="w-5 h-5" /> Chỉ Tiêu</Link>
        <Link to="/admin/reports" className="flex items-center gap-3 px-4 py-3 rounded-xl font-bold text-gray-500 hover:bg-gray-50"><PieChart className="w-5 h-5" /> Thống Kê Báo Cáo</Link>
      </div>
      <div className="p-4 border-t border-gray-100">
        <button onClick={onLogout} className="w-full flex items-center gap-3 px-4 py-3 text-red-500 hover:bg-red-50 font-bold rounded-xl"><X className="w-5 h-5" /> Thoát</button>
      </div>
    </div>
  );
}

function AdminConnections() {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIncoming();
  }, []);

  const fetchIncoming = async () => {
    try {
      const res = await api.get('/connections/incoming');
      setConnections(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (id, accept) => {
    try {
      await api.put(`/connections/${id}?accept=${accept}`);
      toast.success(accept ? "Đã chấp nhận kết nối" : "Đã từ chối");
      fetchIncoming();
    } catch (err) {
      toast.error("Thao tác thất bại");
    }
  };

  return (
    <div className="p-4 md:p-10 flex-1 overflow-y-auto pb-32 animate-fade-in">
      <h1 className="text-2xl md:text-3xl font-black text-gray-800 mb-6 md:mb-8 uppercase tracking-tight">Duyệt Yêu Cầu Kết Nối</h1>
      <div className="glass rounded-2xl md:rounded-3xl p-4 md:p-6 overflow-x-auto shadow-sm">
        {loading ? (
          <div className="py-10 text-center"><div className="animate-spin rounded-full h-8 w-8 border-t-2 border-brand-500 mx-auto"></div></div>
        ) : (
          <table className="w-full text-left min-w-[500px]">
            <thead>
              <tr className="bg-gray-50/50 text-gray-500 font-bold border-b border-gray-100 italic">
                <th className="py-4 px-4 text-xs uppercase tracking-wider">Nhân viên yêu cầu</th>
                <th className="py-4 px-4 text-xs uppercase tracking-wider text-center">Trạng thái</th>
                <th className="py-4 px-4 text-xs uppercase tracking-wider text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50 font-medium">
              {connections.length > 0 ? connections.map(c => (
                <tr key={c.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-3">
                      <img src={c.new_hire.photo || `https://i.pravatar.cc/150?u=${c.new_hire.id}`} className="w-10 h-10 rounded-xl border border-gray-100 shadow-sm" alt="avatar" />
                      <div>
                        <div className="font-bold text-gray-800">{c.new_hire.full_name}</div>
                        <div className="text-[10px] text-gray-400 font-bold uppercase">{c.new_hire.emp_code} • {c.new_hire.department}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-[10px] font-black uppercase tracking-tighter pulse-slow">Chờ duyệt</span>
                  </td>
                  <td className="py-4 px-4 text-right">
                    <div className="flex justify-end gap-2">
                      <button onClick={() => handleAction(c.id, false)} className="px-3 py-1.5 text-xs font-bold text-red-500 hover:bg-red-50 rounded-lg">Từ chối</button>
                      <button onClick={() => handleAction(c.id, true)} className="px-4 py-1.5 text-xs font-bold bg-brand-500 text-white hover:bg-brand-600 rounded-lg shadow-sm">Chấp nhận</button>
                    </div>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="3" className="py-20 text-center text-gray-400 font-bold">Hiện không có yêu cầu nào cần duyệt</td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function AdminTargets() {
  const [selectedMonth, setSelectedMonth] = useState("2026-03");
  const [target, setTarget] = useState({
    period_str: "2026-03",
    operator_required: 5,
    leader_required: 2,
    pl_required: 1,
    tm_required: 1,
    gd_required: 0,
    reward_amount: 500000
  });

  useEffect(() => {
    fetchTarget();
  }, [selectedMonth]);

  const fetchTarget = async () => {
    try {
      const res = await api.get(`/targets/${selectedMonth}`);
      setTarget(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSave = async () => {
    try {
      await api.post('/targets/', target);
      toast.success(`Đã lưu thiết lập chỉ tiêu cho tháng ${selectedMonth}`, { icon: '💾' });
    } catch (err) {
      toast.error("Không thể lưu cấu hình");
    }
  };

  return (
    <div className="p-4 md:p-10 flex-1 overflow-y-auto pb-32">
      <h1 className="text-2xl md:text-3xl font-black text-gray-800 mb-6 md:mb-8 leading-tight">Thiết Lập Chỉ Tiêu KPI Theo Tháng</h1>
      <div className="glass rounded-2xl md:rounded-3xl p-5 md:p-8 border-t-8 border-brand-500 max-w-2xl shadow-xl">
        <div className="mb-8 p-4 bg-brand-50 rounded-2xl border border-brand-100 flex flex-col md:flex-row md:items-center gap-3 md:gap-4">
          <label className="font-bold text-gray-600 text-sm md:text-base">Đang cấu hình cho tháng:</label>
          <input
            type="month"
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="w-full p-3 border border-brand-200 rounded-xl font-black text-brand-700 bg-white shadow-inner"
          />
        </div>

        <h2 className="text-lg md:text-xl font-black mb-6 border-b border-gray-100 pb-3 text-gray-800 flex items-center gap-2">
          <span className="w-8 h-8 bg-brand-100 text-brand-600 rounded-lg flex items-center justify-center text-sm">1</span>
          Định Mức Lượt Quét Yêu Cầu
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-5 mb-8">
          {[
            { label: "Operator (Công Nhân)", key: "operator_required" },
            { label: "Leader", key: "leader_required" },
            { label: "Part Leader", key: "pl_required" },
            { label: "Team Manager", key: "tm_required" }
          ].map((item, idx) => (
            <div key={idx} className="bg-gray-50/50 p-4 rounded-xl border border-gray-100 hover:border-brand-200 transition-colors">
              <label className="font-bold text-gray-500 text-xs uppercase mb-2 block">{item.label}</label>
              <input
                type="number"
                value={target[item.key]}
                onChange={(e) => setTarget({ ...target, [item.key]: parseInt(e.target.value) || 0 })}
                className="w-full p-3 border border-gray-200 rounded-xl font-black bg-white focus:ring-4 focus:ring-brand-500/10 focus:border-brand-500 outline-none transition-all"
              />
            </div>
          ))}
          <div className="bg-brand-50/30 p-4 rounded-xl border border-brand-100 sm:col-span-2">
            <label className="font-bold text-brand-700 text-xs uppercase mb-2 block tracking-wider">Giám Đốc (GD) - Thưởng Thêm</label>
            <input
              type="number"
              value={target.gd_required}
              onChange={(e) => setTarget({ ...target, gd_required: parseInt(e.target.value) || 0 })}
              className="w-full p-3 border border-brand-200 rounded-xl font-black bg-white focus:ring-4 focus:ring-brand-500/10 focus:border-brand-500 outline-none transition-all"
            />
          </div>
        </div>

        <h2 className="text-lg md:text-xl font-black mb-6 border-b border-gray-100 pb-3 text-gray-800 flex items-center gap-2">
          <span className="w-8 h-8 bg-yellow-100 text-yellow-700 rounded-lg flex items-center justify-center text-sm">2</span>
          Gói Thưởng Nóng
        </h2>
        <div className="bg-yellow-50/50 p-5 rounded-2xl border border-yellow-200 mb-8 shadow-inner">
          <label className="font-bold text-yellow-800 text-xs uppercase mb-2 block">Tiền mặt khen thưởng (VND)</label>
          <div className="relative">
            <input
              type="number"
              value={target.reward_amount}
              onChange={(e) => setTarget({ ...target, reward_amount: parseFloat(e.target.value) || 0 })}
              className="w-full p-4 pr-16 border border-yellow-300 rounded-xl font-black text-2xl text-yellow-700 bg-white focus:ring-4 focus:ring-yellow-500/10 outline-none"
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 font-bold text-yellow-600">VNĐ</span>
          </div>
        </div>

        <button onClick={handleSave} className="w-full py-4 bg-gradient-to-r from-brand-600 to-brand-500 text-white font-black text-lg rounded-2xl hover:from-brand-500 hover:to-brand-400 shadow-lg hover:shadow-brand-500/30 active:scale-[0.98] transition-all uppercase">
          LƯU KẾ HOẠCH {selectedMonth}
        </button>
      </div>
    </div>
  );
}

function AdminReports() {
  const [selectedMonth, setSelectedMonth] = useState("2026-03");
  const [stats, setStats] = useState({ total_employees: 0, completed_kpi: 0, projected_reward: 0, total_connections: 0 });
  const [report, setReport] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [selectedMonth]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, reportRes] = await Promise.all([
        api.get(`/admin/stats/${selectedMonth}`),
        api.get(`/admin/report/${selectedMonth}`)
      ]);
      setStats(statsRes.data);
      setReport(reportRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const exportDataToCSV = () => {
    const headers = "Mã NV,Họ tên,Phòng ban,Tháng,Tiến độ,Tiền thưởng (VND)\n";
    const rows = report.map(r => `${r.emp_code},${r.full_name},${r.department},${selectedMonth},${r.count},${r.reward}`).join("\n");
    const csvContent = "data:text/csv;charset=utf-8,\uFEFF" + headers + rows;

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `BaoCao_CSB-Connection_${selectedMonth}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success("Đã xuất CSV báo cáo thành công!");
  };

  return (
    <div className="p-4 md:p-10 flex-1 overflow-y-auto animate-fade-in print:bg-white print:p-0 pb-32">
      <div className="no-print mb-8 space-y-6">
        <h1 className="text-2xl md:text-3xl font-black text-gray-800 leading-tight">Báo Cáo Thống Kê Admin</h1>
        <p className="text-gray-500 font-medium -mt-4">Theo dõi KPI kết nối của nhân sự và hạch toán tiền thưởng.</p>

        <div className="flex flex-col lg:flex-row gap-4 bg-white/50 p-4 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center gap-3">
            <label className="font-bold text-gray-600 text-sm">Chọn Tháng:</label>
            <input type="month" value={selectedMonth} onChange={(e) => setSelectedMonth(e.target.value)} className="p-3 rounded-xl border border-gray-200 bg-white font-black text-brand-700 flex-1 sm:w-48 shadow-inner" />
          </div>
          <div className="flex-1"></div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:flex gap-3">
            <button onClick={() => window.print()} className="bg-gray-800 text-white px-6 py-3 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-black transition-all shadow-md active:scale-95">
              <Printer className="w-5 h-5" /> In Báo Cáo
            </button>
            <button onClick={exportDataToCSV} className="bg-green-600 text-white px-6 py-3 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-green-700 transition-all shadow-md active:scale-95">
              <Download className="w-5 h-5" /> Xuất Excel
            </button>
          </div>
        </div>
      </div>

      {/* Printable Area Starts */}
      <div className="print-only hidden text-center mb-8">
        <h1 className="text-2xl font-black uppercase tracking-widest">Báo Cáo Tiến Độ Kết Nối CSB-Connection</h1>
        <p className="font-bold text-lg mt-2 text-gray-600">Kỳ báo cáo: {selectedMonth}</p>
        <div className="w-20 h-1 bg-brand-500 mx-auto mt-4"></div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-8">
        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm print:border-gray-300">
          <p className="text-gray-400 font-bold text-xs uppercase tracking-wider mb-2">Tổng nhân sự</p>
          <p className="text-3xl font-black text-brand-600 tracking-tighter">{stats.total_employees}</p>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm print:border-gray-300">
          <p className="text-gray-400 font-bold text-xs uppercase tracking-wider mb-2">Đạt Thưởng KPI</p>
          <p className="text-3xl font-black text-green-600 tracking-tighter">{stats.completed_kpi} NV</p>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm print:border-gray-300 sm:col-span-2">
          <p className="text-gray-400 font-bold text-xs uppercase tracking-wider mb-2">Dự chi thưởng ({selectedMonth})</p>
          <p className="text-3xl font-black text-yellow-500 tracking-tighter">{stats.projected_reward.toLocaleString()} <span className="text-sm font-bold text-gray-300">VNĐ</span></p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm print:border">
        <div className="bg-brand-50/50 p-4 border-b border-brand-100 print:bg-white">
          <h3 className="font-black text-brand-700 text-sm tracking-tight print:text-black uppercase">CHI TIẾT MỨC ĐỘ HOÀN THÀNH - {selectedMonth}</h3>
        </div>
        <div className="overflow-x-auto">
          {loading ? (
            <div className="py-20 text-center"><div className="animate-spin rounded-full h-8 w-8 border-t-2 border-brand-500 mx-auto"></div></div>
          ) : (
            <table className="w-full text-left min-w-[600px]">
              <thead>
                <tr className="bg-gray-50/50 text-gray-500 font-bold border-b text-xs uppercase tracking-wider print:bg-gray-100">
                  <th className="py-4 px-4">Mã NV</th>
                  <th className="py-4 px-4">Họ Tên</th>
                  <th className="py-4 px-4">Phòng ban</th>
                  <th className="py-4 px-4 text-center">Tiến độ</th>
                  <th className="py-4 px-4 text-right">Tiền thưởng (VNĐ)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50 font-medium">
                {report.map(r => (
                  <tr key={r.emp_code} className="hover:bg-gray-50/50 transition-colors">
                    <td className="py-4 px-4 font-bold text-gray-800">{r.emp_code}</td>
                    <td className="py-4 px-4 font-black text-brand-600 print:text-black">{r.full_name}</td>
                    <td className="py-4 px-4 text-gray-500">{r.department}</td>
                    <td className="py-4 px-4 text-center">
                      <span className={`font-black px-3 py-1 rounded-full text-[10px] uppercase ${r.reward > 0 ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'}`}>
                        {r.reward > 0 ? 'Đạt ' : 'Đang chạy '} {r.count}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-right font-black text-gray-800">{r.reward.toLocaleString()}</td>
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

export default function App() {
  const [user, setUser] = useState(null);
  const [initializing, setInitializing] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('csb_token');
    if (token) {
      api.get('/auth/me')
        .then(res => {
          const userData = res.data;
          setUser({
            id: userData.employee_profile?.emp_code || userData.username,
            name: userData.employee_profile?.full_name || userData.username,
            isAdmin: userData.is_staff || false,
            profile: userData.employee_profile
          });
        })
        .catch(() => {
          localStorage.removeItem('csb_token');
        })
        .finally(() => setInitializing(false));
    } else {
      setInitializing(false);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('csb_token');
    setUser(null);
    toast('Đã đăng xuất tài khoản', { icon: '👋', style: { borderRadius: '12px' } });
  };

  if (initializing) return (
    <div className="h-screen flex items-center justify-center bg-brand-50">
      <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-brand-600"></div>
    </div>
  );

  return (
    <BrowserRouter>
      <Toaster position="top-center" />
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/" /> : <LoginPage onLogin={setUser} />} />
        <Route path="/tv" element={<TVDashboard />} />

        <Route path="/admin/*" element={!user ? <Navigate to="/login" /> : !user.isAdmin ? <Navigate to="/" /> :
          <div className="flex h-screen bg-[#f8fafc]">
            <AdminSidebar onLogout={handleLogout} />
            <div className="flex-1 flex flex-col min-w-0 pb-16 md:pb-0">
              <Routes>
                <Route path="connections" element={<AdminConnections />} />
                <Route path="targets" element={<AdminTargets />} />
                <Route path="reports" element={<AdminReports />} />
                <Route path="*" element={<Navigate to="reports" />} />
              </Routes>
            </div>
            <MobileBottomNav onLogout={handleLogout} />
          </div>
        } />

        <Route path="/*" element={!user ? <Navigate to="/login" /> :
          <div className="min-h-screen text-gray-900 font-sans pb-16 md:pb-0 relative">
            <DesktopNavbar onLogout={handleLogout} user={user} />
            <main className="px-4 sm:px-6 md:px-8 py-8 md:py-10 max-w-7xl mx-auto">
              <Routes>
                <Route path="/" element={<Dashboard user={user} />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="/qr" element={<QRCodeScanPage />} />
                <Route path="/rewards" element={<div className="glass p-8 rounded-3xl text-center"><Award className="w-16 h-16 mx-auto mb-4 text-brand-400" /><h1 className="text-2xl font-black">Danh sách Thưởng</h1></div>} />
              </Routes>
            </main>
            <MobileBottomNav onLogout={handleLogout} />
          </div>
        } />
      </Routes>
    </BrowserRouter>
  );
}
