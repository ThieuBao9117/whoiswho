import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate, useNavigate } from 'react-router-dom';
import {
  Bell, Search, Award, Users, QrCode, CheckCircle2, X, ScanLine, LayoutDashboard,
  Settings, UserCheck, Shield, Lock, User, PieChart, Download, Printer, LogOut, Home, Menu, Trophy
} from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import api from './services/api';

// Page imports
import SearchPage from './pages/SearchPage';
import Dashboard from './pages/Dashboard';
import QRCodeScanPage from './pages/QRCodeScanPage';
import NotificationsPage from './pages/NotificationsPage';
import TVDashboard from './pages/TVDashboard';
import LeaderboardPage from './pages/LeaderboardPage';
import AdminConnections from './pages/admin/AdminConnections';
import AdminTargets from './pages/admin/AdminTargets';
import AdminReports from './pages/admin/AdminReports';

// ----------------------
// LOGIN PAGE
// ----------------------
function LoginPage({ onLogin }) {
  const [loading, setLoading] = useState(false);
  const [empId, setEmpId] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.post('/auth/login', { username: empId, password });
      const { access_token } = response.data;
      localStorage.setItem('csb_token', access_token);

      const userRes = await api.get('/auth/me');
      const userData = userRes.data;
      const mappedUser = {
        id: userData.employee_profile?.emp_code || userData.username,
        name: userData.employee_profile?.full_name || userData.username,
        isAdmin: userData.is_staff || false,
        profile: userData.employee_profile,
        gameState: userData.game_state,
      };
      onLogin(mappedUser);
      navigate('/');
      toast.success(mappedUser.isAdmin ? 'Đăng nhập Admin thành công!' : 'Đăng nhập thành công!');
    } catch (err) {
      console.error(err);
      toast.error('Đăng nhập thất bại. Vui lòng kiểm tra lại tài khoản.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary-50 via-white to-accent-50">
      <div className="card w-full max-w-md p-8 md:p-10 animate-fade-in">
        <div className="flex flex-col items-center mb-8">
          <div className="w-20 h-20 bg-primary-100 rounded-2xl flex items-center justify-center mb-4">
            <img src="/logo.png" className="h-12 w-auto object-contain" alt="CSB Logo" />
          </div>
          <h1 className="text-2xl font-heading font-bold text-surface-800 text-center">CSB Connection</h1>
          <p className="text-surface-500 mt-1 text-sm">Hệ thống kết nối đồng nghiệp</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label className="text-sm font-semibold text-surface-600 block mb-1.5">Mã nhân viên</label>
            <div className="relative">
              <User className="absolute left-3.5 top-3.5 h-5 w-5 text-surface-400" />
              <input
                type="text" placeholder="Nhập mã nhân viên" required
                value={empId} onChange={(e) => setEmpId(e.target.value)}
                className="input-field pl-11"
              />
            </div>
          </div>
          <div>
            <label className="text-sm font-semibold text-surface-600 block mb-1.5">Mật khẩu</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3.5 h-5 w-5 text-surface-400" />
              <input
                type="password" placeholder="Nhập mật khẩu" required
                value={password} onChange={(e) => setPassword(e.target.value)}
                className="input-field pl-11"
              />
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full py-3.5 text-base">
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Đang đăng nhập...
              </span>
            ) : 'Đăng nhập'}
          </button>
        </form>
      </div>
    </div>
  );
}

