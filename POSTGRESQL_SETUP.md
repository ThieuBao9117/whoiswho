# CSB Connection - PostgreSQL Setup Guide

> Hướng dẫn thiết lập và sử dụng PostgreSQL cho CSB Connection

---

## 📋 Tổng Quan

CSB Connection sử dụng **PostgreSQL độc lập**, tách biệt hoàn toàn với HRM Database.

| Thành Phần | HRM | CSB |
|------------|-----|-----|
| **Database** | HRM PostgreSQL | CSB PostgreSQL |
| **Port** | 5432 | 5433 |
| **Quản lý migration** | Django `manage.py migrate` | Alembic `alembic upgrade head` |
| **Primary Key** | Integer (Auto-increment) | UUID |
| **JSON Column** | JSON/JSONB | JSONB |
| **Timestamp** | TIMESTAMP | TIMESTAMPTZ |

---

## 🚀 Cài Đặt Nhanh

### 1. Khởi động PostgreSQL

```bash
# Start CSB PostgreSQL database
docker-compose up -d csb_db

# Kiểm tra status
docker-compose ps
```

### 2. Chạy Migration

```bash
cd backend

# Tạo migration (nếu có thay đổi models)
alembic revision --autogenerate -m "description"

# Chạy migration
alembic upgrade head

# Kiểm tra migration status
alembic current
```

### 3. Khởi động toàn bộ

```bash
# Start tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f backend
```

---

## 🗄️ Cấu Trúc Database

### Bảng: `csb_employee_refs`
Tham chiếu nhân viên từ HRM (sync qua API)

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `hrm_employee_id` | INT | ID từ HRM (unique) |
| `hrm_user_id` | INT | Auth user ID từ HRM |
| `emp_code` | VARCHAR(32) | Mã nhân viên |
| `username` | VARCHAR(150) | Username đăng nhập |
| `full_name` | VARCHAR(120) | Tên đầy đủ |
| `department` | VARCHAR(120) | Phòng ban |
| `part` | VARCHAR(120) | Bộ phận |
| `role` | VARCHAR(120) | Chức vụ |
| `status` | VARCHAR(32) | Active/Inactive |
| `is_active` | BOOL | Trạng thái hoạt động |
| `last_synced_at` | TIMESTAMPTZ | Lần sync cuối |

### Bảng: `crw_targets`
Chỉ tiêu kết nối theo kỳ

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `target_type` | ENUM | WEEK/MONTH/YEAR |
| `period_str` | VARCHAR(7) | "2026-03" |
| `reward_amount` | FLOAT | Số tiền thưởng |

### Bảng: `crw_connections`
Kết nối giữa nhân viên mới và người hướng dẫn

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `new_hire_id` | UUID | FK → csb_employee_refs |
| `connector_id` | UUID | FK → csb_employee_refs |
| `status` | ENUM | PENDING/ACCEPTED/REJECTED |

### Bảng: `crw_rewards`
Thưởng cho nhân viên

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `employee_id` | UUID | FK → csb_employee_refs |
| `target_id` | UUID | FK → crw_targets |
| `status` | ENUM | PENDING/APPROVED/FAILED |

### Bảng: `crw_progress_snapshots`
Thống kê hàng tháng

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `snapshot_month` | VARCHAR(7) | "2026-03" |
| `connections_by_dept` | JSONB | Thống kê theo phòng ban |

### Bảng: `csb_audit_logs`
Lịch sử thay đổi

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `table_name` | VARCHAR(50) | Bảng bị thay đổi |
| `record_id` | UUID | ID bản ghi |
| `action` | ENUM | INSERT/UPDATE/DELETE |
| `old_values` | JSONB | Giá trị cũ |
| `new_values` | JSONB | Giá trị mới |

---

## 🔄 Sync Dữ Liệu Từ HRM

### HRM Django → CSB PostgreSQL

