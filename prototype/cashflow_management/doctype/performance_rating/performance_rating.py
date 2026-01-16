# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PerformanceRating(Document):
    def validate(self):
        """Validate performance rating (monthly for interns)"""
        self.validate_intern_only()
        self.validate_duplicate_rating()
        self.calculate_performance_factor()
        self.set_rating_metadata()
    
    def validate_intern_only(self):
        """Performance ratings are primarily for interns"""
        if self.employee_type and self.employee_type != "Intern":
            frappe.msgprint(
                _("Lưu ý: Đánh giá hiệu suất chủ yếu dùng để tính lương cho Thực Tập Sinh. "
                  "Nhân viên loại {0} không cần đánh giá hàng tháng.").format(self.employee_type),
                alert=True,
                indicator="blue"
            )
    
    def validate_duplicate_rating(self):
        """BR-PERF-001: Prevent duplicate rating for same employee and month"""
        # Get year and month from rating_period
        from frappe.utils import get_first_day, get_last_day
        
        first_day = get_first_day(self.rating_period)
        last_day = get_last_day(self.rating_period)
        
        existing = frappe.db.exists(
            "Performance Rating",
            {
                "employee": self.employee,
                "rating_period": ["between", [first_day, last_day]],
                "name": ["!=", self.name],
                "docstatus": ["!=", 2]  # Exclude cancelled
            }
        )
        
        if existing:
            frappe.throw(
                _("Đánh giá hiệu suất cho nhân viên {0} trong tháng {1} đã tồn tại").format(
                    self.employee_name or self.employee,
                    frappe.utils.formatdate(self.rating_period, "MM/yyyy")
                ),
                frappe.exceptions.ValidationError
            )
    
    def calculate_performance_factor(self):
        """Calculate performance factor based on rating score"""
        # Performance Factor mapping: 1=0.6x, 2=0.8x, 3=1.0x, 4=1.2x, 5=1.5x
        factor_map = {
            "1": 0.6,
            "2": 0.8,
            "3": 1.0,
            "4": 1.2,
            "5": 1.5
        }
        
        self.performance_factor = factor_map.get(str(self.rating_score), 1.0)
    
    def set_rating_metadata(self):
        """Set rating by and date if not already set"""
        if not self.rating_by:
            self.rating_by = frappe.session.user
        
        if not self.rating_date:
            self.rating_date = frappe.utils.today()
    
    def on_submit(self):
        """On submit actions"""
        self.update_employee_last_rating()
    
    def on_cancel(self):
        """On cancel actions"""
        self.clear_employee_last_rating()
    
    def update_employee_last_rating(self):
        """Update employee's last performance rating"""
        frappe.db.set_value(
            "Employee",
            self.employee,
            {
                "custom_last_performance_rating": self.rating_score,
                "custom_last_rating_date": self.rating_date,
                "custom_performance_factor": self.performance_factor
            }
        )
    
    def clear_employee_last_rating(self):
        """Clear employee's last performance rating if this was the latest"""
        latest_rating = frappe.db.get_value(
            "Performance Rating",
            {
                "employee": self.employee,
                "docstatus": 1,
                "name": ["!=", self.name]
            },
            ["rating_score", "rating_date", "performance_factor"],
            as_dict=True,
            order_by="rating_date DESC"
        )
        
        if latest_rating:
            frappe.db.set_value(
                "Employee",
                self.employee,
                {
                    "custom_last_performance_rating": latest_rating.rating_score,
                    "custom_last_rating_date": latest_rating.rating_date,
                    "custom_performance_factor": latest_rating.performance_factor
                }
            )
        else:
            frappe.db.set_value(
                "Employee",
                self.employee,
                {
                    "custom_last_performance_rating": None,
                    "custom_last_rating_date": None,
                    "custom_performance_factor": None
                }
            )


@frappe.whitelist()
def override_rating_by_bod(performance_rating, new_rating_score, bod_comments):
    """BR-PERF-002: BOD can override any performance rating"""
    # Check if user has BOD role
    if not frappe.has_permission("Performance Rating", "write") or \
       "System Manager" not in frappe.get_roles():
        frappe.throw(_("Chỉ BOD mới có quyền ghi đè đánh giá hiệu suất"))
    
    doc = frappe.get_doc("Performance Rating", performance_rating)
    
    if doc.docstatus != 1:
        frappe.throw(_("Chỉ có thể ghi đè đánh giá đã được phê duyệt"))
    
    # Create amended version
    amended_doc = frappe.copy_doc(doc)
    amended_doc.rating_score = new_rating_score
    amended_doc.is_overridden_by_bod = 1
    amended_doc.bod_comments = bod_comments
    amended_doc.amended_from = doc.name
    
    # Calculate new performance factor
    amended_doc.calculate_performance_factor()
    
    # Save and submit
    amended_doc.insert()
    amended_doc.submit()
    
    # Cancel original
    doc.cancel()
    
    frappe.msgprint(
        _("Đã ghi đè đánh giá hiệu suất. Đánh giá mới: {0}").format(amended_doc.name)
    )
    
    return amended_doc.name
