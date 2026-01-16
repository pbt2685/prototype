# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe


def execute():
    """
    M002: Attendance customization patch
    
    Note: ERPNext v15 doesn't have Attendance DocType by default.
    This patch is designed for future compatibility when Attendance is available.
    If Attendance DocType doesn't exist, skip this patch gracefully.
    """
    
    # Check if Attendance DocType exists
    if not frappe.db.exists("DocType", "Attendance"):
        print("⚠ Attendance DocType not found - skipping custom fields patch")
        print("  This is expected for ERPNext v15. Attendance tracking will be added in future modules.")
        return
    
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    
    custom_fields = {
        "Attendance": [
            {
                "fieldname": "late_minutes",
                "label": "Số Phút Trễ",
                "fieldtype": "Int",
                "insert_after": "status",
                "default": "0",
                "read_only": 1,
                "description": "Số phút đến muộn so với giờ làm việc (auto-calculated)"
            },
            {
                "fieldname": "is_half_day",
                "label": "Nửa Ngày",
                "fieldtype": "Check",
                "insert_after": "late_minutes",
                "default": "0",
                "description": "Đánh dấu nếu nhân viên chỉ làm nửa ngày"
            },
            {
                "fieldname": "check_in_time",
                "label": "Giờ Vào",
                "fieldtype": "Time",
                "insert_after": "is_half_day",
                "description": "Thời gian check-in thực tế"
            },
            {
                "fieldname": "check_out_time",
                "label": "Giờ Ra",
                "fieldtype": "Time",
                "insert_after": "check_in_time",
                "description": "Thời gian check-out thực tế"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    print("✓ Added custom fields to Attendance: late_minutes, is_half_day, check_in_time, check_out_time")
