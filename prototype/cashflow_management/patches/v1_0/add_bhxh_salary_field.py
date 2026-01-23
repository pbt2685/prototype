"""
Add BHXH Salary field to Employee
"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    """Add BHXH salary field for manual entry"""
    
    # Minimum salary in Vietnam (as of 2024, adjust as needed)
    MINIMUM_SALARY = 4960000  # 4.96M VND
    
    custom_fields = {
        "Employee": [
            {
                "fieldname": "custom_bhxh_salary",
                "label": "Lương BHXH (Social Security Salary)",
                "fieldtype": "Currency",
                "insert_after": "custom_payment_method",
                "precision": 2,
                "default": str(MINIMUM_SALARY),
                "depends_on": "eval:doc.custom_employee_type=='Regular'",
                "description": "Mức lương đóng BHXH (mặc định = lương tối thiểu vùng)"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    
    # Set default BHXH salary for existing regular employees
    frappe.db.sql(f"""
        UPDATE `tabEmployee`
        SET custom_bhxh_salary = {MINIMUM_SALARY}
        WHERE custom_employee_type = 'Regular'
        AND (custom_bhxh_salary IS NULL OR custom_bhxh_salary = 0)
    """)
    
    frappe.db.commit()
    print(f"✓ Added BHXH salary field with default {MINIMUM_SALARY:,} VND")