```python
# Trong HRM Django project
import requests

CSB_BASE_URL = "http://localhost:8000"

def sync_employee_to_csb(employee):
    """Sync 1 nhân viên từ HRM → CSB"""
    payload = {
        "hrm_employee_id": employee.id,
        "hrm_user_id": employee.user_id,
        "emp_code": employee.emp_code,
        "username": employee.user.username,
        "full_name": employee.full_name,
        "department": employee.department,
        "status": employee.status,
    }
    
    response = requests.post(
        f"{CSB_BASE_URL}/api/sync/employees",
        json=payload
    )
    return response.json()


def batch_sync_all_employees():
    """Sync toàn bộ nhân viên"""
    from your_app.models import Employee
    
    employees = Employee.objects.all()
    payloads = [{
        "hrm_employee_id": emp.id,
        "username": emp.user.username,
        "full_name": emp.full_name,
        "emp_code": emp.emp_code,
        "department": emp.department,
        "status": emp.status,
    } for emp in employees]
    
    response = requests.post(
        f"{CSB_BASE_URL}/api/sync/employees/batch",
        json=payloads
    )
    return response.json()
```

### Kiểm Tra Sync Status

```bash
curl http://localhost:8000/api/sync/status
```

---

## 🛠️ Alembic Commands

```bash
# Kiểm tra migration hiện tại
alembic current

# Xem lịch sử migrations
alembic history

# Tạo migration mới (autogenerate từ models)
alembic revision --autogenerate -m "add new column"

# Chạy migration lên phiên bản mới nhất
alembic upgrade head

# Rollback 1 version
alembic downgrade -1

# Rollback về version cụ thể
alembic downgrade 001_initial

# Xem SQL sẽ chạy (dry run)
alembic upgrade head --sql
```

---

## 🔍 Truy Vấn Hữu Ích

### Kết nối PostgreSQL

```bash
# Via Docker
docker exec -it csb-db psql -U csb_user -d csb_db

# Via localhost (nếu expose port 5433)
psql -h localhost -p 5433 -U csb_user -d csb_db
```

### Kiểm Tra Tables

```sql
-- Liệt kê tables
\dt

-- Xem cấu trúc bảng
\d csb_employee_refs

-- Đếm số nhân viên đã sync
SELECT COUNT(*) FROM csb_employee_refs;

-- Xem nhân viên chưa active
SELECT emp_code, full_name, status, last_synced_at
FROM csb_employee_refs
WHERE is_active = false;

-- Xem thống kê theo phòng ban (JSONB)
SELECT 
    snapshot_month,
    connections_by_dept->>'IT' as it_connections,
    connections_by_dept->>'HR' as hr_connections
FROM crw_progress_snapshots;
```

---

## ⚠️ Lưu Ý Quan Trọng

### 1. KHÔNG Bao Giờ

- ❌ Chạy `manage.py migrate` trên CSB database
- ❌ Tạo FK từ CSB sang HRM tables
- ❌ Sửa trực tiếp `csb_employee_refs` (chỉ sync từ HRM)
- ❌ Đổi `SECRET_KEY` mà không cập nhật cả 2 hệ thống

### 2. Luôn Luôn

- ✅ Dùng Alembic cho CSB migrations
- ✅ Sync employees từ HRM trước khi dùng
- ✅ Backup database trước khi migrate
- ✅ Test migrations trên local trước

### 3. Khi Có Lỗi Sync

```bash
# Kiểm tra sync status
curl http://localhost:8000/api/sync/status

# Sync lại employee cụ thể
curl -X POST http://localhost:8000/api/sync/employees \
  -H "Content-Type: application/json" \
  -d '{"hrm_employee_id": 123, ...}'

# Reset toàn bộ và sync lại
docker-compose down -v csb_db
docker-compose up -d csb_db
alembic upgrade head
# Sau đó batch sync từ HRM
```

---

## 📊 Performance Optimization

### Indexes đã tạo

```sql
-- Employee refs
idx_hrm_employee_id (unique)
idx_emp_code (unique)
idx_username (unique)
idx_status
idx_department
idx_is_active
idx_last_synced

-- Connections
idx_connection_pair (unique composite)
idx_connection_status
idx_connection_created

-- Rewards
idx_reward_employee_target
idx_reward_status
idx_reward_achieved

-- Audit
idx_audit_table_record
idx_audit_action
idx_audit_changed_at
```

### Connection Pool

```python
# database.py đã cấu hình
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)
```

---

## 🔗 Tài Liệu Liên Quan

- `.agent/DATABASE_SEPARATION.md` - Kiến trúc tách database
- `.agent/ARCHITECTURE.md` - Tổng quan hệ thống
- `backend/app/models/` - SQLAlchemy models
