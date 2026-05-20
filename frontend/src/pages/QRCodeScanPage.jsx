import React, { useState, useEffect, useRef } from 'react';
import { Camera, ScanLine, X, UserPlus } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { BrowserMultiFormatReader } from '@zxing/browser';
import toast from 'react-hot-toast';
import api from '../services/api';

export default function QRCodeScanPage({ user }) {
  const [scanActive, setScanActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [manualId, setManualId] = useState('');
  const videoRef = useRef(null);

  const sendInvite = async (connectorId, connectorName = "đồng nghiệp") => {
    try {
      await api.post('/connections/invite', { connector_id: connectorId });
      toast.success(`Đã gửi yêu cầu kết nối đến ${connectorName}!`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Không thể kết nối");
    }
  };

  useEffect(() => {
    let reader = null;
    setCameraError(null);
    if (scanActive && videoRef.current) {
      const isSecure = location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1';
      if (!isSecure) { setCameraError('http_ip'); return; }

      reader = new BrowserMultiFormatReader();
      reader.decodeFromVideoDevice(null, videoRef.current, async (result, err) => {
        if (result?.text) {
          try {
            let id = result.text, name = "đồng nghiệp";
            try { const d = JSON.parse(result.text); id = d.id || d.emp_code; name = d.name || d.full_name; } catch {}
            await sendInvite(id, name);
          } catch {}
          setScanActive(false);
          reader.reset();
        }
        if (err?.name === 'NotAllowedError') setCameraError('denied');
      });
    }
    return () => { if (reader) reader.reset(); };
  }, [scanActive]);

  const handleManualConnect = async (e) => {
    e.preventDefault();
    if (!manualId.trim()) return;
    await sendInvite(manualId.trim());
    setManualId('');
  };

  const qrValue = JSON.stringify({ id: user?.profile?.id, emp_code: user?.id, name: user?.name });

  return (
    <div className="animate-fade-in max-w-md mx-auto space-y-5 pb-24">
      {/* My QR */}
      <div className="card p-6 text-center">
        <div className="mb-4">
          <img src={user?.profile?.photo || "https://i.pravatar.cc/150?u=ME"} className="w-20 h-20 rounded-full border-2 border-primary-200 mx-auto object-cover" alt="" />
        </div>
        <h2 className="text-xl font-heading font-bold text-surface-800 mb-1">{user?.name}</h2>
        <p className="text-sm text-surface-400 mb-5">{user?.id}</p>
        <div className="bg-surface-50 rounded-2xl p-5 inline-block">
          <QRCodeSVG value={qrValue} size={200} level="H" fgColor="#1e293b" />
        </div>
        <p className="text-xs text-surface-400 mt-4 px-4 leading-relaxed">
          Cho đồng nghiệp quét mã QR này để kết nối, hoặc quét mã QR của họ!
        </p>
      </div>

      {/* Scanner */}
      <div className="card p-6 text-center">
        {!scanActive ? (
          <div className="space-y-4">
            <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto">
              <Camera className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="font-heading font-bold text-lg text-surface-800">Quét mã QR</h3>
            <button onClick={() => { setScanActive(true); setCameraError(null); }}
              className="btn-primary w-full py-3.5 flex items-center justify-center gap-2">
              <ScanLine className="w-5 h-5" /> Mở camera quét QR
            </button>
            <div className="flex items-center gap-3 my-2">
              <div className="flex-1 h-px bg-surface-200" />
              <span className="text-xs text-surface-400">hoặc nhập mã thủ công</span>
              <div className="flex-1 h-px bg-surface-200" />
            </div>
            <form onSubmit={handleManualConnect} className="flex gap-2">
              <input type="text" value={manualId} onChange={e => setManualId(e.target.value)}
                placeholder="Nhập mã nhân viên..." className="input-field flex-1" />
              <button type="submit" className="btn-primary px-4">Gửi</button>
            </form>
          </div>
        ) : cameraError ? (
          <div className="space-y-4">
            <div className="w-16 h-16 bg-danger-100 rounded-2xl flex items-center justify-center mx-auto">
              <X className="w-8 h-8 text-danger-500" />
            </div>
            <h3 className="font-heading font-bold text-lg text-danger-600">
              {cameraError === 'http_ip' ? 'Không thể mở camera' : 'Camera bị chặn'}
            </h3>
            <p className="text-sm text-surface-500">
              {cameraError === 'http_ip' ? 'Camera chỉ hoạt động trên HTTPS hoặc localhost. Hãy dùng cách nhập mã thủ công.' : 'Vui lòng cho phép quyền camera trong cài đặt trình duyệt.'}
            </p>
            <button onClick={() => { setScanActive(false); setCameraError(null); }} className="btn-secondary w-full">Đóng</button>
            <form onSubmit={handleManualConnect} className="flex gap-2 mt-3">
              <input type="text" value={manualId} onChange={e => setManualId(e.target.value)}
                placeholder="Nhập mã nhân viên..." className="input-field flex-1" />
              <button type="submit" className="btn-primary px-4">Gửi</button>
            </form>
          </div>
        ) : (
          <div>
            <div className="overflow-hidden rounded-2xl border-2 border-primary-200 bg-black aspect-square relative">
              <video autoPlay muted playsInline ref={videoRef} className="w-full h-full object-cover" />
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-48 h-48 border-2 border-primary-400 rounded-2xl opacity-50" />
              </div>
            </div>
            <button onClick={() => setScanActive(false)} className="btn-danger w-full mt-4">
              Dừng quét
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