// ----------------------
// SSO HANDLER
// ----------------------
function SSOHandler({ onLogin }) {
  const [status, setStatus] = useState('Đang xác thực tài khoản từ HRM...');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const hrmToken = params.get('token');

    if (!hrmToken) {
      toast.error('Không tìm thấy mã xác thực SSO!');
      navigate('/login');
      return;
    }

    const processSSO = async () => {
      try {
        // Exchange HRM token for CSB access token
        const response = await api.post(`/auth/sso-login?token=${hrmToken}`);
        const { access_token } = response.data;
        localStorage.setItem('csb_token', access_token);

        // Fetch user profile
        const userRes = await api.get('/auth/me');
        const userData = userRes.data;
        const mappedUser = {
          id: userData.employee_profile?.emp_code || userData.username,
          name: userData.employee_profile?.full_name || userData.username,
          isAdmin: userData.is_staff || false,
          profile: userData.employee_profile,
          gameState: userData.game_state,
        };
        
        onLogin(mappedUser);
        toast.success('Đăng nhập thành công qua hệ thống nhân sự!');
        navigate('/');
      } catch (err) {
        console.error(err);
        setStatus('Xác thực thất bại! Token không hợp lệ hoặc đã hết hạn.');
        toast.error('Đăng nhập SSO thất bại. Vui lòng đăng nhập lại từ HRM.');
        setTimeout(() => navigate('/login'), 2000);
      }
    };

    processSSO();
  }, [location, navigate, onLogin]);

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-surface-50">
      <div className="card p-8 flex flex-col items-center max-w-sm w-full text-center">
        <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4" />
        <h2 className="text-lg font-bold text-surface-800">Đang xử lý SSO</h2>
        <p className="text-surface-500 mt-2 text-sm">{status}</p>
      </div>
    </div>
  );
}

