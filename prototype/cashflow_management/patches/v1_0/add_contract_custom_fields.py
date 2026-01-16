# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Add custom fields to Contract DocType for M003"""
    
    custom_fields = {
        "Contract": [
            {
                "fieldname": "custom_payment_type",
                "label": "Hình Thức Thanh Toán",
                "fieldtype": "Select",
                "options": "Long-term\nMonthly\nOne-time",
                "insert_after": "contract_terms",
                "description": "Dài Hạn = nhiều mốc, Hàng Tháng = thanh toán định kỳ, Một Lần = thanh toán 1 lần"
            },
            {
                "fieldname": "custom_total_contract_value",
                "label": "Tổng Giá Trị Hợp Đồng",
                "fieldtype": "Currency",
                "insert_after": "custom_payment_type",
                "precision": "2",
                "description": "Tổng giá trị của hợp đồng"
            },
            {
                "fieldname": "custom_total_received",
                "label": "Tổng Đã Nhận",
                "fieldtype": "Currency",
                "insert_after": "custom_total_contract_value",
                "precision": "2",
                "read_only": 1,
                "default": "0",
                "description": "Tổng số tiền đã nhận từ payment schedule"
            },
            {
                "fieldname": "custom_balance",
                "label": "Còn Lại",
                "fieldtype": "Currency",
                "insert_after": "custom_total_received",
                "precision": "2",
                "read_only": 1,
                "description": "Số tiền còn lại chưa thu (auto-calculated)"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    print("✓ Added custom fields to Contract: custom_payment_type, custom_total_contract_value, custom_total_received, custom_balance")
