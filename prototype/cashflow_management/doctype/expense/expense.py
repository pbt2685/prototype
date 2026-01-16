# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, get_first_day, get_last_day, getdate


class Expense(Document):
    def validate(self):
        """Validate expense"""
        self.validate_finance_only()
        self.validate_grouped_expenses()
        self.validate_rd_expense()
        self.calculate_total_amount()
        self.set_initiated_metadata()
    
    def validate_finance_only(self):
        """BR-EXP-002: Only Finance can create expenses"""
        if self.is_new() and not self.initiated_by:
            user_roles = frappe.get_roles(frappe.session.user)
            
            if "Accounts Manager" not in user_roles and "System Manager" not in user_roles:
                frappe.throw(
                    _("Chỉ bộ phận Tài Chính mới có quyền tạo chi phí"),
                    frappe.exceptions.PermissionError
                )
    
    def validate_grouped_expenses(self):
        """BR-EXP-003, BR-EXP-004, BR-EXP-005: Validate grouped expenses"""
        if self.expense_type != "Grouped":
            return
        
        if not self.grouped_items or len(self.grouped_items) == 0:
            frappe.throw(_("Chi phí gộp nhóm phải có ít nhất 1 khoản chi"))
        
        # BR-EXP-004: All items must be in same month
        first_date = None
        for item in self.grouped_items:
            if not first_date:
                first_date = getdate(item.expense_date)
            else:
                item_date = getdate(item.expense_date)
                if item_date.month != first_date.month or item_date.year != first_date.year:
                    frappe.throw(
                        _("Tất cả các khoản chi trong nhóm phải cùng tháng")
                    )
    
    def validate_rd_expense(self):
        """BR-EXP-006: R&D expenses must link to project"""
        if self.category == "R&D" and not self.project:
            frappe.throw(
                _("Chi phí R&D phải liên kết với một Dự Án"),
                frappe.exceptions.ValidationError
            )
        
        # Check R&D budget
        if self.category == "R&D" and self.project:
            project = frappe.get_doc("Project", self.project)
            
            if project.custom_project_type != "Internal R&D":
                frappe.msgprint(
                    _("Lưu ý: Dự án '{0}' không phải là dự án R&D nội bộ").format(project.name),
                    alert=True,
                    indicator="orange"
                )
            
            if project.custom_rd_budget:
                # Get total R&D expenses for this project
                total_rd_expense = frappe.db.sql("""
                    SELECT SUM(amount)
                    FROM `tabExpense`
                    WHERE project = %s 
                    AND category = 'R&D'
                    AND approval_status = 'Approved'
                    AND name != %s
                """, (self.project, self.name))[0][0] or 0
                
                if (total_rd_expense + self.amount) > project.custom_rd_budget:
                    frappe.msgprint(
                        _("Cảnh báo: Tổng chi phí R&D ({0}) sẽ vượt ngân sách ({1})").format(
                            frappe.format(total_rd_expense + self.amount, {"fieldtype": "Currency"}),
                            frappe.format(project.custom_rd_budget, {"fieldtype": "Currency"})
                        ),
                        alert=True,
                        indicator="red"
                    )
    
    def calculate_total_amount(self):
        """Calculate total amount"""
        if self.expense_type == "Grouped":
            total = sum(item.amount or 0 for item in self.grouped_items)
            self.amount = total
        # For Individual type, amount is entered directly
    
    def set_initiated_metadata(self):
        """Set initiated by and date"""
        if self.is_new():
            self.initiated_by = frappe.session.user
            self.initiated_date = today()
    
    def before_save(self):
        """BR-EXP-007: Cannot modify approved expenses"""
        if not self.is_new() and self.has_value_changed("approval_status"):
            old_status = self.get_doc_before_save().approval_status if self.get_doc_before_save() else None
            
            if old_status == "Approved" and self.approval_status != "Approved":
                frappe.throw(
                    _("Không thể sửa đổi chi phí đã được duyệt"),
                    frappe.exceptions.ValidationError
                )
    
    def on_trash(self):
        """BR-EXP-007: Cannot delete approved expenses"""
        if self.approval_status == "Approved":
            frappe.throw(
                _("Không thể xóa chi phí đã được duyệt"),
                frappe.exceptions.ValidationError
            )


@frappe.whitelist()
def submit_for_approval(expense_name):
    """Submit expense for BOD approval"""
    doc = frappe.get_doc("Expense", expense_name)
    
    if doc.approval_status != "Draft":
        frappe.throw(_("Chỉ có thể gửi duyệt chi phí ở trạng thái Nháp"))
    
    doc.approval_status = "Pending BOD"
    doc.save()
    
    # Send notification to BOD members
    send_approval_notification(doc)
    
    frappe.msgprint(
        _("Đã gửi chi phí '{0}' để BGĐ duyệt").format(doc.name),
        alert=True,
        indicator="blue"
    )
    
    return doc.name


@frappe.whitelist()
def approve_expense(expense_name, approval_notes=None):
    """BR-EXP-001: BOD approves expense"""
    # Check if user is BOD (System Manager role)
    user_roles = frappe.get_roles(frappe.session.user)
    if "System Manager" not in user_roles:
        frappe.throw(_("Chỉ BGĐ mới có quyền duyệt chi phí"))
    
    doc = frappe.get_doc("Expense", expense_name)
    
    if doc.approval_status != "Pending BOD":
        frappe.throw(_("Chỉ có thể duyệt chi phí ở trạng thái 'Chờ BGĐ Duyệt'"))
    
    doc.approval_status = "Approved"
    doc.approved_by = frappe.session.user
    doc.approval_date = today()
    if approval_notes:
        doc.approval_notes = approval_notes
    
    doc.save()
    
    frappe.msgprint(
        _("Đã duyệt chi phí '{0}'").format(doc.name),
        alert=True,
        indicator="green"
    )
    
    return doc.name


@frappe.whitelist()
def reject_expense(expense_name, approval_notes=None):
    """BOD rejects expense"""
    # Check if user is BOD (System Manager role)
    user_roles = frappe.get_roles(frappe.session.user)
    if "System Manager" not in user_roles:
        frappe.throw(_("Chỉ BGĐ mới có quyền từ chối chi phí"))
    
    doc = frappe.get_doc("Expense", expense_name)
    
    if doc.approval_status != "Pending BOD":
        frappe.throw(_("Chỉ có thể từ chối chi phí ở trạng thái 'Chờ BGĐ Duyệt'"))
    
    doc.approval_status = "Rejected"
    doc.approved_by = frappe.session.user
    doc.approval_date = today()
    if approval_notes:
        doc.approval_notes = approval_notes
    
    doc.save()
    
    frappe.msgprint(
        _("Đã từ chối chi phí '{0}'").format(doc.name),
        alert=True,
        indicator="red"
    )
    
    return doc.name


def send_approval_notification(doc):
    """Send notification to BOD members for approval"""
    # Get users with System Manager role
    bod_users = frappe.get_all(
        "Has Role",
        filters={"role": "System Manager", "parenttype": "User"},
        fields=["parent"],
        pluck="parent"
    )
    
    for user in bod_users:
        notification = frappe.new_doc("Notification Log")
        notification.subject = _("Chi phí cần duyệt: {0}").format(doc.name)
        notification.for_user = user
        notification.type = "Alert"
        notification.document_type = "Expense"
        notification.document_name = doc.name
        notification.email_content = _(
            "Chi phí {0} - {1}: {2} đang chờ phê duyệt"
        ).format(
            doc.name,
            doc.category,
            frappe.format(doc.amount, {"fieldtype": "Currency"})
        )
        notification.insert(ignore_permissions=True)
