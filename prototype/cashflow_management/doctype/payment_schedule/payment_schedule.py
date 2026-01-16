# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, today, getdate


class PaymentSchedule(Document):
    def validate(self):
        """Validate payment schedule"""
        self.calculate_percentage()
        self.update_status()
        self.calculate_delay()
    
    def calculate_percentage(self):
        """Calculate percentage of total contract value"""
        if not self.contract:
            return
        
        contract_value = frappe.db.get_value("Contract", self.contract, "custom_total_contract_value")
        if contract_value and contract_value > 0:
            self.percentage = (self.amount / contract_value) * 100
    
    def update_status(self):
        """BR-PAY-001: Update status based on dates"""
        if self.actual_date:
            self.status = "Received"
        elif self.expected_date:
            expected = getdate(self.expected_date)
            current = getdate(today())
            
            if current > expected:
                # Overdue if > 30 days past expected date
                days_overdue = date_diff(current, expected)
                if days_overdue > 30:
                    self.status = "Overdue"
                    frappe.msgprint(
                        _("Cảnh báo: Thanh toán quá hạn {0} ngày. Cần theo dõi với khách hàng.").format(days_overdue),
                        alert=True,
                        indicator="red"
                    )
                else:
                    self.status = "Pending"
            else:
                self.status = "Pending"
    
    def calculate_delay(self):
        """Calculate delay days if received late"""
        if self.actual_date and self.expected_date:
            actual = getdate(self.actual_date)
            expected = getdate(self.expected_date)
            self.delay_days = date_diff(actual, expected)
            
            if self.delay_days < 0:
                self.delay_days = 0  # Received early = no delay
    
    def on_update(self):
        """Update contract total received when payment is received"""
        if self.status == "Received" and self.actual_date:
            self.update_contract_received_amount()
    
    def update_contract_received_amount(self):
        """Update total received amount in contract"""
        total_received = frappe.db.sql("""
            SELECT SUM(amount)
            FROM `tabPayment Schedule`
            WHERE contract = %s AND status = 'Received' AND docstatus != 2
        """, self.contract)[0][0] or 0
        
        frappe.db.set_value("Contract", self.contract, "custom_total_received", total_received)


@frappe.whitelist()
def mark_as_received(payment_schedule, actual_date=None):
    """Mark payment as received"""
    doc = frappe.get_doc("Payment Schedule", payment_schedule)
    
    if doc.status == "Received":
        frappe.throw(_("Thanh toán này đã được đánh dấu là đã nhận"))
    
    doc.actual_date = actual_date or today()
    doc.status = "Received"
    doc.save()
    
    frappe.msgprint(
        _("Đã đánh dấu thanh toán '{0}' là đã nhận").format(doc.milestone_name),
        alert=True,
        indicator="green"
    )
    
    return doc.name
