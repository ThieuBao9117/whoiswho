import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Award, Users, CheckCircle2, X, ScanLine, Trophy, ArrowRight, Zap } from 'lucide-react';
import api from '../services/api';
import { getAvatarUrl } from '../utils/avatar';

// ─── Confetti helper ──────────────────────────────────────────────────────────

function Confetti() {
  const canvasRef = useRef(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    const colors = ['#f59e0b', '#3b82f6', '#10b981', '#8b5cf6', '#ef4444', '#ec4899'];
    const pieces = Array.from({ length: 80 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height - canvas.height,
      r: Math.random() * 6 + 3,
      d: Math.random() * 3 + 1,
      color: colors[Math.floor(Math.random() * colors.length)],
      tilt: Math.floor(Math.random() * 10) - 10,
      tiltAngleIncrementInc: (Math.random() * 0.07) + 0.05,
      tiltAngle: 0,
    }));

    let animId;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      pieces.forEach(p => {
        p.tiltAngle += p.tiltAngleIncrementInc;
        p.y += (Math.cos(p.d) + p.r / 4);
        p.x += Math.sin(p.d);
        p.tilt = Math.sin(p.tiltAngle) * 12;
        ctx.beginPath();
        ctx.lineWidth = p.r / 2;
        ctx.strokeStyle = p.color;
        ctx.moveTo(p.x + p.tilt + p.r / 4, p.y);
        ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r / 4);
        ctx.stroke();
        if (p.y > canvas.height) { p.y = -10; p.x = Math.random() * canvas.width; }
      });
      animId = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(animId);
  }, []);
  return <canvas ref={canvasRef} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none' }} />;
}

// ─── Congratulations Modal ────────────────────────────────────────────────────

