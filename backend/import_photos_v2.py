import os
import shutil
import re
from sqlalchemy import create_engine, text
from unidecode import unidecode

SOURCE_PHOTO_DIR = r"C:\WHO\csbwhoiswho\Photo"
DEST_PHOTO_DIR = r"C:\WHO\csbwhoiswho\frontend\public\avatars"
DB_URL = "postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/csb_db"

def clean_string(s):
    if not s:
        return ""
    # remove accents, lowercase, remove spaces and plus signs
    return unidecode(s).lower().replace(" ", "").replace("+", "")

def main():
    print("=== START IMPORT PHOTOS V2 (NAME MATCHING) ===")
    
    if not os.path.exists(DEST_PHOTO_DIR):
        os.makedirs(DEST_PHOTO_DIR)

    engine = create_engine(DB_URL)
    
    with engine.begin() as conn:
        # Load all employees from DB
        db_emps = conn.execute(text("SELECT id, emp_code, full_name FROM csb_employee_refs")).fetchall()
        
        # Create dictionaries for fast lookup
        # by emp_code
        emps_by_code = {emp.emp_code.upper(): emp for emp in db_emps}
        # by clean_name
        emps_by_name = {}
        for emp in db_emps:
            cname = clean_string(emp.full_name)
            if cname not in emps_by_name:
                emps_by_name[cname] = []
            emps_by_name[cname].append(emp)
            
        # Reset all photos in DB to NULL to start fresh
        conn.execute(text("UPDATE csb_employee_refs SET photo = NULL"))
        
        files = [f for f in os.listdir(SOURCE_PHOTO_DIR) if f.lower().endswith(('.jpeg', '.jpg', '.png'))]
        
        success_count = 0
        name_matched = 0
        code_matched = 0
        not_found = 0
        
        for filename in files:
            # Format is usually: NAME_EMPCODE.ext
            # E.g. "BUI+VU LAM_V0260310.jpeg" or "Thị Trinh+Trịnh_V0200401.jpeg"
            match = re.search(r'^(.*)_([A-Za-z0-9]+)\.(jpeg|jpg|png)$', filename, re.IGNORECASE)
            if not match:
                continue
                
            file_name_part = match.group(1)
            file_code_part = match.group(2).upper()
            ext = match.group(3).lower()
            
            cname = clean_string(file_name_part)
            
            matched_emp = None
            
            # 1. Try to match by name
            if cname in emps_by_name:
                matches = emps_by_name[cname]
                if len(matches) == 1:
                    matched_emp = matches[0]
                    name_matched += 1
                else:
                    # Multiple people with same name, tie-break with emp_code
                    for m in matches:
                        if m.emp_code.upper() == file_code_part:
                            matched_emp = m
                            name_matched += 1
                            break
                    if not matched_emp:
                        matched_emp = matches[0] # Just pick first if code doesn't match either
                        name_matched += 1
            
            # 2. If name doesn't match, fallback to exact emp_code match
            if not matched_emp and file_code_part in emps_by_code:
                matched_emp = emps_by_code[file_code_part]
                code_matched += 1
                
            if matched_emp:
                db_code = matched_emp.emp_code
                new_filename = f"{db_code}.{ext}"
                src_path = os.path.join(SOURCE_PHOTO_DIR, filename)
                dst_path = os.path.join(DEST_PHOTO_DIR, new_filename)
                
                shutil.copy2(src_path, dst_path)
                
                photo_url = f"/game/avatars/{new_filename}"
                conn.execute(
                    text("UPDATE csb_employee_refs SET photo = :photo_url WHERE id = :id"),
                    {"photo_url": photo_url, "id": matched_emp.id}
                )
                success_count += 1
            else:
                not_found += 1
                
        print(f"Total files: {len(files)}")
        print(f"Matched by name: {name_matched}")
        print(f"Matched by code (fallback): {code_matched}")
        print(f"Total Success: {success_count}")
        print(f"Not found in DB: {not_found}")

if __name__ == "__main__":
    main()
