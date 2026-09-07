import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import { getAvatarUrl } from '../utils/avatar';

/* ─── palette cho bubble avatars ─────────────────────────── */
const BUBBLE_COLORS = [
  { bg: 'linear-gradient(135deg,#f472b6,#ec4899)', shadow: '#f472b680', ring: '#fce7f3' },
  { bg: 'linear-gradient(135deg,#a78bfa,#7c3aed)', shadow: '#a78bfa80', ring: '#ede9fe' },
  { bg: 'linear-gradient(135deg,#34d399,#059669)', shadow: '#34d39980', ring: '#d1fae5' },
  { bg: 'linear-gradient(135deg,#fb923c,#ea580c)', shadow: '#fb923c80', ring: '#ffedd5' },
  { bg: 'linear-gradient(135deg,#38bdf8,#0284c7)', shadow: '#38bdf880', ring: '#e0f2fe' },
  { bg: 'linear-gradient(135deg,#fbbf24,#d97706)', shadow: '#fbbf2480', ring: '#fef3c7' },
  { bg: 'linear-gradient(135deg,#f87171,#dc2626)', shadow: '#f8717180', ring: '#fee2e2' },
  { bg: 'linear-gradient(135deg,#818cf8,#4f46e5)', shadow: '#818cf880', ring: '#e0e7ff' },
];

/* ─── positions for surrounding bubbles (% of container) ─── */
const ORBIT_POSITIONS = [
  { top: '18%', left: '15%'  },   // 0 upper-left
  { top: '15%', left: '62%'  },   // 1 upper-right
  { top: '45%', left: '8%'   },   // 2 left
  { top: '42%', left: '76%'  },   // 3 right-top
  { top: '68%', left: '70%'  },   // 4 right-bottom
  { top: '72%', left: '22%'  },   // 5 bottom-left
  { top: '70%', left: '48%'  },   // 6 bottom-center
  { top: '30%', left: '88%'  },   // 7 far-right
];

/* ─── Confetti particle ─────────────────────────────────── */
function Confetti() {
  const pieces = Array.from({ length: 60 }, (_, i) => ({
    id: i,
    left: Math.random() * 100,
    delay: Math.random() * 5,
    dur: 3 + Math.random() * 4,
    color: ['#f472b6','#fbbf24','#34d399','#60a5fa','#a78bfa','#fb923c','#f87171'][i % 7],
    size: 6 + Math.random() * 8,
    rotate: Math.random() * 360,
  }));

  return (
    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden', zIndex: 0 }}>
      {pieces.map(p => (
        <div key={p.id} style={{
          position: 'absolute',
          left: `${p.left}%`,
          top: '-20px',
          width: p.size,
          height: p.size,
          background: p.color,
          borderRadius: Math.random() > 0.5 ? '50%' : '2px',
          transform: `rotate(${p.rotate}deg)`,
          opacity: 0.85,
          animation: `confetti-fall ${p.dur}s ${p.delay}s linear infinite`,
        }} />
      ))}
    </div>
  );
}

/* ─── SVG Lines between center and each bubble ──────────── */
function NetworkLines({ count }) {
  // Center is approx 50%, 42% in the orbit container
  const cx = 50, cy = 44;
  const lines = ORBIT_POSITIONS.slice(0, count).map((pos, i) => {
    const bx = parseFloat(pos.left) + 7; // center of bubble (~14% wide bubble)
    const by = parseFloat(pos.top) + 10;
    return { x1: cx, y1: cy, x2: bx, y2: by, i };
  });

  return (
    <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', zIndex: 1, pointerEvents: 'none' }}
      viewBox="0 0 100 100" preserveAspectRatio="none">
      <defs>
        <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#fff" stopOpacity="0.6" />
          <stop offset="100%" stopColor="#fff" stopOpacity="0.1" />
        </linearGradient>
      </defs>
      {lines.map(({ x1, y1, x2, y2, i }) => (
        <g key={i}>
          <line x1={x1} y1={y1} x2={x2} y2={y2}
            stroke="url(#lineGrad)" strokeWidth="0.4"
            strokeDasharray="1.5 1"
            style={{ animation: `dash-anim 3s linear infinite ${i * 0.4}s` }}
          />
          {/* Connection count badge on line midpoint */}
          <circle cx={(x1+x2)/2} cy={(y1+y2)/2} r="2.2"
            fill={BUBBLE_COLORS[i % BUBBLE_COLORS.length].bg.includes('f472b6') ? '#f472b6' : '#fbbf24'}
            style={{ filter: 'drop-shadow(0 0 2px rgba(255,255,255,0.8))' }}
          />
        </g>
      ))}
    </svg>
  );
}