function CongratulationsModal({ gameState, onClose }) {
  const days = gameState?.days_to_complete;
  const completionSecs = gameState?.completion_time_seconds;
  const hours = completionSecs ? Math.floor((completionSecs % 86400) / 3600) : 0;

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'rgba(15,23,42,0.6)', backdropFilter: 'blur(6px)',
      animation: 'fadeIn 0.3s ease',
    }}>
      <style>{`
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes popIn { from { opacity: 0; transform: scale(0.85) translateY(24px); } to { opacity: 1; transform: scale(1) translateY(0); } }
        @keyframes pulse2 { 0%,100% { transform: scale(1); } 50% { transform: scale(1.08); } }
      `}</style>
      <div style={{
        background: 'white', borderRadius: 28, padding: '40px 36px',
        maxWidth: 440, width: '90%', textAlign: 'center', position: 'relative',
        overflow: 'hidden', boxShadow: '0 32px 80px rgba(0,0,0,0.25)',
        animation: 'popIn 0.4s cubic-bezier(0.34,1.56,0.64,1)',
      }}>
        <Confetti />
        <div style={{ position: 'relative', zIndex: 1 }}>
          {/* Trophy icon */}
          <div style={{
            width: 100, height: 100, borderRadius: '50%', margin: '0 auto 20px',
            background: 'linear-gradient(135deg,#fef3c7,#fde68a)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: '4px solid #f59e0b', boxShadow: '0 0 40px rgba(245,158,11,0.3)',
            animation: 'pulse2 2s ease-in-out infinite',
          }}>
            <span style={{ fontSize: 48 }}>🏆</span>
          </div>

          <h2 style={{ fontWeight: 800, fontSize: 26, color: '#1e293b', marginBottom: 8, lineHeight: 1.2 }}>
            🎉 Chúc Mừng!
          </h2>
          <h3 style={{ fontWeight: 700, fontSize: 17, color: '#059669', marginBottom: 16 }}>
            Bạn đã hoàn thành nhiệm vụ!
          </h3>

          <p style={{ color: '#475569', fontSize: 14, lineHeight: 1.7, marginBottom: 24 }}>
            Tuyệt vời! Bạn đã kết nối đủ số lượng đồng nghiệp theo yêu cầu và sẽ được xếp hạng trong bảng xếp hạng tháng này.
          </p>

          {/* Stats */}
          <div style={{ display: 'flex', gap: 12, marginBottom: 28 }}>
            <div style={{ flex: 1, background: '#f0fdf4', borderRadius: 16, padding: '16px 12px', border: '1px solid #bbf7d0' }}>
              <div style={{ fontSize: 22, fontWeight: 800, color: '#16a34a' }}>
                {days !== null && days !== undefined ? `${days}` : '—'}
              </div>
              <div style={{ fontSize: 11, color: '#6b7280', marginTop: 2 }}>Ngày hoàn thành</div>
            </div>
            {hours > 0 && (
              <div style={{ flex: 1, background: '#eff6ff', borderRadius: 16, padding: '16px 12px', border: '1px solid #bfdbfe' }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: '#2563eb' }}>{hours}h</div>
                <div style={{ fontSize: 11, color: '#6b7280', marginTop: 2 }}>Giờ dư</div>
              </div>
            )}
            <div style={{ flex: 1, background: '#fdf4ff', borderRadius: 16, padding: '16px 12px', border: '1px solid #e9d5ff' }}>
              <div style={{ fontSize: 22, fontWeight: 800, color: '#9333ea' }}>✅</div>
              <div style={{ fontSize: 11, color: '#6b7280', marginTop: 2 }}>Đủ chỉ tiêu</div>
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 12 }}>
            <Link
              to="/leaderboard"
              onClick={onClose}
              style={{
                flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                background: 'linear-gradient(135deg,#1d4ed8,#0ea5e9)', color: 'white',
                borderRadius: 14, padding: '12px 16px', fontWeight: 700, fontSize: 14,
                textDecoration: 'none', boxShadow: '0 4px 16px rgba(29,78,216,0.3)',
              }}
            >
              <Trophy style={{ width: 16, height: 16 }} /> Xem bảng xếp hạng
            </Link>
            <button
              onClick={onClose}
              style={{
                flex: 0, padding: '12px 16px', borderRadius: 14, border: '1.5px solid #e2e8f0',
                background: 'white', color: '#475569', fontWeight: 600, cursor: 'pointer', fontSize: 14,
              }}
            >Đóng</button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Progress Bar ─────────────────────────────────────────────────────────────

