import sqlite3
import datetime

DB_PATH = "backend/connectreward.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"Initializing database at {DB_PATH}...")

    # Create auth_user table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS auth_user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        password VARCHAR(128),
        last_login DATETIME,
        is_superuser BOOLEAN DEFAULT 0,
        username VARCHAR(150) UNIQUE,
        first_name VARCHAR(150),
        last_name VARCHAR(150),
        email VARCHAR(254),
        is_staff BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        date_joined DATETIME
    )
    ''')

    # Create hr_employee table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hr_employee (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_code VARCHAR(32) UNIQUE,
        full_name VARCHAR(120),
        department VARCHAR(120),
        part VARCHAR(120),
        role VARCHAR(120),
        status VARCHAR(32) DEFAULT 'Active',
        join_date DATE,
        user_id INTEGER,
        photo VARCHAR(100),
        FOREIGN KEY (user_id) REFERENCES auth_user (id)
    )
    ''')

    # Create crw_targets table (Plural to match SQLAlchemy)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crw_targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_type VARCHAR(20) DEFAULT 'WEEK',
        period_str VARCHAR(10) UNIQUE,
        operator_required INTEGER DEFAULT 5,
        leader_required INTEGER DEFAULT 2,
        pl_required INTEGER DEFAULT 1,
        tm_required INTEGER DEFAULT 1,
        gd_required INTEGER DEFAULT 0,
        reward_amount FLOAT DEFAULT 500000.0,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create crw_connections table (Missing table causing 500 error)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crw_connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        new_hire_id INTEGER NOT NULL,
        connector_id INTEGER NOT NULL,
        status VARCHAR(20) DEFAULT 'PENDING',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        responded_at DATETIME,
        FOREIGN KEY (new_hire_id) REFERENCES hr_employee (id),
        FOREIGN KEY (connector_id) REFERENCES hr_employee (id)
    )
    ''')

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # Insert Admin
    try:
        cursor.execute('''
        INSERT INTO auth_user (username, password, is_staff, is_superuser, is_active, date_joined)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ("admin", "admin123", 1, 1, 1, now))
        admin_id = cursor.lastrowid
        
        cursor.execute('''
        INSERT INTO hr_employee (emp_code, full_name, department, role, join_date, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ("ADM-001", "Quản Trị Viên (HR)", "HR Dept", "HR Manager", today, admin_id))
        print("Done: admin / admin123")
    except sqlite3.IntegrityError:
        print("Admin user already exists.")

    # Insert Demo Users
    demo_users = [
        ("user", "user123", "EMP-001", "Minh Trần", "Sản xuất", "Operator"),
        ("user1", "123123", "EMP-002", "Hải Nam", "Sản xuất", "Operator"),
        ("user2", "123123", "EMP-003", "Thu Trang", "Sản xuất", "Leader"),
        ("user3", "123123", "EMP-004", "Quốc Bảo", "Kỹ thuật", "Part Leader"),
        ("user4", "123123", "EMP-005", "Thị Lan", "Sản xuất", "Team Manager"),
        ("user5", "123123", "EMP-006", "Văn Dũng", "Giám Đốc", "GD"),
    ]

    for username, password, emp_code, full_name, dept, role in demo_users:
        try:
            cursor.execute('''
            INSERT INTO auth_user (username, password, is_staff, is_superuser, is_active, date_joined)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password, 0, 0, 1, now))
            u_id = cursor.lastrowid
            
            cursor.execute('''
            INSERT INTO hr_employee (emp_code, full_name, department, role, join_date, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (emp_code, full_name, dept, role, today, u_id))
            print(f"Done: {username} / {password} - {full_name}")
        except sqlite3.IntegrityError:
            print(f"User {username} already exists.")

    # Insert some mentors for Search demo
    mentors = [
        ("MNT-001", "Nguyễn Văn A", "Leader", "Sản xuất"),
        ("MNT-002", "Lê Văn B", "Part Leader", "Kỹ thuật"),
        ("MNT-003", "Trần Thị C", "Team Manager", "Sản xuất"),
        ("MNT-004", "Phạm Văn D", "GD", "Giám Đốc"),
    ]
    for code, name, role, dept in mentors:
        try:
            cursor.execute('''
            INSERT INTO hr_employee (emp_code, full_name, role, department, join_date)
            VALUES (?, ?, ?, ?, ?)
            ''', (code, name, role, dept, "2025-01-01"))
        except sqlite3.IntegrityError:
            pass

    # Target for current month
    period = datetime.datetime.now().strftime("%Y-%m")
    try:
        cursor.execute('''
        INSERT INTO crw_targets (period_str, reward_amount) VALUES (?, ?)
        ''', (period, 500000.0))
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