/* ─── Avatar bubble ─────────────────────────────────────── */
function AvatarBubble({ user, color, size = 110, isCenter = false, rank = 0 }) {
  const score = user.raw_count ?? user.score ?? '';
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
      animation: `pop-in 0.5s cubic-bezier(.34,1.56,.64,1) ${rank * 0.12}s both`,
    }}>
      {/* Crown for #1 */}
      {isCenter && (
        <div style={{ fontSize: 36, lineHeight: 1, filter: 'drop-shadow(0 2px 8px #fbbf24)', marginBottom: -4 }}>
          👑
        </div>
      )}

      {/* Circle avatar - fill the frame while preserving the photo aspect ratio */}
      <div style={{
        width: size,
        height: size,
        borderRadius: '50%',
        overflow: 'hidden',
        border: `4px solid ${color.ring}`,
        boxShadow: `0 0 ${isCenter ? 40 : 20}px ${color.shadow}, 0 4px 20px rgba(0,0,0,0.3)`,
        animation: isCenter ? 'center-pulse 2.5s ease-in-out infinite' : `float-${rank % 3} ${2.5 + rank * 0.3}s ease-in-out infinite`,
         background: '#f1f5f9',
        flexShrink: 0,
      }}>
        <img
          src={getAvatarUrl(user.avatar, user.name)}
          alt={user.name}
          style={{
            width: '100%',
            height: '100%',
             objectFit: 'cover',
             objectPosition: 'center',
            display: 'block',
          }}
          onError={e => {
            if (!e.target.dataset.fallback) {
              e.target.dataset.fallback = '1';
              e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name || 'NV')}&background=random&color=fff&size=200&bold=true`;
            }
          }}
        />
      </div>

      {/* Score badge — OUTSIDE circle so not clipped by overflow:hidden */}
      {isCenter ? (
        <div style={{
          background: 'linear-gradient(135deg,#fbbf24,#f59e0b)',
          color: '#7c2d12', fontWeight: 900, fontSize: 13,
          padding: '3px 14px', borderRadius: 99, whiteSpace: 'nowrap',
          boxShadow: '0 2px 8px rgba(0,0,0,0.25)',
          marginTop: -4,
        }}>
          ⭐ {user.completion_time ? `${user.completion_time} • ${user.raw_count} KN` : `${score} kết nối`}
        </div>
      ) : (
        <div style={{
          background: color.bg, color: '#fff', fontWeight: 800, fontSize: 11,
          padding: '2px 10px', borderRadius: 99, whiteSpace: 'nowrap',
          boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
          marginTop: -4,
        }}>
          {user.completion_time ? `${user.completion_time} • ${user.raw_count} KN` : `${score} kết nối`}
        </div>
      )}

      {/* Name */}
      <div style={{ textAlign: 'center', maxWidth: 130 }}>
        <div style={{
          fontWeight: 800, fontSize: isCenter ? 16 : 13, color: '#fff',
          textShadow: '0 2px 8px rgba(0,0,0,0.5)',
          lineHeight: 1.2, overflow: 'hidden',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
        }}>
          {user.name}
        </div>
        {isCenter && (
          <div style={{
            marginTop: 4, background: 'linear-gradient(135deg,#f472b6,#ec4899)',
            color: '#fff', fontWeight: 700, fontSize: 11,
            padding: '2px 10px', borderRadius: 99, display: 'inline-block',
          }}>
            🏆 Kết nối nhiều nhất
          </div>
        )}
        {!isCenter && user.dept && (
          <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: 10, marginTop: 2 }}>
            {user.dept}
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Main TV Dashboard ─────────────────────────────────── */
export default function TVDashboard() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [isFinal, setIsFinal] = useState(false);
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [year, setYear] = useState(new Date().getFullYear());
  const [totalConns, setTotalConns] = useState(0);
  const [tick, setTick] = useState(0);

  const toggleMonth = () => {
    const currentMonth = new Date().getMonth() + 1;
    const currentYear = new Date().getFullYear();
    
    if (month === currentMonth && year === currentYear) {
      // Go back 1 month
      if (currentMonth === 1) {
        setMonth(12);
        setYear(currentYear - 1);
      } else {
        setMonth(currentMonth - 1);
      }
    } else {
      // Return to current month
      setMonth(currentMonth);
      setYear(currentYear);
    }
  };

  const fetchData = async () => {
    try {
      const res = await api.get(`/admin/leaderboard?month=${month}&year=${year}`);
      setIsFinal(res.data?.is_final || false);
      const entries = res.data?.entries || res.data || [];
      const arr = Array.isArray(entries) ? entries : [];
      setLeaderboard(arr);
      setTotalConns(arr.reduce((s, u) => s + (u.raw_count || 0), 0));
    } catch {}
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    const tickInterval = setInterval(() => setTick(t => t + 1), 1000);
    return () => { clearInterval(interval); clearInterval(tickInterval); };
  }, [month, year]);

  const top = leaderboard[0];
  const others = leaderboard.slice(1, 9); // up to 8 surrounding

  const now = new Date();
  const timeStr = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  return (
    <div style={{
      position: 'fixed', inset: 0, overflow: 'hidden', zIndex: 100,
      background: 'linear-gradient(160deg, #0ea5e9 0%, #38bdf8 25%, #7dd3fc 45%, #bae6fd 60%, #e0f2fe 80%, #dbeafe 100%)',
      fontFamily: "'Nunito', 'Inter', sans-serif",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

        @keyframes confetti-fall {
          0%   { transform: translateY(-20px) rotate(0deg);   opacity: 1; }
          100% { transform: translateY(110vh) rotate(720deg); opacity: 0; }
        }
        @keyframes pop-in {
          from { opacity: 0; transform: scale(0.3); }
          to   { opacity: 1; transform: scale(1); }
        }
        @keyframes center-pulse {
          0%,100% { transform: scale(1); }
          50%      { transform: scale(1.05); }
        }
        @keyframes float-0 {
          0%,100% { transform: translateY(0px); }
          50%      { transform: translateY(-8px); }
        }
        @keyframes float-1 {
          0%,100% { transform: translateY(0px); }
          50%      { transform: translateY(-12px); }
        }
        @keyframes float-2 {
          0%,100% { transform: translateY(0px); }
          50%      { transform: translateY(-6px); }
        }
        @keyframes dash-anim {
          to { stroke-dashoffset: -10; }
        }
        @keyframes glow-text {
          0%,100% { text-shadow: 0 0 20px #fbbf24, 0 0 40px #f59e0b; }
          50%      { text-shadow: 0 0 40px #fbbf24, 0 0 80px #f59e0b, 0 4px 20px rgba(0,0,0,0.3); }
        }
        @keyframes bounce-slow {
          0%,100% { transform: translateY(0); }
          50%      { transform: translateY(-6px); }
        }
        @keyframes star-spin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
        @keyframes fade-slide {
          from { opacity: 0; transform: translateX(-30px); }
          to   { opacity: 1; transform: translateX(0); }
        }
      `}</style>

      {/* Confetti */}
      <Confetti />

      {/* Decorative circles in bg */}
      {[...Array(6)].map((_, i) => (
        <div key={i} style={{
          position: 'absolute',
          width: 120 + i * 60, height: 120 + i * 60,
          borderRadius: '50%',
          border: '2px solid rgba(255,255,255,0.15)',
          top: `${10 + i * 12}%`, left: `${-5 + i * 8}%`,
          animation: `star-spin ${20 + i * 5}s linear infinite`,
          pointerEvents: 'none',
        }} />
      ))}

      {/* ── HEADER ──────────────────────────────────────── */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '8px 24px', position: 'relative', zIndex: 10,
      }}>
        {/* Left: Logo */}
        <div style={{ display: 'flex', flexDirection: 'column', animation: 'fade-slide 0.6s ease both' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <img
              src={`${import.meta.env.BASE_URL}logo.png`}
              alt="CS Bearing"
              style={{ height: 36, objectFit: 'contain', filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.2))' }}
            />
          </div>
        </div>

        {/* Center: Big Title */}
        <div style={{ textAlign: 'center', flex: 1 }}>
          <div style={{
            fontWeight: 900, letterSpacing: '-0.02em', lineHeight: 1,
            fontSize: 'clamp(40px, 7vw, 80px)',
            background: 'linear-gradient(90deg, #1e40af, #7c3aed, #db2777, #dc2626, #d97706)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.15))',
            fontFamily: "'Nunito', sans-serif",
          }}>
            Who Is Who?
          </div>
          {/* Sub banner */}
          <div style={{
            marginTop: 8, display: 'inline-flex', alignItems: 'center', gap: 8,
            background: 'linear-gradient(135deg, #fbbf24, #f59e0b)',
            borderRadius: 99, padding: '6px 20px',
            boxShadow: '0 4px 16px rgba(245,158,11,0.4)',
            animation: 'bounce-slow 2s ease-in-out infinite',
          }}>
            <span style={{ fontSize: 18 }}>🏆</span>
            <span style={{ fontWeight: 800, fontSize: 13, color: '#7c2d12', letterSpacing: '0.03em' }}>
              VINH DANH NEWCOMER – KẾT NỐI ĐỂ TỎA SÁNG
            </span>
            <span style={{ fontSize: 18 }}>⭐</span>
          </div>
        </div>

        {/* Right: Stats box */}
        <div style={{
          background: 'rgba(255,255,255,0.85)', backdropFilter: 'blur(12px)',
          borderRadius: 20, padding: '14px 20px', textAlign: 'center',
          boxShadow: '0 8px 32px rgba(0,0,0,0.12)', border: '2px solid rgba(255,255,255,0.9)',
          minWidth: 160,
        }}>
          <div style={{ fontSize: 28, marginBottom: 4 }}>🤝</div>
          <div style={{ fontWeight: 900, fontSize: 32, color: '#1e40af',
            animation: 'glow-text 2s ease-in-out infinite' }}>
            {totalConns}
          </div>
          <div style={{ fontWeight: 700, fontSize: 11, color: '#475569', lineHeight: 1.3 }}>
            SỐ LƯỢT<br />KẾT NỐI<br />THÀNH CÔNG
          </div>
          <div style={{ marginTop: 6, fontSize: 10, color: '#94a3b8' }}>
            🕐 {timeStr}
          </div>
        </div>
      </div>

      {/* ── NETWORK VISUALIZATION ─────────────────────── */}
      <div style={{
        position: 'relative', flex: 1, zIndex: 5,
        height: 'calc(100vh - 120px)',
        margin: '0 12px',
        overflow: 'visible',
      }}>
        {leaderboard.length === 0 ? (
          <div style={{
            height: '100%', display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center', gap: 20,
          }}>
            <div style={{ fontSize: 80 }}>🎯</div>
            <div style={{ fontWeight: 900, fontSize: 32, color: '#1e3a8a', textAlign: 'center' }}>
              Chưa có dữ liệu tháng {String(month).padStart(2,'0')}/{year}
            </div>
            <div style={{ fontWeight: 600, fontSize: 16, color: '#475569' }}>
              Bảng xếp hạng sẽ cập nhật khi có người kết nối 🚀
            </div>
          </div>
        ) : (
          <>
            {/* SVG Lines */}
            <NetworkLines count={others.length} />

            {/* Center bubble */}
            {top && (
              <div style={{
                position: 'absolute', top: '32%', left: '50%',
                transform: 'translate(-50%, -50%)',
                zIndex: 10,
              }}>
                <AvatarBubble
                  user={top} isCenter rank={0}
                  color={{ bg: 'linear-gradient(135deg,#3b82f6,#1d4ed8)', shadow: '#3b82f680', ring: '#dbeafe' }}
                  size={130}
                />
              </div>
            )}

            {/* Orbit bubbles */}
            {others.map((user, i) => {
              const pos = ORBIT_POSITIONS[i];
              if (!pos) return null;
              const color = BUBBLE_COLORS[i % BUBBLE_COLORS.length];
              return (
                <div key={user.id} style={{
                  position: 'absolute',
                  top: pos.top, left: pos.left,
                  transform: 'translate(-50%, -50%)',
                  zIndex: 8,
                }}>
                  <AvatarBubble user={user} color={color} size={76} rank={i + 1} />
                </div>
              );
            })}
          </>
        )}
      </div>

      {/* ── FOOTER BAR ─────────────────────────────────── */}
      <div style={{
        position: 'fixed', bottom: 0, left: 0, right: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '10px 24px', zIndex: 20,
        background: 'linear-gradient(to top, rgba(14,165,233,0.5) 0%, transparent 100%)',
      }}>
        {/* Bottom-left motivational */}
        <div style={{
          background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(12px)',
          borderRadius: 18, padding: '10px 18px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.12)', border: '2px solid rgba(255,255,255,0.9)',
          display: 'flex', alignItems: 'center', gap: 10,
          animation: 'fade-slide 1s ease 0.5s both',
        }}>
          <div style={{ fontSize: 28 }}>👥❤️</div>
          <div>
            <div style={{ fontWeight: 900, fontSize: 13, color: '#1e3a8a' }}>CÀNG KẾT NỐI –</div>
            <div style={{ fontWeight: 900, fontSize: 13, color: '#db2777' }}>CÀNG THÀNH CÔNG!</div>
          </div>
        </div>

        {/* Bottom-center month/year */}
        <button 
          onClick={toggleMonth}
          style={{
            background: 'rgba(255,255,255,0.75)', borderRadius: 99, padding: '5px 18px',
            fontWeight: 700, fontSize: 12, color: '#475569',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
            border: '2px solid rgba(255,255,255,0.5)',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}>
          {isFinal ? '🏆 Tổng kết' : '⚡ Đang diễn ra'} · Tháng {String(month).padStart(2,'0')}/{year} · 🔄 Tự động làm mới 30s (Nhấn để chuyển tháng)
        </button>

        {/* Bottom-right congrats */}
        <div style={{
          textAlign: 'right',
          animation: 'fade-slide 1s ease 0.8s both',
          background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(12px)',
          borderRadius: 18, padding: '10px 18px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.12)', border: '2px solid rgba(255,255,255,0.9)',
        }}>
          <div style={{
            fontWeight: 900, fontSize: 'clamp(18px, 2.5vw, 28px)',
            color: '#dc2626', fontStyle: 'italic',
            textShadow: '0 2px 8px rgba(255,255,255,0.8)',
            lineHeight: 1.1,
          }}>
            Congrats!
          </div>
          <div style={{ fontWeight: 800, fontSize: 13, color: '#1e40af' }}>
            TO OUR TOP CONNECTORS! 🎁⭐
          </div>
        </div>
      </div>
    </div>
  );
}
