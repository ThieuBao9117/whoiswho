import React, { useState, useEffect } from 'react';
import { Trophy } from 'lucide-react';
import api from '../services/api';

function RoleBadge({ isOperator }) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 3,
      background: isOperator
        ? 'rgba(59,130,246,0.15)' : 'rgba(139,92,246,0.15)',
      color: isOperator ? '#1d4ed8' : '#6d28d9',
      borderRadius: 999, padding: '3px 10px',
      fontSize: 11, fontWeight: 700,
    }}>
      {isOperator ? '🔧 Operator' : '💼 Staff'}
    </span>
  );
}

export default function TVDashboard() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [year, setYear] = useState(new Date().getFullYear());

  const fetchData = async () => {
    try {
      const res = await api.get(`/admin/leaderboard?month=${month}&year=${year}`);
      const entries = res.data?.entries || res.data || [];
      setLeaderboard(Array.isArray(entries) ? entries : []);
    } catch {}
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [month, year]);

  return (
    <div style={{
      position: 'fixed', inset: 0, overflow: 'hidden',
      background: 'linear-gradient(135deg,#0f172a 0%,#1e1b4b 50%,#0c1445 100%)',
      display: 'flex', flexDirection: 'column', zIndex: 100,
    }}>
      <style>{`
        @keyframes shimmer {
          0%,100% { opacity: 1; } 50% { opacity: 0.7; }
        }
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(20px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes crown-glow {
          0%,100% { box-shadow: 0 0 30px rgba(245,158,11,0.5), 0 0 60px rgba(245,158,11,0.2); }
          50%      { box-shadow: 0 0 50px rgba(245,158,11,0.8), 0 0 100px rgba(245,158,11,0.4); }
        }
      `}</style>

      {/* Header */}
      <div style={{
        padding: '24px 40px',
        borderBottom: '1px solid rgba(255,255,255,0.08)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        background: 'rgba(255,255,255,0.04)', backdropFilter: 'blur(12px)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 18 }}>
          <div style={{
            width: 60, height: 60, borderRadius: 18,
            background: 'linear-gradient(135deg,#f59e0b,#d97706)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 8px 24px rgba(245,158,11,0.4)',
          }}>
            <Trophy style={{ width: 30, height: 30, color: 'white' }} />
          </div>
          <div>
            <h1 style={{ fontWeight: 800, fontSize: 32, color: 'white', margin: 0, letterSpacing: '-0.02em' }}>
              CSB Connection
            </h1>
            <p style={{ color: 'rgba(255,255,255,0.55)', fontSize: 16, margin: '4px 0 0', fontWeight: 500 }}>
              🏆 Bảng Xếp Hạng Kết Nối — Tháng {String(month).padStart(2, '0')}/{year}
            </p>
          </div>
        </div>
        <div style={{
          background: 'rgba(255,255,255,0.08)', borderRadius: 14, padding: '10px 18px',
          color: 'rgba(255,255,255,0.6)', fontSize: 13, fontWeight: 500,
        }}>
          🔄 Cập nhật mỗi 30 giây
        </div>
      </div>

      {/* Body */}
      <div style={{ flex: 1, padding: '32px 40px', overflowY: 'auto' }}>
        {leaderboard.length > 0 ? (
          <div style={{ display: 'grid', gap: 16 }}>
            {leaderboard.map((user, idx) => {
              const isFirst = idx === 0;
              const medals = ['🥇', '🥈', '🥉'];
              return (
                <div key={user.id} style={{
                  display: 'flex', alignItems: 'center', gap: 20,
                  background: isFirst
                    ? 'linear-gradient(135deg,rgba(245,158,11,0.2),rgba(251,191,36,0.08))'
                    : 'rgba(255,255,255,0.05)',
                  border: isFirst ? '1.5px solid rgba(245,158,11,0.5)' : '1px solid rgba(255,255,255,0.08)',
                  borderRadius: isFirst ? 24 : 18,
                  padding: isFirst ? '24px 28px' : '16px 24px',
                  backdropFilter: 'blur(8px)',
                  animation: `slideIn 0.5s ease ${idx * 0.06}s both`,
                  boxShadow: isFirst ? '0 0 40px rgba(245,158,11,0.15)' : undefined,
                  transition: 'transform 0.2s',
                }}>
                  {/* Rank */}
                  <div style={{
                    width: isFirst ? 56 : 44, height: isFirst ? 56 : 44, borderRadius: '50%', flexShrink: 0,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: isFirst ? 28 : 20,
                    background: isFirst
                      ? 'linear-gradient(135deg,#fbbf24,#f59e0b)'
                      : idx === 1 ? 'linear-gradient(135deg,#d1d5db,#9ca3af)'
                      : idx === 2 ? 'linear-gradient(135deg,#fb923c,#ea580c)'
                      : 'rgba(255,255,255,0.12)',
                    animation: isFirst ? 'crown-glow 2s ease-in-out infinite' : undefined,
                  }}>
                    {idx < 3 ? medals[idx] : <span style={{ color: 'rgba(255,255,255,0.5)', fontWeight: 700, fontSize: 16 }}>{idx + 1}</span>}
                  </div>

                  {/* Avatar */}
                  <img
                    src={user.avatar || `https://i.pravatar.cc/80?u=${user.id}`}
                    alt=""
                    style={{
                      width: isFirst ? 72 : 52, height: isFirst ? 72 : 52,
                      borderRadius: '50%', objectFit: 'cover', flexShrink: 0,
                      border: isFirst ? '3px solid #f59e0b' : '2px solid rgba(255,255,255,0.15)',
                    }}
                  />

                  {/* Name + Dept + Role */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h3 style={{
                      fontWeight: 800, color: 'white', margin: 0,
                      fontSize: isFirst ? 28 : 18, letterSpacing: '-0.01em',
                      overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                    }}>{user.name}</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 6 }}>
                      <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: 13 }}>{user.dept}</span>
                      <RoleBadge isOperator={user.is_operator} />
                    </div>
                  </div>

                  {/* Completion */}
                  <div style={{
                    flexShrink: 0, textAlign: 'right',
                    background: 'rgba(255,255,255,0.07)', borderRadius: 16,
                    padding: isFirst ? '16px 24px' : '10px 18px',
                    border: '1px solid rgba(255,255,255,0.1)',
                    minWidth: 140,
                  }}>
                    <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
                      Hoàn thành
                    </div>
                    <div style={{
                      fontWeight: 800, color: isFirst ? '#fbbf24' : '#38bdf8',
                      fontSize: isFirst ? 26 : 20,
                    }}>
                      {user.days_to_complete !== undefined ? `${user.days_to_complete} ngày` : user.score}
                    </div>
                    {user.win_date && (
                      <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: 11, marginTop: 2 }}>
                        {user.win_date}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 20, color: 'rgba(255,255,255,0.3)' }}>
            <Trophy style={{ width: 96, height: 96, opacity: 0.2 }} />
            <h2 style={{ fontWeight: 700, fontSize: 28, color: 'rgba(255,255,255,0.35)' }}>Chưa có dữ liệu xếp hạng</h2>
            <p style={{ fontSize: 16, color: 'rgba(255,255,255,0.2)' }}>
              Bảng xếp hạng tháng {String(month).padStart(2,'0')}/{year} sẽ cập nhật khi có người hoàn thành.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
