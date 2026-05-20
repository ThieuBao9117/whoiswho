# PostgreSQL Quick Reference Card

> CSB Connection - Tối ưu cho PostgreSQL

---

## 🎯 Tối Ưu PostgreSQL Đã Áp Dụng

### 1. UUID Primary Keys
```python
# Thay vì Integer
id = Column(Integer, primary_key=True)  # ❌ Old

# Dùng UUID
from sqlalchemy.dialects.postgresql import UUID
import uuid
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # ✅ New
```

**Lợi ích:**
- 🔒 Bảo mật cao hơn (không đoán được ID)
- 🌐 Phân tán dễ dàng (multiple databases)
- 📈 Scalable cho distributed systems

### 2. JSONB Columns
```python
# Thay vì JSON
from sqlalchemy import Column, JSON
connections_by_dept = Column(JSON)  # ❌ Old

# Dùng JSONB (PostgreSQL)
from sqlalchemy.dialects.postgresql import JSONB
connections_by_dept = Column(JSONB)  # ✅ New
```

**Lợi ích:**
- ⚡ Query nhanh hơn (indexed)
- 🔍 Hỗ trợ operators: `?`, `@>`, `<@`
- 💾 Lưu trữ nhị phân hiệu quả

### 3. TIMESTAMPTZ
```python
# Thay vì TIMESTAMP
created_at = Column(DateTime)  # ❌ Old

# Dùng TIMESTAMPTZ
created_at = Column(DateTime(timezone=True))  # ✅ New
```

**Lợi ích:**
- 🌍 Tự động chuyển timezone
- 📅 Lưu trữ UTC + offset
- ⏰ Tránh nhầm lẫn DST

### 4. PostgreSQL ENUM Types
```python
# Thay vì String
status = Column(String(32))  # ❌ Old

# Dùng ENUM
from sqlalchemy.dialects.postgresql import ENUM
import enum

class RewardStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    FAILED = "FAILED"

status = Column(Enum(RewardStatus))  # ✅ New
```

**Lợi ích:**
- ✅ Validation tự động
- 📏 Type-safe
- 🚀 Performance tốt hơn

### 5. Connection Pooling
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Tối đa 20 connections
    max_overflow=10,        # Thêm 10 khi cao điểm
    pool_timeout=30,        # Timeout 30s
    pool_recycle=1800,      # Recycle mỗi 30 phút
)
```

---

## 📊 Index Strategy

### Unique Indexes
```sql
-- Prevent duplicates
idx_hrm_employee_id (UNIQUE)
idx_emp_code (UNIQUE)
idx_username (UNIQUE)
idx_target_type_period (UNIQUE)
idx_connection_pair (UNIQUE)
idx_snapshot_month (UNIQUE)
```

### Performance Indexes
```sql
-- Filter queries
idx_status
idx_department
idx_is_active
idx_last_synced

-- Composite queries
idx_connection_pair (new_hire_id, connector_id)
idx_reward_employee_target (employee_id, target_id)
idx_audit_table_record (table_name, record_id)
```

---

## 🔍 JSONB Query Examples

### Query trong JSONB
```sql
-- Get specific key
SELECT connections_by_dept->>'IT' FROM crw_progress_snapshots;

-- Check if key exists
SELECT * FROM crw_progress_snapshots 
WHERE connections_by_dept ? 'IT';

-- Contains operator
SELECT * FROM crw_progress_snapshots 
WHERE connections_by_dept @> '{"IT": 10}';
```

### Update JSONB
```sql
-- Update specific key
UPDATE crw_progress_snapshots
SET connections_by_dept = jsonb_set(
    connections_by_dept,
    '{IT}',
    '15'
)
WHERE snapshot_month = '2026-04';
```

---

## 🛡️ Migration Safety

### Before Migrate
```bash
# 1. Backup database
pg_dump -U csb_user -d csb_db > backup_$(date +%Y%m%d).sql

# 2. Check what will change
alembic upgrade head --sql

# 3. Test on local first
docker-compose up -d csb_db
alembic upgrade head
```

### During Migration
```bash
# Run migration
alembic upgrade head

# Verify
alembic current
psql -U csb_user -d csb_db -c "\dt"
```

### Rollback if Failed
```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade 001_initial

# Restore from backup
psql -U csb_user -d csb_db < backup_20260413.sql
```

---

## 📈 Performance Tips

### 1. EXPLAIN ANALYZE
```sql
-- Check query performance
EXPLAIN ANALYZE
SELECT * FROM crw_connections
WHERE new_hire_id = 'uuid-here';
```

### 2. Vacuum & Analyze
```sql
-- Update statistics
ANALYZE csb_employee_refs;

-- Reclaim storage
VACUUM ANALYZE csb_employee_refs;
```

### 3. Monitor Connections
```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity 
WHERE datname = 'csb_db';

-- Long running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;
```

---

## 🚨 Common Issues

### Issue: UUID Generation
```sql
-- Enable uuid-ossp extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Test UUID generation
SELECT gen_random_uuid();
```

### Issue: Timezone Mismatch
```sql
-- Check database timezone
SHOW timezone;

-- Set to UTC
SET timezone = 'UTC';
```

### Issue: JSONB Errors
```sql
-- Validate JSON
SELECT connections_by_dept IS JSON 
FROM crw_progress_snapshots;

-- Convert JSON to JSONB
ALTER TABLE table_name 
ALTER COLUMN column_name TYPE JSONB 
USING column_name::JSONB;
```

---

## 🔗 Useful Commands

### psql Shortcuts
```bash
# Connect
psql -h localhost -p 5433 -U csb_user -d csb_db

# List tables
\dt

# Describe table
\d table_name

# List indexes
\di

# Show query plan
EXPLAIN SELECT * FROM table_name;

# Export to CSV
\copy (SELECT * FROM table_name) TO 'output.csv' CSV HEADER
```

### Docker Commands
```bash
# View logs
docker logs csb-db -f

# Execute psql
docker exec -it csb-db psql -U csb_user -d csb_db

# Backup
docker exec csb-db pg_dump -U csb_user csb_db > backup.sql

# Restore
docker exec -i csb-db psql -U csb_user csb_db < backup.sql

# Reset (DELETE ALL DATA)
docker-compose down -v csb_db
docker-compose up -d csb_db
```

---

## 📚 Resources

- [PostgreSQL UUID](https://www.postgresql.org/docs/current/datatype-uuid.html)
- [JSONB Functions](https://www.postgresql.org/docs/current/functions-json.html)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy PostgreSQL](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