// ----------------------
// MOBILE BOTTOM NAV
// ----------------------
function MobileBottomNav({ onLogout, notifCount = 0 }) {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;
  if (location.pathname === '/tv' || location.pathname === '/login') return null;

  if (location.pathname.startsWith('/admin')) {
    return (
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-surface-200 z-50 md:hidden shadow-float">
        <div className="flex justify-around items-center py-2 px-1">
          <Link to="/admin/connections" className={`flex flex-col items-center flex-1 py-1 ${isActive('/admin/connections') ? 'text-primary-600' : 'text-surface-400'}`}>
            <UserCheck className="h-5 w-5" /><span className="text-[10px] mt-0.5 font-medium">Kết nối</span>
          </Link>
          <Link to="/tv" target="_blank" className="flex flex-col items-center flex-1 py-1 text-surface-400">
            <LayoutDashboard className="h-5 w-5" /><span className="text-[10px] mt-0.5 font-medium">TV</span>
          </Link>
          <Link to="/admin/targets" className={`flex flex-col items-center flex-1 py-1 ${isActive('/admin/targets') ? 'text-primary-600' : 'text-surface-400'}`}>
            <Settings className="h-5 w-5" /><span className="text-[10px] mt-0.5 font-medium">Chỉ tiêu</span>
          </Link>
          <Link to="/admin/reports" className={`flex flex-col items-center flex-1 py-1 ${isActive('/admin/reports') ? 'text-primary-600' : 'text-surface-400'}`}>
            <PieChart className="h-5 w-5" /><span className="text-[10px] mt-0.5 font-medium">Báo cáo</span>
          </Link>
          <button onClick={onLogout} className="flex flex-col items-center flex-1 py-1 text-danger-400">
            <LogOut className="h-5 w-5" /><span className="text-[10px] mt-0.5 font-medium">Thoát</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-surface-200 z-50 md:hidden shadow-float">
      <div className="flex justify-around items-center py-2 px-1">
        <Link to="/" className={`flex flex-col items-center flex-1 py-1 ${isActive('/') ? 'text-primary-600' : 'text-surface-400'}`}>
          <Home className="h-5 w-5" /><span className="text-[10px] mt-0.5 font-medium">Trang chủ</span>
        </Link>
        <Link to="/search" className={`flex flex-col items-center flex-1 py-1 ${isActive('/search') ? 'text-primary-600' : 'text-surface-400'}`}>
          <Search className="h-5 w-5" /><span className="text-[10px] mt-0.5 font-medium">Tìm kiếm</span>
        </Link>
        <Link to="/qr" className="flex flex-col items-center flex-1 py-1 relative">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center -mt-5 shadow-lg ${isActive('/qr') ? 'bg-primary-600 text-white' : 'bg-primary-500 text-white'}`}>
            <ScanLine className="h-6 w-6" />
          </div>
        </Link>
        <Link to="/leaderboard" className={`flex flex-col items-center flex-1 py-1 ${isActive('/leaderboard') ? 'text-primary-600' : 'text-surface-400'}`}>
          <Trophy className="h-5 w-5" /><span className="text-[10px] mt-0.5 font-medium">Xếp hạng</span>
        </Link>
        <Link to="/notifications" className={`flex flex-col items-center flex-1 py-1 relative ${isActive('/notifications') ? 'text-primary-600' : 'text-surface-400'}`}>
          <div className="relative">
            <Bell className="h-5 w-5" />
            {notifCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 bg-danger-500 text-white text-[9px] font-bold w-4 h-4 flex items-center justify-center rounded-full">{notifCount > 9 ? '9+' : notifCount}</span>
            )}
          </div>
          <span className="text-[10px] mt-0.5 font-medium">Thông báo</span>
        </Link>
        <button onClick={onLogout} className="flex flex-col items-center flex-1 py-1 text-surface-400">
          <LogOut className="h-5 w-5" /><span className="text-[10px] mt-0.5 font-medium">Thoát</span>
        </button>
      </div>
    </div>
  );
}

// ----------------------
// DESKTOP NAVBAR
// ----------------------
function DesktopNavbar({ onLogout, user, notifCount = 0 }) {
  const location = useLocation();
  if (location.pathname === '/tv' || location.pathname.startsWith('/admin') || location.pathname === '/login') return null;

  const navLink = (path, label) => (
    <Link to={path} className={`text-sm font-medium px-3 py-2 rounded-lg transition-colors ${location.pathname === path ? 'bg-primary-50 text-primary-700' : 'text-surface-600 hover:text-primary-600 hover:bg-surface-100'}`}>
      {label}
    </Link>
  );

  return (
    <nav className="bg-white/80 backdrop-blur-lg sticky top-0 z-50 border-b border-surface-200 hidden md:block shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img src="/logo.png" className="h-9 w-auto" alt="Logo" />
          <span className="text-lg font-heading font-bold text-surface-800">CSB Connection</span>
        </div>
        <div className="flex items-center gap-1">
          {navLink('/', 'Trang chủ')}
          {navLink('/search', 'Tìm kiếm')}
          {navLink('/qr', 'Quét QR')}
          {navLink('/leaderboard', '🏆 Xếp hạng')}
          <Link to="/notifications" className={`text-sm font-medium px-3 py-2 rounded-lg transition-colors relative ${location.pathname === '/notifications' ? 'bg-primary-50 text-primary-700' : 'text-surface-600 hover:text-primary-600 hover:bg-surface-100'}`}>
            Thông báo
            {notifCount > 0 && <span className="absolute -top-0.5 -right-0.5 bg-danger-500 text-white text-[9px] font-bold w-4 h-4 flex items-center justify-center rounded-full">{notifCount > 9 ? '9+' : notifCount}</span>}
          </Link>
          {user?.isAdmin && (
            <Link to="/admin/reports" className="btn-primary text-xs px-4 py-2 ml-2">Quản trị</Link>
          )}
          <div className="h-6 w-px bg-surface-200 mx-2" />
          <div className="flex items-center gap-2 bg-surface-50 rounded-xl px-3 py-1.5">
            <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-sm">
              {user?.name?.charAt(0) || 'U'}
            </div>
            <span className="text-sm font-medium text-surface-700 hidden lg:block">{user?.name}</span>
          </div>
          <button onClick={onLogout} className="text-surface-400 hover:text-danger-500 p-2 rounded-lg hover:bg-danger-50 transition-colors" title="Đăng xuất">
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
    </nav>
  );
}

// ----------------------
// ADMIN SIDEBAR
// ----------------------
function AdminSidebar({ onLogout }) {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;
  const sideLink = (path, icon, label) => (
    <Link to={path} className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors ${isActive(path) ? 'bg-primary-50 text-primary-700' : 'text-surface-600 hover:bg-surface-100 hover:text-surface-800'}`}>
      {icon}<span>{label}</span>
    </Link>
  );

  return (
    <div className="bg-white w-64 border-r border-surface-200 flex-shrink-0 flex flex-col hidden md:flex">
      <div className="p-6 border-b border-surface-100 flex items-center gap-3">
        <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
          <Shield className="w-5 h-5 text-primary-600" />
        </div>
        <div>
          <span className="font-heading font-bold text-surface-800">Quản trị</span>
          <p className="text-xs text-surface-400">CSB Connection</p>
        </div>
      </div>
      <div className="p-3 flex-1 space-y-1">
        {sideLink('/admin/connections', <UserCheck className="w-5 h-5" />, 'Yêu cầu kết nối')}
        {sideLink('/admin/targets', <Settings className="w-5 h-5" />, 'Thiết lập chỉ tiêu')}
        {sideLink('/admin/reports', <PieChart className="w-5 h-5" />, 'Báo cáo')}
        <Link to="/" className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-surface-500 hover:bg-surface-100 hover:text-surface-700 transition-colors">
          <Home className="w-5 h-5" /><span>Về trang chủ</span>
        </Link>
      </div>
      <div className="p-3 border-t border-surface-100">
        <button onClick={onLogout} className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-danger-500 hover:bg-danger-50 transition-colors">
          <LogOut className="w-5 h-5" /><span>Đăng xuất</span>
        </button>
      </div>
    </div>
  );
}

