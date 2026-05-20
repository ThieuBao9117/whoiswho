import React, { useState, useEffect } from 'react';
import { Trophy, Calendar, Users, Lock, ChevronLeft, ChevronRight } from 'lucide-react';
import api from '../services/api';

// ─── Helpers ─────────────────────────────────────────────────────────────────

function isLeaderboardDay() {
  const today = new Date();
  return today.getDate() === 30;
}

function getRankStyle(rank) {
  if (rank === 1) return { bg: 'bg-amber-400', text: 'text-white', shadow: 'shadow-amber-200' };
  if (rank === 2) return { bg: 'bg-slate-300', text: 'text-white', shadow: 'shadow-slate-200' };
  if (rank === 3) return { bg: 'bg-orange-400', text: 'text-white', shadow: 'shadow-orange-200' };
  return { bg: 'bg-surface-100', text: 'text-surface-500', shadow: '' };
}

function getMedalEmoji(rank) {
  if (rank === 1) return '🥇';
  if (rank === 2) return '🥈';
  if (rank === 3) return '🥉';
  return null;
}

function RoleBadge({ isOperator }) {
  return isOperator ? (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '3px',
      background: 'linear-gradient(135deg,#3b82f6,#1d4ed8)',
      color: 'white', borderRadius: '999px', padding: '2px 10px',
      fontSize: '11px', fontWeight: 700, letterSpacing: '0.03em',
    }}>🔧 Operator</span>
  ) : (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '3px',
      background: 'linear-gradient(135deg,#8b5cf6,#6d28d9)',
      color: 'white', borderRadius: '999px', padding: '2px 10px',
      fontSize: '11px', fontWeight: 700, letterSpacing: '0.03em',
    }}>💼 Staff</span>
  );
}

// ─── Top 3 Podium ─────────────────────────────────────────────────────────────

function PodiumCard({ entry, rank }) {
  const isFirst = rank === 1;
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px',
      flex: 1, minWidth: 0,
      animation: `fadeSlideUp 0.5s ease ${(rank - 1) * 0.1}s both`,
    }}>
      {/* Avatar */}
      <div style={{ position: 'relative' }}>
        <img
          src={entry.avatar}
          alt={entry.name}
          style={{
            width: isFirst ? 88 : 72, height: isFirst ? 88 : 72,
            borderRadius: '50%', objectFit: 'cover',
            border: isFirst ? '4px solid #f59e0b' : rank === 2 ? '3px solid #9ca3af' : '3px solid #f97316',
            boxShadow: isFirst ? '0 0 20px rgba(245,158,11,0.4)' : '0 4px 12px rgba(0,0,0,0.12)',
          }}
        />
        <div style={{
          position: 'absolute', bottom: -6, right: -6,
          width: 26, height: 26, borderRadius: '50%',
          background: isFirst ? 'linear-gradient(135deg,#fbbf24,#f59e0b)' : rank === 2 ? 'linear-gradient(135deg,#d1d5db,#9ca3af)' : 'linear-gradient(135deg,#fb923c,#ea580c)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '13px', fontWeight: 700, color: 'white',
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
        }}>{rank}</div>
      </div>

      {/* Info */}
      <div style={{ textAlign: 'center', width: '100%', overflow: 'hidden' }}>
        <div style={{
          fontWeight: 700, fontSize: isFirst ? '15px' : '13px',
          color: '#1e293b', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>{entry.name}</div>
        <div style={{ fontSize: '11px', color: '#64748b', marginTop: 2 }}>{entry.dept}</div>
        <div style={{ marginTop: 4 }}><RoleBadge isOperator={entry.is_operator} /></div>
      </div>

      {/* Completion time */}
      <div style={{
        background: isFirst ? 'linear-gradient(135deg,#fef3c7,#fde68a)' : '#f1f5f9',
        border: isFirst ? '1px solid #f59e0b' : '1px solid #e2e8f0',
        borderRadius: '12px', padding: '8px 14px', textAlign: 'center',
      }}>
        <div style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Hoàn thành</div>
        <div style={{ fontWeight: 800, fontSize: isFirst ? '17px' : '14px', color: isFirst ? '#d97706' : '#0ea5e9', marginTop: 2 }}>
          {entry.days_to_complete} ngày
        </div>
      </div>

      {/* Podium base */}
      <div style={{
        width: '100%', borderRadius: '12px 12px 0 0',
        height: isFirst ? 64 : rank === 2 ? 48 : 32,
        background: isFirst
          ? 'linear-gradient(180deg,#fbbf24,#f59e0b)'
          : rank === 2 ? 'linear-gradient(180deg,#d1d5db,#9ca3af)'
          : 'linear-gradient(180deg,#fb923c,#ea580c)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: isFirst ? '26px' : '20px',
        boxShadow: '0 -4px 12px rgba(0,0,0,0.1)',
      }}>
        {getMedalEmoji(rank)}
      </div>
    </div>
  );
}

// ─── Row entry ────────────────────────────────────────────────────────────────

