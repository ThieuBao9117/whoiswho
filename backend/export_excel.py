import os
import sys
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.csb_employee_ref import CSBEmployeeRef
from app.models.crw_models import CRWConnection, ConnectionStatus

def get_dept(emp):
    if not emp: return "N/A"
    return (emp.part or emp.department) or "N/A"

def run_export():
    db: Session = SessionLocal()
    
    # Get all connections
    connections = db.query(CRWConnection).filter(
        CRWConnection.status == ConnectionStatus.ACCEPTED
    ).all()
    
    # Group by connector (the one who initiated or owns the connection)
    # Wait, the user is the "connector_id", who connects with the "new_hire_id" (or target)
    from collections import defaultdict
    user_connections = defaultdict(list)
    
    for conn in connections:
        user_connections[conn.connector_id].append(conn)
        
    if not user_connections:
        print("No connections found.")
        return

    wb = openpyxl.Workbook()
    # Remove default sheet
    default_sheet = wb.active
    wb.remove(default_sheet)
    
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)

    # Process each user
    for user_id, conns in user_connections.items():
        user = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == user_id).first()
        if not user: continue
        
        # Safe sheet name (max 31 chars, no special chars)
        sheet_name = (user.full_name or user.emp_code)[:31].replace(":", "").replace("\\", "").replace("/", "").replace("?", "").replace("*", "").replace("[", "").replace("]", "")
        
        # Check for duplicate sheet names
        original_sheet_name = sheet_name
        counter = 1
        while sheet_name in wb.sheetnames:
            sheet_name = f"{original_sheet_name[:28]}_{counter}"
            counter += 1
            
        ws = wb.create_sheet(title=sheet_name)
        
        # Write title
        ws.append(["Danh sách kết nối của:", user.full_name, f"({user.emp_code})", get_dept(user)])
        ws.append([]) # Empty row
        
        headers = ["STT", "Tên người được kết nối", "Mã NV", "Phòng ban / Bộ phận", "Chức vụ", "Thời gian kết nối"]
        ws.append(headers)
        
        for cell in ws[3]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
            
        # Write connections
        # Sort by responded_at
        conns.sort(key=lambda x: x.responded_at or x.created_at)
        
        for idx, conn in enumerate(conns, 1):
            target = conn.new_hire
            target_name = target.full_name if target else "Unknown"
            target_code = target.emp_code if target else "Unknown"
            target_dept = get_dept(target)
            target_role = target.role if target else "N/A"
            conn_time = (conn.responded_at or conn.created_at).strftime("%Y-%m-%d %H:%M:%S")
            
            ws.append([idx, target_name, target_code, target_dept, target_role, conn_time])
            
        # Adjust column widths
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter # Get the column name
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width

    output_path = os.path.join(os.path.dirname(__file__), "Ket_qua_ket_noi_chi_tiet.xlsx")
    wb.save(output_path)
    print(f"Exported successfully to {output_path}")

if __name__ == "__main__":
    run_export()
