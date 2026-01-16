# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, time


def validate_attendance(doc, method):
    """Custom validation for Attendance DocType - M002 Business Rules"""
    calculate_late_minutes(doc)
    check_excessive_late_attendance(doc)
    check_intern_low_attendance(doc)


def calculate_late_minutes(doc):
    """BR-ATT-001: Calculate late minutes if check-in > 15 minutes after start time"""
    if not doc.check_in_time or doc.status != "Present":
        doc.late_minutes = 0
        return
    
    # Get company work start time (default 08:00)
    company_start_time = frappe.db.get_value("Company", doc.company, "default_work_start_time")
    if not company_start_time:
        company_start_time = time(8, 0)  # 08:00 AM
    
    # Parse check-in time
    if isinstance(doc.check_in_time, str):
        check_in = datetime.strptime(doc.check_in_time, "%H:%M:%S").time()
    else:
        check_in = doc.check_in_time
    
    # Calculate minutes late
    check_in_minutes = check_in.hour * 60 + check_in.minute
    start_minutes = company_start_time.hour * 60 + company_start_time.minute
    
    late_minutes = check_in_minutes - start_minutes
    
    # Apply 15-minute grace period
    if late_minutes > 15:
        doc.late_minutes = late_minutes
    else:
        doc.late_minutes = 0


def check_excessive_late_attendance(doc):
    """BR-ATT-002: Alert manager if late > 3 times/month"""
    if doc.late_minutes <= 0:
        return
    
    # Count late attendance this month
    from frappe.utils import get_first_day, get_last_day
    
    first_day = get_first_day(doc.attendance_date)
    last_day = get_last_day(doc.attendance_date)
    
    late_count = frappe.db.count(
        "Attendance",
        {
            "employee": doc.employee,
            "attendance_date": ["between", [first_day, last_day]],
            "late_minutes": [">", 0],
            "name": ["!=", doc.name]
        }
    )
    
    # If this is the 4th late attendance, send alert
    if late_count >= 3:
        send_late_alert_to_manager(doc, late_count + 1)


def check_intern_low_attendance(doc):
    """BR-ATT-003: Alert manager if intern attendance < 15 days/month"""
    # Check if employee is intern
    employee_type = frappe.db.get_value("Employee", doc.employee, "employee_type")
    
    if employee_type != "Intern":
        return
    
    # Count attendance days this month
    from frappe.utils import get_first_day, get_last_day, formatdate
    
    first_day = get_first_day(doc.attendance_date)
    last_day = get_last_day(doc.attendance_date)
    
    attendance_count = frappe.db.count(
        "Attendance",
        {
            "employee": doc.employee,
            "attendance_date": ["between", [first_day, last_day]],
            "status": "Present",
            "docstatus": 1
        }
    )
    
    # On last day of month, if < 15 days, send alert
    if formatdate(doc.attendance_date) == formatdate(last_day):
        if attendance_count < 15:
            send_intern_low_attendance_alert(doc, attendance_count)


def send_late_alert_to_manager(doc, late_count):
    """Send notification to manager about excessive late attendance"""
    # Get team lead
    team = frappe.db.get_value("Employee", doc.employee, "primary_team")
    if not team:
        return
    
    team_lead = frappe.db.get_value("Team", team, "team_lead")
    if not team_lead:
        return
    
    team_lead_user = frappe.db.get_value("Employee", team_lead, "user_id")
    if not team_lead_user:
        return
    
    # Create notification
    notification = frappe.new_doc("Notification Log")
    notification.subject = _("Cảnh báo: Nhân viên đi trễ quá nhiều")
    notification.for_user = team_lead_user
    notification.type = "Alert"
    notification.document_type = "Attendance"
    notification.document_name = doc.name
    notification.email_content = _(
        "Nhân viên {0} đã đi trễ {1} lần trong tháng {2}. Vui lòng kiểm tra và xử lý."
    ).format(
        doc.employee_name,
        late_count,
        frappe.utils.formatdate(doc.attendance_date, "MM/yyyy")
    )
    notification.insert(ignore_permissions=True)
    
    frappe.msgprint(
        _("Đã gửi cảnh báo đến quản lý về việc đi trễ quá nhiều"),
        alert=True,
        indicator="orange"
    )


def send_intern_low_attendance_alert(doc, attendance_count):
    """Send notification to manager about low intern attendance"""
    # Get team lead
    team = frappe.db.get_value("Employee", doc.employee, "primary_team")
    if not team:
        return
    
    team_lead = frappe.db.get_value("Team", team, "team_lead")
    if not team_lead:
        return
    
    team_lead_user = frappe.db.get_value("Employee", team_lead, "user_id")
    if not team_lead_user:
        return
    
    # Create notification
    notification = frappe.new_doc("Notification Log")
    notification.subject = _("Cảnh báo: Thực tập sinh chấm công thấp")
    notification.for_user = team_lead_user
    notification.type = "Alert"
    notification.document_type = "Attendance"
    notification.document_name = doc.name
    notification.email_content = _(
        "Thực tập sinh {0} chỉ có {1} ngày chấm công trong tháng {2} (< 15 ngày). Điều này ảnh hưởng đến tính lương."
    ).format(
        doc.employee_name,
        attendance_count,
        frappe.utils.formatdate(doc.attendance_date, "MM/yyyy")
    )
    notification.insert(ignore_permissions=True)
    
    frappe.msgprint(
        _("Đã gửi cảnh báo đến quản lý về việc chấm công thấp"),
        alert=True,
        indicator="red"
    )