function LeaderboardRow({ entry }) {
  const style = getRankStyle(entry.rank);
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 14, padding: '12px 16px',
      background: 'white', borderRadius: 14, border: '1px solid #e2e8f0',
      transition: 'box-shadow 0.2s, transform 0.2s',
      animation: `fadeSlideUp 0.4s ease ${entry.rank * 0.04}s both`,
    }}
      onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.09)'; e.currentTarget.style.transform = 'translateX(4px)'; }}
      onMouseLeave={e => { e.currentTarget.style.boxShadow = ''; e.currentTarget.style.transform = ''; }}
    >
      {/* Rank */}
      <div style={{
        width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontWeight: 800, fontSize: 15,
      }} className={`${style.bg} ${style.text}`}>
        {entry.rank}
      </div>

      {/* Avatar */}
      <img src={entry.avatar} alt="" style={{ width: 42, height: 42, borderRadius: '50%', objectFit: 'cover', border: '2px solid #e2e8f0', flexShrink: 0 }} />

      {/* Name + dept + role */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 700, fontSize: 14, color: '#1e293b', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {entry.name}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 3, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 11, color: '#64748b' }}>{entry.dept}</span>
          <RoleBadge isOperator={entry.is_operator} />
        </div>
      </div>

      {/* Days + win date */}
      <div style={{ textAlign: 'right', flexShrink: 0 }}>
        <div style={{ fontWeight: 800, fontSize: 15, color: '#0ea5e9' }}>{entry.days_to_complete} ngày</div>
        <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>{entry.win_date}</div>
      </div>
    </div>
  );
}

// ─── Lock overlay (not day 30) ────────────────────────────────────────────────

function LockedOverlay({ month, year }) {
  const monthStr = String(month).padStart(2, '0');
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      padding: '64px 24px', textAlign: 'center', gap: 20,
    }}>
      <div style={{
        width: 96, height: 96, borderRadius: '50%',
        background: 'linear-gradient(135deg,#f1f5f9,#e2e8f0)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 8px 32px rgba(0,0,0,0.07)',
      }}>
        <Lock style={{ width: 40, height: 40, color: '#94a3b8' }} />
      </div>
      <div>
        <h2 style={{ fontWeight: 800, fontSize: 22, color: '#1e293b', marginBottom: 8 }}>
          Bảng Xếp Hạng Chưa Mở
        </h2>
        <p style={{ color: '#64748b', fontSize: 14, lineHeight: 1.7, maxWidth: 400 }}>
          Bảng xếp hạng tháng <strong>{monthStr}/{year}</strong> sẽ được công bố vào{' '}
          <strong>ngày 30 tháng {monthStr}</strong>.<br />
          Hãy tiếp tục kết nối để lên hạng cao nhất! 💪
        </p>
      </div>
      <div style={{
        display: 'inline-flex', alignItems: 'center', gap: 8, padding: '10px 20px',
        background: 'linear-gradient(135deg,#eff6ff,#dbeafe)', borderRadius: 12,
        border: '1px solid #bfdbfe', fontSize: 13, color: '#2563eb', fontWeight: 600,
      }}>
        <Calendar style={{ width: 16, height: 16 }} />
        Công bố ngày 30 hàng tháng
      </div>
    </div>
  );
}

// ─── Main Page ─────────────────────────────────────────────────────────────────

