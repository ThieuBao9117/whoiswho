# HƯỚNG DẪN DEPLOY CSB Game lên 50.50.50.4/game

## Kiến trúc sau khi deploy

```
50.50.50.4 (IIS - Port 80)
├── /            → Django HRM (existing)
├── /game/       → CSB Frontend (React build files, served by IIS)
├── /game/api/   → CSB Backend (FastAPI, reverse proxy từ IIS → port 7000)
└── /media/      → Django media files (existing)
```

---

## BƯỚC 1: Build Frontend React

Chạy trên máy local (Windows):

```cmd
cd C:\WHO\csbwhoiswho\frontend
npm.cmd install
npm.cmd run build
```

Sau khi build xong, thư mục `frontend\dist\` sẽ chứa các file tĩnh.
Vì `vite.config.js` đã có `base: '/game/'`, toàn bộ assets đã đúng path.

---

## BƯỚC 2: Copy file lên server IIS

Copy toàn bộ nội dung thư mục `frontend\dist\` lên server:

**Đường dẫn đích trên server** (ví dụ):
```
C:\inetpub\wwwroot\game\
```

Hoặc nếu HRM đang dùng thư mục riêng:
```
D:\WHO\wwwroot\game\
```

Cấu trúc sau khi copy:
```
C:\inetpub\wwwroot\game\
├── index.html
├── assets\
│   ├── index-xxxxx.js
│   └── index-xxxxx.css
└── ...
```

---

## BƯỚC 3: Cấu hình IIS - Virtual Directory `/game`

### 3a. Tạo Virtual Directory hoặc Application trong IIS

1. Mở **IIS Manager**
2. Chọn site `50.50.50.4`
3. Click phải → **Add Application**
   - Alias: `game`
   - Physical path: `C:\inetpub\wwwroot\game\`
4. Click OK

### 3b. Thêm web.config cho SPA (React Router)

Tạo file `C:\inetpub\wwwroot\game\web.config`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <!-- Rewrite all routes to index.html for React Router -->
    <rewrite>
      <rules>
        <rule name="CSB Game SPA" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
            <add input="{REQUEST_URI}" pattern="^/game/api" negate="true" />
          </conditions>
          <action type="Rewrite" url="/game/index.html" />
        </rule>
      </rules>
    </rewrite>

    <!-- Cache static assets -->
    <staticContent>
      <clientCache cacheControlMode="UseMaxAge" cacheControlMaxAge="365.00:00:00" />
    </staticContent>

    <!-- Default document -->
    <defaultDocument>
      <files>
        <clear />
        <add value="index.html" />
      </files>
    </defaultDocument>
  </system.webServer>
</configuration>
```

> **Yêu cầu**: IIS cần cài module **URL Rewrite** (tải miễn phí từ Microsoft).

---

## BƯỚC 4: Cấu hình Reverse Proxy `/game/api` → Backend Port 7000

CSB Backend (FastAPI) chạy tại `http://localhost:7000`.
IIS cần forward `/game/api/*` → `http://localhost:7000/api/*`.

### 4a. Cài IIS Application Request Routing (ARR)

Tải và cài:
- **URL Rewrite**: https://www.iis.net/downloads/microsoft/url-rewrite
- **ARR 3.0**: https://www.iis.net/downloads/microsoft/application-request-routing

### 4b. Thêm rule proxy vào web.config của game

Thêm vào `web.config` phần `<rewrite><rules>`:

```xml
<!-- Proxy /game/api/* → http://localhost:7000/api/* -->
<rule name="CSB API Proxy" stopProcessing="true">
  <match url="^game/api/(.*)" />
  <action type="Rewrite" url="http://localhost:7000/api/{R:1}" />
</rule>
```

**Hoặc** nếu muốn đơn giản hơn, cấu hình tại site root `web.config` của HRM:

```xml
<rule name="CSB API Reverse Proxy" stopProcessing="true">
  <match url="^game/api/(.*)" />
  <action type="Rewrite" url="http://localhost:7000/api/{R:1}" />
  <serverVariables>
    <set name="HTTP_X_FORWARDED_HOST" value="50.50.50.4" />
  </serverVariables>
</rule>
```

---

## BƯỚC 5: Chạy CSB Backend như Windows Service

Backend FastAPI cần chạy liên tục tại port 7000.

### Option A: Dùng NSSM (Non-Sucking Service Manager)

```cmd
:: Tải NSSM: https://nssm.cc/download
:: Chạy cmd với quyền Administrator

nssm install CSBBackend "C:\WHO\csbwhoiswho\backend\venv\Scripts\uvicorn.exe"
nssm set CSBBackend AppParameters "app.main:app --host 127.0.0.1 --port 7000"
nssm set CSBBackend AppDirectory "C:\WHO\csbwhoiswho\backend"
nssm set CSBBackend AppEnvironmentExtra "CSB_DATABASE_URL=postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/csb_db" "SECRET_KEY=csb-connection-secret-2026"
nssm set CSBBackend Start SERVICE_AUTO_START
nssm start CSBBackend
```

### Option B: Tạo file .bat và dùng Task Scheduler

Tạo `C:\WHO\csbwhoiswho\backend\start_service.bat`:
```cmd
@echo off
cd /d C:\WHO\csbwhoiswho\backend
venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 7000
```

Tạo Task Scheduler chạy file này khi Windows khởi động với quyền SYSTEM.

---

## BƯỚC 6: Cập nhật CORS trong Backend

Backend cần cho phép requests từ `50.50.50.4`:

Mở `C:\WHO\csbwhoiswho\backend\app\main.py` và kiểm tra CORS origins, thêm:
```python
origins = [
    "http://50.50.50.4",
    "https://50.50.50.4",
    "http://localhost:5173",
    "http://localhost:80",
]
```

---

## BƯỚC 7: Cập nhật Frontend API URL cho Production

Tạo file `C:\WHO\csbwhoiswho\frontend\.env.production`:
```env
VITE_API_URL=/game/api
```

Rồi build lại:
```cmd
npm.cmd run build
```

---

## BƯỚC 8: Cập nhật HRM - Nút "Vào CSB Game"

Trong Django HRM, view `redirect_to_csb_game` cần redirect đến:
```python
CSB_FRONTEND_URL = "http://50.50.50.4/game"  # ← Thay localhost bằng domain thật
```

---

## Tóm tắt Checklist Deploy

- [ ] `npm.cmd run build` trên máy local
- [ ] Copy `frontend/dist/*` → `C:\inetpub\wwwroot\game\` trên server
- [ ] Tạo `web.config` với URL Rewrite rule cho SPA
- [ ] Cài IIS URL Rewrite + ARR
- [ ] Thêm rule reverse proxy `/game/api → localhost:7000`  
- [ ] Cài NSSM, tạo Windows Service cho backend FastAPI
- [ ] Kiểm tra CORS trong backend cho phép `50.50.50.4`
- [ ] Tạo `.env.production` cho frontend với `VITE_API_URL=/game/api`
- [ ] Build lại frontend và copy lại dist
- [ ] Trong Django: cập nhật `CSB_FRONTEND_URL = "http://50.50.50.4/game"`
- [ ] Test: `http://50.50.50.4/game` → giao diện game
- [ ] Test: `http://50.50.50.4/game/api/` → `{"message":"WHO Is WHO API is running"}`
- [ ] Test SSO flow: Login HRM → click nút → redirect `50.50.50.4/game/sso?token=...`
