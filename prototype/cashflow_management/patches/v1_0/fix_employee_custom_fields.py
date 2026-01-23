"""
Script to fix Employee custom field names
"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    """Add missing custom_ prefixed fields to Employee"""
    
    # First, check if the old fields exist and delete them
    old_fields = ['employee_type', 'payment_method', 'daily_rate', 'primary_team', 'employee_type_section']
    for fieldname in old_fields:
        if frappe.db.exists("Custom Field", {"dt": "Employee", "fieldname": fieldname}):
            try:
                frappe.delete_doc("Custom Field", f"Employee-{fieldname}")
                print(f"Deleted old field: {fieldname}")
            except:
                pass
    
    # Now create the correct custom_ prefixed fields
    custom_fields = {
        "Employee": [
            {
                "fieldname": "custom_employee_type_section",
                "label": "Phân Loại Nhân Viên",
                "fieldtype": "Section Break",
                "insert_after": "employment_type",
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
                "fieldname": "custom_base_salary",
                "label": "Lương Cơ Bản",
                "fieldtype": "Currency",
                "insert_after": "custom_payment_method",
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
            {
                "fieldname": "column_break_emp_type",
                "fieldtype": "Column Break",
                "insert_after": "custom_daily_rate"
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
            {
                "fieldname": "custom_last_performance_rating",
                "label": "Đánh Giá Gần Nhất",
                "fieldtype": "Select",
                "options": "1\n2\n3\n4\n5",
                "insert_after": "custom_primary_team",
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
    
    # Set default values for existing employees
    frappe.db.sql("""
        UPDATE `tabEmployee`
        SET custom_employee_type = 'Regular',
            custom_performance_factor = 1.0,
            custom_payment_method = 'Bank'
        WHERE custom_employee_type IS NULL OR custom_employee_type = ''
    """)
    
    frappe.db.commit()
    print("✓ Fixed all Employee custom fields")