// ----------------------
// MAIN APP
// ----------------------
export default function App() {
  const [user, setUser] = useState(null);
  const [initializing, setInitializing] = useState(true);
  const [notifCount, setNotifCount] = useState(0);

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
            profile: userData.employee_profile,
            gameState: userData.game_state,
          });
          api.get('/connections/incoming').then(r => setNotifCount(r.data.length)).catch(() => {});
        })
        .catch(() => { localStorage.removeItem('csb_token'); })
        .finally(() => setInitializing(false));
    } else {
      setInitializing(false);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('csb_token');
    setUser(null);
    setNotifCount(0);
    toast('Đã đăng xuất', { icon: '👋' });
  };

  if (initializing) return (
    <div className="h-screen flex items-center justify-center bg-surface-50">
      <div className="w-10 h-10 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
    </div>
  );

  return (
    <BrowserRouter basename="/game">
      <Toaster position="top-center" toastOptions={{
        className: 'text-sm font-medium',
        style: { borderRadius: '12px', padding: '12px 16px' }
      }} />
      <Routes>
        <Route path="/sso" element={<SSOHandler onLogin={setUser} />} />
        <Route path="/login" element={user ? <Navigate to="/" /> : <LoginPage onLogin={setUser} />} />
        <Route path="/tv" element={<TVDashboard />} />

        <Route path="/admin/*" element={!user ? <Navigate to="/login" /> : !user.isAdmin ? <Navigate to="/" /> :
          <div className="flex h-screen bg-surface-50 overflow-hidden">
            <AdminSidebar onLogout={handleLogout} />
            <div className="flex-1 flex flex-col min-w-0 pb-16 md:pb-0 overflow-y-auto">
              <Routes>
                <Route path="connections" element={<AdminConnections />} />
                <Route path="targets" element={<AdminTargets />} />
                <Route path="reports" element={<AdminReports />} />
                <Route path="*" element={<Navigate to="reports" />} />
              </Routes>
            </div>
            <MobileBottomNav onLogout={handleLogout} notifCount={notifCount} />
          </div>
        } />

        <Route path="/*" element={!user ? <Navigate to="/login" /> :
          <div className="min-h-screen bg-surface-50 pb-20 md:pb-0">
            <DesktopNavbar onLogout={handleLogout} user={user} notifCount={notifCount} />
            <main className="px-4 sm:px-6 md:px-8 py-6 md:py-8 max-w-7xl mx-auto">
              <Routes>
                <Route path="/" element={<Dashboard user={user} />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="/qr" element={<QRCodeScanPage user={user} />} />
                <Route path="/leaderboard" element={<LeaderboardPage />} />
                <Route path="/notifications" element={<NotificationsPage onNotifCountChange={setNotifCount} />} />
                <Route path="/rewards" element={<Navigate to="/notifications" />} />
              </Routes>
            </main>
            <MobileBottomNav onLogout={handleLogout} notifCount={notifCount} />
          </div>
        } />
      </Routes>
    </BrowserRouter>
  );
}