function ProgressBar({ label, current, max, isComplete }) {
  const pct = max > 0 ? Math.min((current / max) * 100, 100) : 0;
  return (
    <div className="mb-4 last:mb-0">
      <div className="flex justify-between items-center mb-1.5">
        <span className="text-sm font-medium text-surface-600">{label}</span>
        <span className={`text-sm font-bold ${isComplete ? 'text-success-600' : 'text-surface-800'}`}>
          {current} / {max}
        </span>
      </div>
      <div className="w-full bg-surface-100 rounded-full h-3 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${isComplete ? 'bg-gradient-to-r from-success-400 to-success-500' : 'bg-gradient-to-r from-primary-400 to-primary-500'}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

// ─── Main Dashboard ───────────────────────────────────────────────────────────

export default function Dashboard({ user }) {
  const [myConnections, setMyConnections] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCongrats, setShowCongrats] = useState(false);

  // Track if we've already shown the congrats popup this session
  const hasShownRef = useRef(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const now = new Date();
        const [connRes, leaderRes] = await Promise.all([
          api.get('/connections/all'),
          api.get(`/admin/leaderboard?month=${now.getMonth() + 1}&year=${now.getFullYear()}`),
        ]);
        setMyConnections(connRes.data);
        // Support both old (array) and new (object with entries) response format
        const entries = leaderRes.data?.entries || leaderRes.data || [];
        setLeaderboard(Array.isArray(entries) ? entries : []);
      } catch (err) { console.error(err); }
      finally { setLoading(false); }
    };
    fetchData();
  }, []);

  // Show congratulations popup once when user has won (first time this session)
  useEffect(() => {
    if (!hasShownRef.current && user?.gameState?.has_won) {
      // Small delay to let page render first
      const timer = setTimeout(() => {
        setShowCongrats(true);
        hasShownRef.current = true;
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [user?.gameState?.has_won]);

  const gameState = user?.gameState || {};
  const isEligibleForReward = gameState.has_won;

  const stats = [
    { label: "Tiến độ kết nối", current: gameState.current_connections || 0, max: gameState.target_connections || 0 }
  ];

  return (
    <div className="animate-fade-in space-y-6 pb-8">
      {/* Congratulations popup */}
      {showCongrats && (
        <CongratulationsModal gameState={gameState} onClose={() => setShowCongrats(false)} />
      )}

      {/* Admin banner */}
      {user?.isAdmin && (
        <div className="bg-primary-600 text-white rounded-2xl p-4 flex justify-between items-center md:hidden">
          <div>
            <h3 className="font-heading font-bold">Quyền Quản Trị</h3>
            <p className="text-sm text-primary-200">Bạn có quyền truy cập Admin</p>
          </div>
          <Link to="/admin" className="bg-white text-primary-600 px-4 py-2 rounded-xl text-sm font-semibold">Vào Admin</Link>
        </div>
      )}

      {/* User profile card */}
      <div className="card p-6 md:p-8">
        <div className="flex flex-col md:flex-row items-center md:items-start justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="relative">
              <img src={getAvatarUrl(user?.profile?.photo, user?.profile?.full_name)} alt="Avatar"
                className="w-16 h-16 md:w-20 md:h-20 rounded-full border-2 border-primary-200 object-cover" />
              <div className="absolute -bottom-1 -right-1 bg-success-500 text-white p-1 rounded-full">
                <CheckCircle2 className="h-3.5 w-3.5" />
              </div>
            </div>
            <div>
              <h1 className="text-xl md:text-2xl font-heading font-bold text-surface-800">{user?.name}</h1>
              <div className="flex items-center gap-2 mt-1 flex-wrap">
                <span className="badge badge-primary">{user?.profile?.part || user?.profile?.department || "Nhân viên"}</span>
                <span className="text-sm text-surface-400">{user?.profile?.emp_code}</span>
                {(() => {
                  const role = (gameState.role || user?.profile?.role || '').toLowerCase();
                  const actualRole = gameState.role || user?.profile?.role || '';
                  let icon = '💼';
                  let bg = 'linear-gradient(135deg,#8b5cf6,#6d28d9)';
                  if (role.includes('operator') || role.includes('công nhân')) {
                    icon = '🔧'; bg = 'linear-gradient(135deg,#3b82f6,#1d4ed8)';
                  } else if (role.includes('director') || role.includes('manager') || role.includes('giám đốc')) {
                    icon = '🌟'; bg = 'linear-gradient(135deg,#f59e0b,#d97706)';
                  } else if (role.includes('leader') || role.includes('trưởng')) {
                    icon = '👑'; bg = 'linear-gradient(135deg,#10b981,#059669)';
                  } else if (role.includes('engineer') || role.includes('kỹ sư')) {
                    icon = '⚙️'; bg = 'linear-gradient(135deg,#06b6d4,#0284c7)';
                  } else if (role.includes('inspector') || role.includes('qc') || role.includes('qa')) {
                    icon = '🔍'; bg = 'linear-gradient(135deg,#8b5cf6,#6d28d9)';
                  }
                  if (!actualRole) return null;
                  return (
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', gap: 4,
                      background: bg,
                      color: 'white', borderRadius: 999, padding: '2px 10px', fontSize: 11, fontWeight: 700,
                    }}>
                      {icon} {actualRole}
                    </span>
                  );
                })()}
              </div>
            </div>
          </div>

          <div className="flex gap-4 w-full md:w-auto">
            <div className={`card p-4 flex-1 md:min-w-[120px] text-center ${gameState.is_expired && !gameState.has_won ? 'border-danger-200 bg-danger-50' : ''}`}>
              <p className="text-xs text-surface-500 mb-1">{gameState.is_expired ? 'Đã hết hạn' : 'Thời hạn còn'}</p>
              <p className={`text-2xl font-heading font-bold ${gameState.is_expired && !gameState.has_won ? 'text-danger-500' : 'text-primary-600'}`}>
                {gameState.days_remaining || 0} <span className="text-sm font-normal text-surface-400">ngày</span>
              </p>
            </div>
            <div className={`card p-4 flex-1 md:min-w-[120px] text-center ${isEligibleForReward ? 'border-accent-300 bg-accent-50' : ''}`}>
              <p className="text-xs text-surface-500 mb-1">Tiền thưởng</p>
              <p className="text-xl font-heading font-bold text-accent-600">
                {isEligibleForReward ? '200K' : '0'} <span className="text-sm font-normal text-surface-400">VNĐ</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Mission accomplished banner */}
      {gameState.has_won && (
        <div className="bg-gradient-to-r from-success-50 to-accent-50 border border-success-200 rounded-2xl p-6 text-center animate-scale-in">
          <Award className="w-14 h-14 text-accent-500 mx-auto mb-3" />
          <h2 className="text-2xl font-heading font-bold text-success-700 mb-2">🎉 Hoàn thành nhiệm vụ!</h2>
          <p className="text-surface-600 mb-3">Bạn đã kết nối đủ số lượng đồng nghiệp theo yêu cầu.</p>
          <div className="flex justify-center gap-3 flex-wrap">
            <span className="badge badge-success text-sm px-4 py-1.5">
              ⏱ Thời gian: {gameState.days_to_complete !== null && gameState.days_to_complete !== undefined
                ? `${gameState.days_to_complete} ngày`
                : gameState.completion_time_seconds
                  ? `${Math.floor(gameState.completion_time_seconds / 3600)}h ${Math.floor((gameState.completion_time_seconds % 3600) / 60)}m`
                  : 'N/A'}
            </span>
            <button
              onClick={() => setShowCongrats(true)}
              className="badge badge-neutral text-sm px-4 py-1.5 cursor-pointer hover:bg-surface-200 transition-colors"
            >🏆 Xem chúc mừng lại</button>
          </div>
        </div>
      )}

      {gameState.is_expired && !gameState.has_won && (
        <div className="bg-danger-50 border border-danger-200 rounded-2xl p-6 text-center">
          <X className="w-14 h-14 text-danger-400 mx-auto mb-3" />
          <h2 className="text-2xl font-heading font-bold text-danger-600 mb-2">Hết thời hạn</h2>
          <p className="text-surface-500">Thời gian để hoàn thành kết nối đã hết.</p>
        </div>
      )}

      {/* ── Thể Lệ Mini Game ──────────────────────────────────────────── */}
      <div style={{
        background: 'linear-gradient(135deg, #f0f9ff 0%, #faf5ff 50%, #fff7ed 100%)',
        border: '1.5px solid #e0e7ff',
        borderRadius: 20,
        padding: '24px 28px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Decorative blobs */}
        <div style={{
          position: 'absolute', top: -20, right: -20, width: 120, height: 120,
          background: 'radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%)',
          borderRadius: '50%', pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute', bottom: -10, left: -10, width: 80, height: 80,
          background: 'radial-gradient(circle, rgba(59,130,246,0.07) 0%, transparent 70%)',
          borderRadius: '50%', pointerEvents: 'none',
        }} />

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <span style={{ fontSize: 22 }}>🎮</span>
          <h3 style={{ fontSize: 16, fontWeight: 800, color: '#1e293b', margin: 0 }}>
            Thể Lệ Mini Game:&nbsp;
            <span style={{ background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              WHO IS WHO?
            </span>
          </h3>
        </div>

        {/* Mục tiêu */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16,
          background: 'linear-gradient(135deg,#dcfce7,#bbf7d0)',
          borderRadius: 12, padding: '10px 16px',
          border: '1px solid #86efac',
        }}>
          <span style={{ fontSize: 18 }}>🎯</span>
          <p style={{ margin: 0, fontSize: 13, color: '#15803d', fontWeight: 700 }}>
            Mục tiêu: Nhận ngay{' '}
            <span style={{ color: '#166534', fontSize: 15 }}>200.000 VNĐ</span>
            {' '}tiền thưởng khi hoàn thành thử thách làm quen!
          </p>
        </div>

        {/* Quy định chạm mốc */}
        <div>
          <p style={{ fontSize: 12, fontWeight: 700, color: '#64748b', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>📋</span> Quy định chạm mốc:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[
              {
                icon: '👷',
                label: 'Nhân viên Sản Xuất (Operator)',
                desc: 'Đạt 10 kết nối trong 1 tháng thử việc.',
                color: '#1d4ed8', bg: '#eff6ff', border: '#bfdbfe',
              },
              {
                icon: '👥',
                label: 'Trưởng Nhóm (Team Leader)',
                desc: 'Đạt 20 kết nối trong 1 tháng thử việc.',
                color: '#7c3aed', bg: '#f5f3ff', border: '#ddd6fe',
              },
              {
                icon: '🧑‍💼',
                label: 'Nhân viên Văn Phòng (Staff)',
                desc: 'Đạt 30 kết nối trong 2 tháng thử việc.',
                color: '#0369a1', bg: '#f0f9ff', border: '#bae6fd',
              },
            ].map((item) => (
              <div key={item.label} style={{
                display: 'flex', alignItems: 'flex-start', gap: 10,
                background: item.bg, border: `1px solid ${item.border}`,
                borderRadius: 12, padding: '10px 14px',
              }}>
                <span style={{ fontSize: 16, marginTop: 1 }}>{item.icon}</span>
                <div>
                  <span style={{ fontSize: 13, fontWeight: 700, color: item.color }}>{item.label}:</span>
                  {' '}
                  <span style={{ fontSize: 13, color: '#475569' }}>{item.desc}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main content */}

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Quests */}
        <div className="md:col-span-8">
          <div className="card p-6 md:p-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-heading font-bold text-surface-800 flex items-center gap-2">
                <Zap className="w-5 h-5 text-accent-500" /> Nhiệm vụ kết nối
              </h2>
              <span className="badge badge-neutral">Tháng {new Date().toLocaleDateString('vi-VN', { month: '2-digit', year: 'numeric' })}</span>
            </div>

            {loading ? (
              <div className="flex justify-center py-16">
                <div className="w-10 h-10 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
              </div>
            ) : (
              <div className="space-y-4">
                {stats.map((stat, i) => (
                  <ProgressBar key={i} label={stat.label} current={stat.current} max={stat.max}
                    isComplete={stat.max > 0 && stat.current >= stat.max} />
                ))}

                {/* Danh sách đã kết nối */}
                <div className="mt-8 pt-6 border-t border-surface-100">
                  <h3 className="text-sm font-bold text-surface-700 mb-4 flex items-center gap-2">
                    <Users className="w-4 h-4 text-primary-500" />
                    Đồng nghiệp đã kết nối ({myConnections.filter(c => c.status === 'ACCEPTED').length})
                  </h3>
                  {myConnections.filter(c => c.status === 'ACCEPTED').length > 0 ? (
                    <div className="flex gap-4 overflow-x-auto pb-4 snap-x smooth-scrollbar">
                      {myConnections.filter(c => c.status === 'ACCEPTED').map(c => {
                        const person = c.other_user;
                        if (!person) return null;
                        return (
                          <div key={c.id} className="flex flex-col items-center flex-shrink-0 w-20 snap-start">
                            <img src={getAvatarUrl(person.photo, person.full_name)} className="w-14 h-14 rounded-full border-2 border-success-400 object-cover mb-2 shadow-sm" alt="" title={person.full_name} />
                            <span className="text-[11px] font-medium text-surface-800 text-center leading-tight line-clamp-2" title={person.full_name}>{person.full_name}</span>
                            <span className="text-[9px] text-surface-400 text-center mt-0.5 max-w-full overflow-hidden text-ellipsis whitespace-nowrap">{person.department || 'N/A'}</span>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="text-center py-6 bg-surface-50 rounded-xl border border-dashed border-surface-200">
                      <p className="text-sm text-surface-400">Bạn chưa có kết nối nào.</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {gameState.can_play ? (
              <Link to="/search" className="btn-primary w-full py-3.5 mt-8 flex items-center justify-center gap-2 text-base">
                <Users className="h-5 w-5" />
                {gameState.has_won ? '⭐ Tiếp tục kết nối thêm' : 'Tìm đồng nghiệp để kết nối'}
                <ArrowRight className="h-4 w-4" />
              </Link>
            ) : (
              <button disabled className="btn-secondary w-full py-3.5 mt-8 opacity-50 cursor-not-allowed flex items-center justify-center gap-2">
                <X className="h-5 w-5" /> Đã hết thời hạn
              </button>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="md:col-span-4 space-y-6">
          {/* Leaderboard */}
          <div className="card p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-heading font-bold text-surface-800 flex items-center gap-2 text-sm">
                <Trophy className="h-5 w-5 text-accent-500" /> Bảng xếp hạng
              </h3>
              <Link to="/leaderboard" className="text-xs text-primary-600 hover:text-primary-700 font-semibold">
                Xem tất cả →
              </Link>
            </div>
            <div className="space-y-3">
              {leaderboard.slice(0, 5).map((person, idx) => (
                <div key={person.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${idx === 0 ? 'bg-accent-100 text-accent-700' : idx === 1 ? 'bg-surface-200 text-surface-600' : 'bg-surface-100 text-surface-400'}`}>
                      {idx + 1}
                    </span>
                    <img src={person.avatar || `https://i.pravatar.cc/40?u=${person.id}`} className="w-8 h-8 rounded-full object-cover" alt="" />
                    <div>
                      <h4 className="text-sm font-medium text-surface-700">{person.name}</h4>
                      <p className="text-[11px] text-surface-400">{person.dept}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold text-primary-600">
                      {person.days_to_complete !== undefined ? `${person.days_to_complete} ngày` : person.completion_time || person.score}
                    </span>
                    <div style={{
                      fontSize: 9, fontWeight: 700, borderRadius: 999, padding: '1px 6px',
                      background: person.is_operator ? '#dbeafe' : '#ede9fe',
                      color: person.is_operator ? '#1d4ed8' : '#6d28d9',
                      marginTop: 2, display: 'inline-block',
                    }}>
                      {person.is_operator ? 'OP' : 'ST'}
                    </div>
                  </div>
                </div>
              ))}
              {leaderboard.length === 0 && <p className="text-sm text-surface-400 text-center py-4">Chưa có dữ liệu</p>}
            </div>
          </div>

          {/* Hint */}
          <div className="card p-6 bg-gradient-to-br from-primary-50 to-accent-50 border-primary-100">
            <h3 className="font-heading font-bold text-primary-700 text-sm mb-2 flex items-center gap-2">
              💡 Mẹo nhanh
            </h3>
            <p className="text-sm text-surface-600 leading-relaxed">
              Hãy <b className="text-primary-600">chủ động kết nối</b> và quét mã QR của bất kỳ đồng nghiệp nào để sớm đạt được tiền thưởng nhé!
            </p>
            <Link to="/qr" className="mt-4 flex items-center gap-2 text-primary-600 font-semibold text-sm hover:text-primary-700 transition-colors">
              Quét QR ngay <ScanLine className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
