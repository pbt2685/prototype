"""
Debt Management DocType Controller
"""

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, date_diff, add_days, getdate


class DebtManagement(Document):
    def validate(self):
        """Validation logic"""
        self.calculate_days_overdue()
        self.auto_escalate()
        self.calculate_payment_probability()
        self.validate_status()
    
    def calculate_days_overdue(self):
        """CR-DEBT-OVERDUE-001: Calculate days overdue"""
        if self.due_date:
            today = getdate(nowdate())
            due = getdate(self.due_date)
            days = date_diff(today, due)
            self.days_overdue = max(0, days)
    
    def auto_escalate(self):
        """
        BR-ESCALATE-001 through BR-ESCALATE-004: Auto-escalate based on days overdue
        """
        if not self.days_overdue:
            return
        
        old_level = self.escalation_level
        
        # BR-ESCALATE-001: 0-15 days = Level 0 (monitoring)
        if self.days_overdue <= 15:
            self.escalation_level = "0 - Monitoring"
        
        # BR-ESCALATE-002: 16-30 days = Level 1 (Account Manager)
        elif self.days_overdue <= 30:
            self.escalation_level = "1 - Account Manager"
        
        # BR-ESCALATE-003: 31-60 days = Level 2 (Finance Manager)
        elif self.days_overdue <= 60:
            self.escalation_level = "2 - Finance Manager"
        
        # BR-ESCALATE-004: 61+ days = Level 3 (CFO/Legal)
        else:
            self.escalation_level = "3 - CFO/Legal"
        
        # BR-DEBT-004: Escalation triggers notification
        if old_level != self.escalation_level and not self.is_new():
            self.send_escalation_notification()
    
    def calculate_payment_probability(self):
        """
        CR-DEBT-RISK-001: Calculate payment probability based on escalation level
        """
        level_map = {
            "0 - Monitoring": 95,
            "1 - Account Manager": 95,
            "2 - Finance Manager": 80,
            "3 - CFO/Legal": 50
        }
        self.payment_probability = level_map.get(self.escalation_level, 50)
    
    def validate_status(self):
        """BR-DEBT-003: Cannot close debt if outstanding > 0"""
        if self.current_status == "Resolved" and self.outstanding_amount > 0:
            frappe.throw("Không thể đóng công nợ khi còn số tiền chưa thanh toán")
    
    def send_escalation_notification(self):
        """BR-DEBT-004: Send notification on escalation"""
        # Get appropriate contact based on level
        contact_role = self.get_contact_role()
        
        # Send notification (simplified - in real system use Email/Notification)
        frappe.msgprint(
            f"Công nợ {self.name} đã leo thang lên mức {self.escalation_level}. "
            f"Liên hệ: {contact_role}",
            indicator="orange",
            alert=True
        )
    
    def get_contact_role(self):
        """Get appropriate contact role based on escalation level"""
        role_map = {
            "0 - Monitoring": "Sales User",
            "1 - Account Manager": "Sales Manager",
            "2 - Finance Manager": "Accounts Manager",
            "3 - CFO/Legal": "System Manager"
        }
        return role_map.get(self.escalation_level, "Accounts Manager")
    
    def on_update(self):
        """Check for action reminders"""
        # BR-ACTION-001: If no action in 7 days, send reminder
        if self.last_action_date:
            days_since_action = date_diff(nowdate(), self.last_action_date)
            if days_since_action > 7 and self.current_status == "In Progress":
                self.send_action_reminder()
    
    def send_action_reminder(self):
        """Send reminder if no action taken"""
        if self.assigned_to:
            # In real system, send email/notification
            frappe.msgprint(
                f"Nhắc nhở: Công nợ {self.name} chưa có hành động trong 7 ngày",
                indicator="red",
                alert=True
            )


@frappe.whitelist()
def create_debt_from_payment_schedule(payment_schedule_name):
    """
    BR-DEBT-001: Auto-create debt record when payment overdue
    Called from Payment Schedule when status = Overdue
    """
    ps = frappe.get_doc("Payment Schedule", payment_schedule_name)
    
    # Check if debt already exists
    existing = frappe.db.exists("Debt Management", {
        "payment_schedule": payment_schedule_name,
        "current_status": ["!=", "Resolved"]
    })
    
    if existing:
        return {"message": "Debt record already exists", "debt": existing}
    
    # Create debt record
    debt = frappe.get_doc({
        "doctype": "Debt Management",
        "customer": ps.customer,
        "contract": ps.contract,
        "payment_schedule": payment_schedule_name,
        "outstanding_amount": ps.amount,
        "due_date": ps.expected_date,
        "current_status": "Pending",
        "escalation_level": "0 - Monitoring"
    })
    debt.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return {
        "message": "Debt record created",
        "debt": debt.name
    }


@frappe.whitelist()
def update_debt_from_payment(payment_schedule_name, amount_received):
    """
    Update debt when payment is received
    """
    # Find associated debt
    debts = frappe.get_all("Debt Management", {
        "payment_schedule": payment_schedule_name,
        "current_status": ["!=", "Resolved"]
    })
    
    for debt_name in debts:
        debt = frappe.get_doc("Debt Management", debt_name.name)
        debt.outstanding_amount -= amount_received
        
        if debt.outstanding_amount <= 0:
            debt.current_status = "Resolved"
            debt.outstanding_amount = 0
        
        debt.save()
    
    frappe.db.commit()
    return {"message": "Debt updated"}


@frappe.whitelist()
def get_customer_payment_pattern(customer):
    """
    Analyze customer's historical payment delays
    Used for CR-CASHFLOW-ADJUSTMENT-001
    """
    debts = frappe.get_all("Debt Management", {
        "customer": customer,
        "current_status": "Resolved"
    }, ["days_overdue"])
    
    if not debts:
        return {"average_delay": 0, "pattern": "No history"}
    
    total_delay = sum([d.days_overdue or 0 for d in debts])
    avg_delay = total_delay / len(debts)
    
    if avg_delay <= 5:
        pattern = "Excellent"
    elif avg_delay <= 15:
        pattern = "Good"
    elif avg_delay <= 30:
        pattern = "Fair"
    else:
        pattern = "Poor"
    
    return {
        "average_delay": avg_delay,
        "pattern": pattern,
        "total_resolved": len(debts)
    }


# Scheduled job to check for overdue payments daily
def check_overdue_payments():
    """
    Daily scheduled job to:
    1. Check Payment Schedules for overdue
    2. Create Debt Management records
    3. Send escalation notifications
    """
    from prototype.cashflow_management.doctype.payment_schedule.payment_schedule import check_overdue_schedules
    
    # Check and update payment schedules
    overdue_schedules = check_overdue_schedules()
    
    # Create debt records for overdue payments
    for schedule in overdue_schedules:
        try:
            create_debt_from_payment_schedule(schedule["name"])
        except Exception as e:
            frappe.log_error(f"Error creating debt for {schedule['name']}: {str(e)}")
    
    # Check for action reminders
    debts_needing_action = frappe.get_all("Debt Management", {
        "current_status": "In Progress",
        "last_action_date": ["<", add_days(nowdate(), -7)]
    })
    
    for debt in debts_needing_action:
        debt_doc = frappe.get_doc("Debt Management", debt.name)
        debt_doc.send_action_reminder()
