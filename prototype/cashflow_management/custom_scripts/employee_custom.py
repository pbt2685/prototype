# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def validate_employee(doc, method):
    """Custom validation for Employee DocType - M002 Business Rules"""
    validate_employee_type_immutable(doc)
    validate_regular_employee_contract(doc)
    validate_intern_daily_rate(doc)


def validate_employee_type_immutable(doc):
    """BR-EMP-001: Employee type cannot change once set"""
    if doc.is_new():
        return
    
    old_doc = doc.get_doc_before_save()
    if not old_doc:
        return
    
    old_type = old_doc.get("employee_type")
    new_type = doc.get("employee_type")
    
    if old_type and new_type and old_type != new_type:
        frappe.throw(
            _("Không thể thay đổi loại nhân viên sau khi đã thiết lập. Loại hiện tại: {0}").format(old_type),
            frappe.exceptions.ValidationError
        )


def validate_regular_employee_contract(doc):
    """BR-EMP-002: Regular employees must have contract"""
    if doc.employee_type == "Regular":
        # Check if contract exists
        has_contract = frappe.db.exists(
            "Contract",
            {
                "party_name": doc.name,
                "contract_type": "Employee",
                "status": ["in", ["Active", "Unsigned"]]
            }
        )
        
        if not has_contract and not doc.is_new():
            frappe.msgprint(
                _("Nhân viên chính thức cần có hợp đồng lao động. Vui lòng tạo hợp đồng."),
                alert=True,
                indicator="orange"
            )


def validate_intern_daily_rate(doc):
    """BR-EMP-003: Interns must have daily_rate"""
    if doc.employee_type == "Intern":
        if not doc.daily_rate or doc.daily_rate <= 0:
            frappe.throw(
                _("Thực tập sinh phải có đơn giá ngày (daily_rate) để tính lương"),
                frappe.exceptions.ValidationError
            )
        
        # Ensure payment method is Cash for interns
        if doc.payment_method != "Cash":
            frappe.msgprint(
                _("Thực tập sinh thường được thanh toán bằng tiền mặt. Đã tự động chuyển sang phương thức Tiền Mặt."),
                alert=True,
                indicator="blue"
            )
            doc.payment_method = "Cash"
