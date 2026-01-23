# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Add custom fields to Project DocType for M003"""
    
    custom_fields = {
        "Project": [
            {
                "fieldname": "custom_project_type",
                "label": "Loại Dự Án",
                "fieldtype": "Select",
                "options": "Contract-based\nInternal R&D",
                "insert_after": "project_type",
                "default": "Contract-based",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "description": "Có Hợp Đồng = dự án tạo doanh thu, Nghiên Cứu Nội Bộ = trung tâm chi phí"
            },
            {
                "fieldname": "custom_linked_contract",
                "label": "Hợp Đồng Liên Kết",
                "fieldtype": "Link",
                "options": "Contract",
                "insert_after": "custom_project_type",
                "depends_on": "eval:doc.custom_project_type=='Contract-based'",
                "description": "Hợp đồng cho dự án có hợp đồng"
            },
            {
                "fieldname": "custom_rd_budget",
                "label": "Ngân Sách R&D",
                "fieldtype": "Currency",
                "insert_after": "custom_linked_contract",
                "depends_on": "eval:doc.custom_project_type=='Internal R&D'",
                "precision": "2",
                "description": "Ngân sách cho dự án nghiên cứu nội bộ"
            },
            {
                "fieldname": "custom_bonus_policy",
                "label": "Chính Sách Thưởng (%)",
                "fieldtype": "Percent",
                "insert_after": "custom_rd_budget",
                "depends_on": "eval:doc.custom_project_type=='Contract-based'",
                "precision": "2",
                "default": "10",
                "description": "% lợi nhuận dự án dành cho quỹ thưởng"
            },
            {
                "fieldname": "custom_project_status",
                "label": "Tình Trạng Tiến Độ",
                "fieldtype": "Select",
                "options": "On-time\nDelayed",
                "insert_after": "status",
                "default": "On-time",
                "in_list_view": 1,
                "description": "Đúng Hạn / Trễ Hạn"
            },
            {
                "fieldname": "custom_assigned_team",
                "label": "Nhóm Phụ Trách",
                "fieldtype": "Link",
                "options": "Team",
                "insert_after": "custom_project_status",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "description": "Nhóm được giao thực hiện dự án"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    print("✓ Added custom fields to Project: custom_project_type, custom_linked_contract, custom_rd_budget, custom_bonus_policy, custom_project_status, custom_assigned_team")
