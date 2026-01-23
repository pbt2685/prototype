# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Add performance tracking fields to Employee DocType for M002"""
    
    custom_fields = {
        "Employee": [
            {
                "fieldname": "custom_last_performance_rating",
                "label": "Đánh Giá Gần Nhất",
                "fieldtype": "Select",
                "options": "1\n2\n3\n4\n5",
                "insert_after": "custom_primary_team",
                "read_only": 1,
                "description": "Điểm đánh giá hiệu suất gần nhất"
            },
            {
                "fieldname": "custom_last_rating_date",
                "label": "Ngày Đánh Giá Gần Nhất",
                "fieldtype": "Date",
                "insert_after": "custom_last_performance_rating",
                "read_only": 1
            },
            {
                "fieldname": "custom_performance_factor",
                "label": "Hệ Số Hiệu Suất",
                "fieldtype": "Float",
                "precision": "2",
                "insert_after": "custom_last_rating_date",
                "read_only": 1,
                "description": "Hệ số nhân cho tính lương (0.6 - 1.5)"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    print("✓ Added performance tracking fields to Employee: custom_last_performance_rating, custom_last_rating_date, custom_performance_factor")
