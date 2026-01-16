# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def validate_project(doc, method):
    """Custom validation for Project DocType - M003 Business Rules"""
    validate_contract_based_project(doc)
    validate_rd_project(doc)


def validate_contract_based_project(doc):
    """BR-PROJECT-001: Contract-based project must have Contract"""
    if doc.custom_project_type == "Contract-based":
        if not doc.custom_linked_contract:
            frappe.msgprint(
                _("Dự án có hợp đồng cần liên kết với một Hợp Đồng"),
                alert=True,
                indicator="orange"
            )


def validate_rd_project(doc):
    """BR-PROJECT-002 & BR-PROJECT-003: Internal R&D project must have Budget, cannot have Contract"""
    if doc.custom_project_type == "Internal R&D":
        # Must have budget
        if not doc.custom_rd_budget or doc.custom_rd_budget <= 0:
            frappe.throw(
                _("Dự án nghiên cứu nội bộ phải có ngân sách R&D"),
                frappe.exceptions.ValidationError
            )
        
        # Cannot have contract
        if doc.custom_linked_contract:
            frappe.throw(
                _("Dự án nghiên cứu nội bộ không thể có hợp đồng. Hãy chọn loại 'Có Hợp Đồng' nếu dự án này tạo doanh thu."),
                frappe.exceptions.ValidationError
            )
