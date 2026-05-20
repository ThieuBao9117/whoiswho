import React, { useState, useEffect } from 'react';
import { UserCheck, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../../services/api';

export default function AdminConnections() {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchIncoming(); }, []);

  const fetchIncoming = async () => {
    try { const res = await api.get('/connections/incoming'); setConnections(res.data); }
    catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleAction = async (id, accept) => {
    try {
      await api.put(`/connections/${id}?accept=${accept}`);
      toast.success(accept ? "Đã chấp nhận kết nối" : "Đã từ chối kết nối");
      fetchIncoming();
    } catch { toast.error("Thao tác thất bại"); }
  };

  return (
    <div className="p-5 md:p-8 flex-1 animate-fade-in">
      <h1 className="text-2xl font-heading font-bold text-surface-800 mb-6">Yêu cầu kết nối</h1>
      <div className="card overflow-hidden">
        {loading ? (
          <div className="py-16 flex justify-center"><div className="w-10 h-10 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div>
        ) : (
          <div className="overflow-x-auto">
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
                        <img src={c.new_hire.photo || `https://i.pravatar.cc/150?u=${c.new_hire.id}`} className="w-10 h-10 rounded-full border border-surface-200" alt="" />
                        <div>
                          <div className="font-semibold text-surface-800">{c.new_hire.full_name}</div>
                          <div className="text-xs text-surface-400">{c.new_hire.emp_code} • {c.new_hire.department}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-5 text-center">
                      <span className="badge badge-accent">Chờ duyệt</span>
                    </td>
                    <td className="py-4 px-5 text-right">
                      <div className="flex justify-end gap-2">
                        <button onClick={() => handleAction(c.id, false)} className="btn-danger text-xs px-3 py-1.5">Từ chối</button>
                        <button onClick={() => handleAction(c.id, true)} className="btn-success text-xs px-3 py-1.5">Chấp nhận</button>
                      </div>
                    </td>
                  </tr>
                )) : (
                  <tr><td colSpan="3" className="py-16 text-center text-surface-400">Không có yêu cầu nào</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