export default function LeaderboardPage() {
  const today = new Date();
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [year, setYear] = useState(today.getFullYear());
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all | operator | staff
  const open = isLeaderboardDay();

  useEffect(() => {
    if (!open) { setLoading(false); return; }
    setLoading(true);
    api.get(`/admin/leaderboard?month=${month}&year=${year}`)
      .then(res => {
        const entries = res.data?.entries || res.data || [];
        setData(Array.isArray(entries) ? entries : []);
      })
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [month, year, open]);

  const filtered = data.filter(e => {
    if (filter === 'operator') return e.is_operator;
    if (filter === 'staff') return !e.is_operator;
    return true;
  });

  const top3 = filtered.slice(0, 3);
  const rest = filtered.slice(3);

  const prevMonth = () => {
    if (month === 1) { setMonth(12); setYear(y => y - 1); }
    else setMonth(m => m - 1);
  };
  const nextMonth = () => {
    const now = new Date();
    if (year > now.getFullYear() || (year === now.getFullYear() && month >= now.getMonth() + 1)) return;
    if (month === 12) { setMonth(1); setYear(y => y + 1); }
    else setMonth(m => m + 1);
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: 860, margin: '0 auto', paddingBottom: 48 }}>
      <style>{`
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(18px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg,#1e3a8a 0%,#1d4ed8 50%,#0ea5e9 100%)',
        borderRadius: 24, padding: '32px 28px', marginBottom: 28, color: 'white',
        position: 'relative', overflow: 'hidden',
        boxShadow: '0 12px 40px rgba(30,58,138,0.3)',
      }}>
        <div style={{ position: 'absolute', top: -40, right: -40, opacity: 0.07, fontSize: 200 }}>🏆</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20, position: 'relative' }}>
          <div style={{ background: 'rgba(255,255,255,0.15)', borderRadius: 16, padding: 12 }}>
            <Trophy style={{ width: 32, height: 32 }} />
          </div>
          <div>
            <h1 style={{ fontWeight: 800, fontSize: 26, margin: 0 }}>Bảng Xếp Hạng Kết Nối</h1>
            <p style={{ opacity: 0.75, margin: '4px 0 0', fontSize: 14 }}>
              Công bố ngày 30 hàng tháng · Xếp hạng theo tốc độ hoàn thành
            </p>
          </div>
        </div>

        {/* Month navigation */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <button
            onClick={prevMonth}
            style={{ background: 'rgba(255,255,255,0.15)', border: 'none', borderRadius: 10, padding: '6px 10px', cursor: 'pointer', color: 'white', display: 'flex', alignItems: 'center' }}
          ><ChevronLeft style={{ width: 18, height: 18 }} /></button>
          <span style={{ fontWeight: 700, fontSize: 18, minWidth: 130, textAlign: 'center' }}>
            Tháng {String(month).padStart(2, '0')}/{year}
          </span>
          <button
            onClick={nextMonth}
            style={{ background: 'rgba(255,255,255,0.15)', border: 'none', borderRadius: 10, padding: '6px 10px', cursor: 'pointer', color: 'white', display: 'flex', alignItems: 'center' }}
          ><ChevronRight style={{ width: 18, height: 18 }} /></button>

          {/* Filter tabs */}
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
            {[
              { key: 'all', label: '🏅 Tất cả' },
              { key: 'operator', label: '🔧 Operator' },
              { key: 'staff', label: '💼 Staff' },
            ].map(f => (
              <button key={f.key} onClick={() => setFilter(f.key)} style={{
                background: filter === f.key ? 'rgba(255,255,255,0.9)' : 'rgba(255,255,255,0.15)',
                color: filter === f.key ? '#1d4ed8' : 'white',
                border: 'none', borderRadius: 10, padding: '6px 14px', cursor: 'pointer',
                fontWeight: 600, fontSize: 12, transition: 'all 0.2s',
              }}>{f.label}</button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      {!open ? (
        <div className="card" style={{ borderRadius: 20, overflow: 'hidden' }}>
          <LockedOverlay month={month} year={year} />
        </div>
      ) : loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '80px 0' }}>
          <div className="w-10 h-10 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="card" style={{ borderRadius: 20, padding: '64px 24px', textAlign: 'center' }}>
          <Trophy style={{ width: 56, height: 56, color: '#e2e8f0', margin: '0 auto 16px' }} />
          <h3 style={{ fontWeight: 700, fontSize: 18, color: '#475569', marginBottom: 8 }}>Chưa có dữ liệu</h3>
          <p style={{ color: '#94a3b8', fontSize: 14 }}>Chưa có nhân viên nào hoàn thành chỉ tiêu trong tháng {String(month).padStart(2,'0')}/{year}.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Podium */}
          {top3.length > 0 && (
            <div className="card" style={{ borderRadius: 20, padding: '28px 24px 0' }}>
              <h2 style={{ fontWeight: 800, fontSize: 16, color: '#1e293b', marginBottom: 24, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Trophy style={{ width: 20, height: 20, color: '#f59e0b' }} /> Top 3 Nhanh Nhất
              </h2>
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: 12 }}>
                {/* Reorder: 2nd | 1st | 3rd */}
                {top3[1] && <PodiumCard entry={top3[1]} rank={2} />}
                {top3[0] && <PodiumCard entry={top3[0]} rank={1} />}
                {top3[2] && <PodiumCard entry={top3[2]} rank={3} />}
              </div>
            </div>
          )}

          {/* Full list */}
          {rest.length > 0 && (
            <div>
              <h2 style={{ fontWeight: 700, fontSize: 15, color: '#475569', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Users style={{ width: 17, height: 17 }} /> Tất cả người hoàn thành ({filtered.length})
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {filtered.map(entry => <LeaderboardRow key={entry.id} entry={entry} />)}
              </div>
            </div>
          )}

          {/* Stats bar */}
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {[
              { icon: '🏆', label: 'Tổng hoàn thành', value: filtered.length },
              { icon: '🔧', label: 'Operator', value: filtered.filter(e => e.is_operator).length },
              { icon: '💼', label: 'Staff', value: filtered.filter(e => !e.is_operator).length },
              { icon: '⚡', label: 'Nhanh nhất', value: top3[0] ? `${top3[0].days_to_complete} ngày` : 'N/A' },
            ].map((s, i) => (
              <div key={i} className="card" style={{ flex: 1, minWidth: 120, borderRadius: 16, padding: '16px 18px', textAlign: 'center' }}>
                <div style={{ fontSize: 24, marginBottom: 6 }}>{s.icon}</div>
                <div style={{ fontWeight: 800, fontSize: 20, color: '#1e293b' }}>{s.value}</div>
                <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
