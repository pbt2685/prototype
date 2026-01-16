"""
Salary Table DocType Controller
"""

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, now, get_first_day, get_last_day, date_diff
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
import os


class SalaryTable(Document):
    def validate(self):
        """Validation logic"""
        self.validate_period()
        self.calculate_total()
        self.validate_status_change()
    
    def validate_period(self):
        """BR-SAL-003: Ensure period is valid"""
        if not self.period_month or not self.period_year:
            frappe.throw("Tháng và năm là bắt buộc")
        
        try:
            year = int(self.period_year)
            if year < 2000 or year > 2100:
                frappe.throw("Năm không hợp lệ")
        except ValueError:
            frappe.throw("Năm phải là số")
    
    def calculate_total(self):
        """Calculate total amount from all salary items"""
        total = 0
        for item in self.salary_items:
            if item.net_pay:
                total += item.net_pay
        self.total_amount = total
    
    def validate_status_change(self):
        """BR-SAL-003: Salary table must be approved before export"""
        if self.export_status == "Exported" and not self.approved_by:
            frappe.throw("Bảng lương phải được duyệt trước khi xuất")
        
        # Cannot modify after exported
        if self.is_new():
            return
        
        old_doc = self.get_doc_before_save()
        if old_doc and old_doc.export_status == "Exported":
            if self.export_status != "Exported":
                frappe.throw("Không thể thay đổi trạng thái sau khi đã xuất")
    
    def before_submit(self):
        """Auto-approve on submit"""
        if self.export_status == "Draft":
            self.export_status = "Approved"
            self.approved_by = frappe.session.user
            self.approval_date = now()


@frappe.whitelist()
def generate_salary_items(salary_table_name, period_month, period_year):
    """
    Generate salary items for all active employees for the given period
    """
    doc = frappe.get_doc("Salary Table", salary_table_name)
    
    # Clear existing items
    doc.salary_items = []
    
    # Get all active employees
    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["name", "employee_name", "custom_employee_type", "custom_primary_team", 
                "bank_ac_no", "custom_base_salary", "custom_daily_rate", 
                "custom_performance_factor"]
    )
    
    for emp in employees:
        salary_item = calculate_employee_salary(
            emp, period_month, period_year
        )
        doc.append("salary_items", salary_item)
    
    doc.calculate_total()
    doc.save()
    frappe.db.commit()
    
    return {
        "message": f"Đã tạo {len(employees)} mục lương",
        "total_amount": doc.total_amount
    }


def calculate_employee_salary(emp, period_month, period_year):
    """
    Calculate salary for one employee based on type
    CR-SAL-REGULAR-001, CR-SAL-INTERN-001, CR-SAL-FREELANCER-001
    """
    emp_type = emp.get("custom_employee_type", "Regular")
    
    salary_item = {
        "employee": emp.name,
        "employee_name": emp.employee_name,
        "employee_type": emp_type,
        "team": emp.get("custom_primary_team"),
        "bank_account": emp.get("bank_ac_no"),
        "base_amount": 0,
        "attendance_days": 0,
        "performance_factor": 1.0,
        "allowances": 0,
        "deductions": 0,
        "bonus": 0,
        "net_pay": 0,
        "payment_note": ""
    }
    
    if emp_type == "Regular":
        # CR-SAL-REGULAR-001: Base + Allowances - (Tax + SS) + Bonus
        base_salary = emp.get("custom_base_salary", 0)
        salary_item["base_amount"] = base_salary
        
        # Simplified calculation (in real system, use Salary Structure)
        gross = base_salary
        employee_ss = gross * 0.105  # 10.5% employee social security
        
        # Tax calculation (simplified)
        taxable = gross - 11000000 - employee_ss
        tax = max(0, taxable * 0.1)  # Simplified 10% tax
        
        allowances = 2000000  # Fixed allowances (simplified)
        bonus = get_employee_bonus(emp.name, period_month, period_year)
        
        net_pay = gross + allowances - employee_ss - tax + bonus
        
        salary_item.update({
            "allowances": allowances,
            "deductions": employee_ss + tax,
            "bonus": bonus,
            "net_pay": net_pay,
            "payment_note": generate_payment_note(
                period_month, period_year, gross, allowances, employee_ss + tax, bonus
            )
        })
    
    elif emp_type == "Intern":
        # CR-SAL-INTERN-001: Daily Rate × Attendance × Performance Factor + Bonus
        # BR-SAL-001: Cannot create without attendance
        # BR-SAL-002: Requires performance rating
        
        daily_rate = emp.get("custom_daily_rate", 0)
        attendance_days = get_attendance_days(emp.name, period_month, period_year)
        
        # Get performance factor from Performance Rating
        performance_factor = get_performance_factor(emp.name, period_month, period_year)
        if performance_factor is None:
            performance_factor = emp.get("custom_performance_factor", 1.0)
        
        base = daily_rate * attendance_days
        adjusted = base * performance_factor
        bonus = get_employee_bonus(emp.name, period_month, period_year)
        net_pay = adjusted + bonus
        
        salary_item.update({
            "base_amount": daily_rate,
            "attendance_days": attendance_days,
            "performance_factor": performance_factor,
            "bonus": bonus,
            "net_pay": net_pay,
            "payment_note": generate_payment_note(
                period_month, period_year, base, 0, 0, bonus, 
                attendance_days, performance_factor
            )
        })
    
    elif emp_type == "Freelancer":
        # CR-SAL-FREELANCER-001: Project Fee - Tax Withholding
        project_fee = get_freelancer_project_fee(emp.name, period_month, period_year)
        tax_withholding = project_fee * 0.1 if project_fee > 2000000 else 0
        
        net_pay = project_fee - tax_withholding
        
        salary_item.update({
            "base_amount": project_fee,
            "deductions": tax_withholding,
            "net_pay": net_pay,
            "payment_note": generate_payment_note(
                period_month, period_year, project_fee, 0, tax_withholding, 0
            )
        })
    
    return salary_item


