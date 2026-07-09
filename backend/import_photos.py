import os
import shutil
import re
from sqlalchemy import create_engine, text

# Cau hinh
SOURCE_PHOTO_DIR = r"C:\WHO\csbwhoiswho\Photo"
DEST_PHOTO_DIR = r"C:\WHO\csbwhoiswho\frontend\public\avatars"
# Trong backend, ta se cap nhat URL truc tiep tro den /game/avatars/
# URL nay can khop voi cau hinh frontend
DB_URL = "postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/csb_db"

def main():
    print("=== START IMPORT PHOTOS ===")
    
    # 1. Tao thu muc dich
    if not os.path.exists(DEST_PHOTO_DIR):
        os.makedirs(DEST_PHOTO_DIR)
        print(f"Da tao thu muc dich: {DEST_PHOTO_DIR}")

    # 2. Ket noi DB
    engine = create_engine(DB_URL)
    
    success_count = 0
    not_found_in_db = 0
    failed_parse = 0
    
    try:
        with engine.begin() as conn:
            # 3. Quet tat ca file trong thu muc Photo
            files = [f for f in os.listdir(SOURCE_PHOTO_DIR) if f.lower().endswith(('.jpeg', '.jpg', '.png'))]
            print(f"Tim thay {len(files)} file hinh anh.")
            
            for filename in files:
                # Dinh dang file: HOÀNG THỊ+PHƯƠNG HUYỀN_V0250411.jpeg hoac tuong tu
                # Phan truoc .jpeg va sau dau _ cuoi cung la emp_code
                match = re.search(r'_([A-Za-z0-9]+)\.(jpeg|jpg|png)$', filename, re.IGNORECASE)
                if not match:
                    print(f"[!] Bo qua (khong the parse emp_code): {filename}")
                    failed_parse += 1
                    continue
                
                emp_code = match.group(1).upper()
                ext = match.group(2).lower()
                
                # 4. Kiem tra nhan vien co trong DB khong
                result = conn.execute(text("SELECT id FROM csb_employee_refs WHERE emp_code = :emp_code"), {"emp_code": emp_code}).fetchone()
                
                if not result:
                    # Nhan vien khong ton tai trong DB CSB
                    not_found_in_db += 1
                    continue
                
                # 5. Copy file sang thu muc dich voi ten chuan (VD: V0250411.jpeg)
                new_filename = f"{emp_code}.{ext}"
                src_path = os.path.join(SOURCE_PHOTO_DIR, filename)
                dst_path = os.path.join(DEST_PHOTO_DIR, new_filename)
                
                shutil.copy2(src_path, dst_path)
                
                # 6. Cap nhat duong dan photo vao DB
                # Vi production dang host tren IIS tai folder /game/,
                # Neu upload len /game/avatars/... thi url la /game/avatars/...
                photo_url = f"/game/avatars/{new_filename}"
                
                conn.execute(
                    text("UPDATE csb_employee_refs SET photo = :photo_url WHERE emp_code = :emp_code"),
                    {"photo_url": photo_url, "emp_code": emp_code}
                )
                success_count += 1
                
        print("\n=== TONG KET ===")
        print(f"Tong so file: {len(files)}")
        print(f"Thanh cong cap nhat DB & copy: {success_count}")
        print(f"Nhan vien khong co trong DB: {not_found_in_db}")
        print(f"File loi dinh dang ten: {failed_parse}")
        
    except Exception as e:
        print(f"Loi: {e}")

if __name__ == "__main__":
    main()
