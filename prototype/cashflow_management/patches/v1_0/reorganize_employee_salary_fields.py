"""
Move salary-related custom fields to Salary tab and hide unused fields
"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
    """Move custom salary fields to Salary tab and hide unused fields"""
    
    # First, delete old custom fields to recreate them in correct position
    old_fields = [
        'custom_employee_type_section', 'custom_employee_type', 'custom_payment_method',
        'custom_base_salary', 'custom_bhxh_salary', 'custom_daily_rate',
        'column_break_emp_type', 'custom_primary_team', 'custom_salary_section',
        'column_break_performance',
        'custom_last_performance_rating', 'custom_last_rating_date', 'custom_performance_factor'
    ]
    
    for fieldname in old_fields:
        if frappe.db.exists("Custom Field", {"dt": "Employee", "fieldname": fieldname}):
            try:
                frappe.delete_doc("Custom Field", f"Employee-{fieldname}", force=1)
                print(f"Deleted old field: {fieldname}")
            except:
                pass
    
    frappe.db.commit()
    
    # Create custom fields in Salary tab (after salary_mode field)
    custom_fields = {
        "Employee": [
            # Section for Employee Type and Payment (in Salary tab)
            {
                "fieldname": "custom_employee_type_section",
                "label": "Phân Loại Nhân Viên",
                "fieldtype": "Section Break",
                "insert_after": "salary_mode",  # First field in Salary tab
                "collapsible": 0
            },
            {
                "fieldname": "custom_employee_type",
                "label": "Loại Nhân Viên",
                "fieldtype": "Select",
                "options": "\nRegular\nIntern\nFreelancer",
                "insert_after": "custom_employee_type_section",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "reqd": 1,
                "default": "Regular"
            },
            {
                "fieldname": "custom_payment_method",
                "label": "Phương Thức Thanh Toán",
                "fieldtype": "Select",
                "options": "\nBank\nCash",
                "insert_after": "custom_employee_type",
                "default": "Bank"
            },
            {
                "fieldname": "column_break_emp_type",
                "fieldtype": "Column Break",
                "insert_after": "custom_payment_method"
            },
            {
                "fieldname": "custom_primary_team",
                "label": "Nhóm Chính",
                "fieldtype": "Link",
                "options": "Team",
                "insert_after": "column_break_emp_type",
                "in_list_view": 1,
                "in_standard_filter": 1
            },
            # Salary section
            {
                "fieldname": "custom_salary_section",
                "label": "Thông Tin Lương",
                "fieldtype": "Section Break",
                "insert_after": "custom_primary_team",
                "collapsible": 0
            },
            {
                "fieldname": "custom_base_salary",
                "label": "Lương Cơ Bản",
                "fieldtype": "Currency",
                "insert_after": "custom_salary_section",
                "precision": 2,
                "depends_on": "eval:doc.custom_employee_type=='Regular'"
            },
            {
                "fieldname": "custom_bhxh_salary",
                "label": "Lương BHXH",
                "fieldtype": "Currency",
                "insert_after": "custom_base_salary",
                "precision": 2,
                "default": "4960000",
                "depends_on": "eval:doc.custom_employee_type=='Regular'",
                "description": "Mức lương đóng BHXH (mặc định = lương tối thiểu vùng)"
            },
            {
                "fieldname": "custom_daily_rate",
                "label": "Đơn Giá Ngày",
                "fieldtype": "Currency",
                "insert_after": "custom_bhxh_salary",
                "precision": 2,
                "depends_on": "eval:doc.custom_employee_type=='Intern'"
            },
            # Performance section
            {
                "fieldname": "column_break_performance",
                "fieldtype": "Column Break",
                "insert_after": "custom_daily_rate"
            },
            {
                "fieldname": "custom_last_performance_rating",
                "label": "Đánh Giá Gần Nhất",
                "fieldtype": "Select",
                "options": "1\n2\n3\n4\n5",
                "insert_after": "column_break_performance",
                "read_only": 1,
                "description": "Điểm đánh giá hiệu suất gần nhất"
            },
            {
                "fieldname": "custom_last_rating_date",
                "label": "Ngày Đánh Giá Gần Nhất",
                "fieldtype": "Date",
                "insert_after": "custom_last_performance_rating",
                "read_only": 1
            },
            {
                "fieldname": "custom_performance_factor",
                "label": "Hệ Số Hiệu Suất",
                "fieldtype": "Float",
                "precision": "2",
                "insert_after": "custom_last_rating_date",
                "read_only": 1,
                "default": "1.0",
                "description": "Hệ số nhân cho tính lương (0.6 - 1.5)"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    
    # Hide unused standard fields in Salary tab
    unused_salary_fields = [
        "salary_currency",
        "salary_mode",
        "ctc"  # Hide CTC field
    ]
    
    for fieldname in unused_salary_fields:
        try:
            make_property_setter(
                doctype="Employee",
                fieldname=fieldname,
                property="hidden",
                value="1",
                property_type="Check"
            )
            print(f"Hidden field: {fieldname}")
        except Exception as e:
            print(f"Could not hide {fieldname}: {e}")
    
    # Set default values for existing employees
    frappe.db.sql("""
        UPDATE `tabEmployee`
        SET custom_employee_type = 'Regular',
            custom_performance_factor = 1.0,
            custom_payment_method = 'Bank'
        WHERE custom_employee_type IS NULL OR custom_employee_type = ''
    """)
    
    frappe.db.commit()
    print("✓ Moved salary fields to Salary tab and hidden unused fields")