def generate_payment_note(period_month, period_year, base, allowances, deductions, bonus, 
                         attendance_days=None, performance_factor=None):
    """
    CR-PAYMENT-NOTE-001: Generate Vietnamese payment note
    BR-SAL-004: Payment note ≤ 200 characters
    """
    note_parts = [f"Lương tháng {period_month}/{period_year}"]
    
    if attendance_days is not None:
        # Intern note
        note_parts.append(f"Ngày công: {attendance_days}")
        if performance_factor:
            note_parts.append(f"HS: {performance_factor}x")
    else:
        # Regular/Freelancer note
        if base:
            note_parts.append(f"LCB: {format_currency(base)}")
        if allowances:
            note_parts.append(f"PC: {format_currency(allowances)}")
        if deductions:
            note_parts.append(f"KT: -{format_currency(deductions)}")
    
    if bonus:
        note_parts.append(f"Thưởng: {format_currency(bonus)}")
    
    note = ", ".join(note_parts)
    
    # BR-SAL-004: Truncate if too long
    if len(note) > 200:
        note = note[:197] + "..."
    
    return note


def format_currency(amount):
    """Format currency in millions for compact display"""
    if amount >= 1000000:
        return f"{amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"{amount/1000:.0f}K"
    else:
        return f"{amount:.0f}"


def get_attendance_days(employee, month, year):
    """Get attendance days for intern (simplified - would use Attendance DocType)"""
    # For now, return estimated days (in real system, query Attendance)
    # This is a placeholder until Attendance DocType is available
    return 22  # Default 22 working days


def get_performance_factor(employee, month, year):
    """Get performance factor from Performance Rating"""
    # Find performance rating for this month
    rating_doc = frappe.db.get_value(
        "Performance Rating",
        {
            "employee": employee,
            "rating_period": ["like", f"{year}-{month}%"]
        },
        "performance_factor"
    )
    return rating_doc


def get_employee_bonus(employee, month, year):
    """Get project bonus for employee (simplified)"""
    # In real system, query from Project milestones
    return 0


def get_freelancer_project_fee(employee, month, year):
    """Get freelancer project fee for the month (simplified)"""
    # In real system, query from Project/Timesheet
    return 0


@frappe.whitelist()
def approve_salary_table(salary_table_name):
    """
    Approve salary table for export
    """
    doc = frappe.get_doc("Salary Table", salary_table_name)
    
    if doc.export_status != "Draft":
        frappe.throw("Chỉ có thể duyệt bảng lương ở trạng thái Draft")
    
    doc.export_status = "Approved"
    doc.approved_by = frappe.session.user
    doc.approval_date = now()
    doc.save()
    frappe.db.commit()
    
    return {"message": "Đã duyệt bảng lương"}


@frappe.whitelist()
def export_to_bank_file(salary_table_name):
    """
    Export salary table to Excel file for bank bulk payment
    BR-SAL-003: Must be approved before export
    """
    doc = frappe.get_doc("Salary Table", salary_table_name)
    
    if doc.export_status != "Approved":
        frappe.throw("Bảng lương phải được duyệt trước khi xuất")
    
    # Create Excel file
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Salary {doc.period_month}-{doc.period_year}"
    
    # Header row
    headers = ["Mã NV", "Tên Nhân Viên", "Tài Khoản NH", "Số Tiền", "Ghi Chú Thanh Toán"]
    ws.append(headers)
    
    # Style header
    header_font = Font(bold=True)
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    # Data rows
    for item in doc.salary_items:
        ws.append([
            item.employee,
            item.employee_name,
            item.bank_account or "",
            item.net_pay,
            item.payment_note or ""
        ])
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Save to temp file
    file_path = frappe.get_site_path("private", "files", 
                                     f"salary_table_{doc.name}.xlsx")
    wb.save(file_path)
    
    # Attach to document
    with open(file_path, "rb") as f:
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"salary_table_{doc.name}.xlsx",
            "attached_to_doctype": "Salary Table",
            "attached_to_name": doc.name,
            "content": f.read(),
            "is_private": 1
        })
        file_doc.insert(ignore_permissions=True)
    
    # Update document
    doc.export_status = "Exported"
    doc.export_date = now()
    doc.bank_file = file_doc.file_url
    doc.save()
    frappe.db.commit()
    
    # Clean up temp file
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return {
        "message": "Đã xuất file ngân hàng",
        "file_url": file_doc.file_url
    }
