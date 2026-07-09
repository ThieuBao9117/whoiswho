import os

def fix_admin():
    admin_path = r"c:\WHO\csbwhoiswho\backend\app\api\admin.py"
    with open(admin_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # We need to replace the entire export_report_excel function
    import re
    
    new_func = """
@router.get("/report/{period}/export")
def export_report_excel(period: str, db: Session = Depends(get_db)):
    \"\"\"Export connection details for winners of a specific month\"\"\"
    try:
        year_str, month_str = period.split("-")
        target_year = int(year_str)
        target_month = int(month_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid period format, expected YYYY-MM")

    winners = get_leaderboard_data(db, limit=1000, target_month=target_month, target_year=target_year)

    wb = openpyxl.Workbook()
    default_sheet = wb.active
    wb.remove(default_sheet)

    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    winner_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

    has_data = False

    def get_dept(emp):
        if not emp: return "N/A"
        return (emp.part or emp.department) or "N/A"

    from sqlalchemy import or_

    sheet_title = f"Tháng {target_month}-{target_year}"
    ws = wb.create_sheet(title=sheet_title)
    ws.append([f"DANH SÁCH CHIẾN THẮNG THÁNG {target_month}/{target_year}"])
    ws.append([])

    for winner in winners:
        has_data = True
        emp_id = winner["id"]
        emp = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == emp_id).first()
        if not emp: continue

        ws.append([
            f"Người thắng: {winner['name']} ({winner['emp_code']})", 
            f"Phòng ban: {winner['dept']}", 
            f"Tổng số lượng kết nối: {winner['raw_count']} người",
            f"Thời gian hoàn thành KPI: {winner['score']}"
        ])
        for cell in ws._cells.values():
            if cell.row == ws.max_row:
                cell.fill = winner_fill
                cell.font = Font(bold=True)

        ws.append(["STT", "Người được kết nối", "Mã NV", "Phòng ban / Tổ", "Chức vụ", "Thời gian kết nối thành công"])
        for cell in ws._cells.values():
            if cell.row == ws.max_row:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center")

        conns = db.query(CRWConnection).filter(
            or_(CRWConnection.connector_id == emp_id, CRWConnection.new_hire_id == emp_id),
            CRWConnection.status == ConnectionStatus.ACCEPTED
        ).all()
        conns.sort(key=lambda x: x.responded_at or x.created_at)

        for idx, conn in enumerate(conns, 1):
            if conn.connector_id == emp_id:
                target = conn.new_hire
            else:
                target = conn.connector
                
            t_name = target.full_name if target else "Unknown"
            t_code = target.emp_code if target else "Unknown"
            t_dept = get_dept(target)
            t_role = target.role if target else "N/A"
            c_time = (conn.responded_at or conn.created_at)
            c_time_str = c_time.strftime("%Y-%m-%d %H:%M:%S") if c_time else "N/A"
            
            ws.append([idx, t_name, t_code, t_dept, t_role, c_time_str])

        ws.append([])
        ws.append([])

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        ws.column_dimensions[column].width = min(max_length + 2, 50)

    if not has_data:
        ws.append([f"Chưa có người chiến thắng nào trong tháng {target_month}/{target_year}."])

    # Save to BytesIO
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    headers = {
        'Content-Disposition': f'attachment; filename="Chi_Tiet_Nguoi_Thang_Cuoc_{period}.xlsx"',
        'Access-Control-Expose-Headers': 'Content-Disposition'
    }
    
    return StreamingResponse(output, headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
"""

    start_idx = content.find('@router.get("/report/{period}/export")')
    if start_idx != -1:
        content = content[:start_idx] + new_func
        with open(admin_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Replaced successfully")
    else:
        print("Could not find function")

if __name__ == "__main__":
    fix_admin()
