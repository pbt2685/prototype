"""
Collection Action DocType Controller
"""

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class CollectionAction(Document):
    def validate(self):
        """Validation logic"""
        self.validate_action_status()
        self.update_debt_record()
    
    def validate_action_status(self):
        """
        BR-ACTION-002: Completed action must have notes
        BR-ACTION-003: Failed action must reschedule follow-up
        """
        if self.action_status == "Completed" and not self.outcome:
            frappe.throw("Hành động hoàn thành phải có ghi chú kết quả")
        
        if self.action_status == "Failed" and not self.followup_date:
            frappe.throw("Hành động thất bại phải đặt lịch theo dõi lại")
    
    def update_debt_record(self):
        """Update associated debt record with latest action info"""
        if self.debt and self.action_status == "Completed":
            debt = frappe.get_doc("Debt Management", self.debt)
            debt.last_action_date = self.action_date
            debt.current_status = "In Progress"
            
            if self.followup_date:
                debt.next_followup_date = self.followup_date
            
            # If outcome mentions payment commitment, update expected date
            if self.outcome and "commitment" in self.outcome.lower():
                # Parse commitment date from outcome (simplified)
                # In real system, use proper date parsing
                if self.followup_date:
                    debt.expected_payment_date = self.followup_date
            
            debt.save(ignore_permissions=True)
