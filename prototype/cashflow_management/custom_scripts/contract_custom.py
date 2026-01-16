# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def validate_contract(doc, method):
    """Custom validation for Contract DocType - M003 Business Rules"""
    validate_payment_terms_sum(doc)
    calculate_balance(doc)


def validate_payment_terms_sum(doc):
    """BR-CONTRACT-001: Payment terms must sum to contract value"""
    if not doc.custom_total_contract_value:
        return
    
    # Get total from payment schedules
    total_scheduled = frappe.db.sql("""
        SELECT SUM(amount)
        FROM `tabPayment Schedule`
        WHERE contract = %s AND docstatus != 2
    """, doc.name)[0][0] or 0
    
    if total_scheduled > 0:
        variance = abs(total_scheduled - doc.custom_total_contract_value)
        variance_percent = (variance / doc.custom_total_contract_value) * 100
        
        if variance_percent > 1:  # Allow 1% variance for rounding
            frappe.msgprint(
                _("Cảnh báo: Tổng lịch thanh toán ({0}) không khớp với giá trị hợp đồng ({1})").format(
                    frappe.format(total_scheduled, {"fieldtype": "Currency"}),
                    frappe.format(doc.custom_total_contract_value, {"fieldtype": "Currency"})
                ),
                alert=True,
                indicator="orange"
            )


def calculate_balance(doc):
    """Calculate remaining balance"""
    if doc.custom_total_contract_value:
        doc.custom_balance = doc.custom_total_contract_value - (doc.custom_total_received or 0)
