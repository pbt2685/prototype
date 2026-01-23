# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
	"""Add custom fields to Employee DocType"""
	
	# Check if Employee DocType exists (requires ERPNext)
	if not frappe.db.exists("DocType", "Employee"):
		print("⚠️  Employee DocType not found. Please install ERPNext first.")
		return
	
	# Define custom fields
	custom_fields = [
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
			"fieldname": "custom_daily_rate",
			"label": "Đơn Giá Ngày",
			"fieldtype": "Currency",
			"insert_after": "custom_base_salary",
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
		}
	]
	
	# Create each field, skip if already exists
	for field_dict in custom_fields:
		fieldname = field_dict.get("fieldname")
		
		# Check if custom field already exists
		if frappe.db.exists("Custom Field", {"dt": "Employee", "fieldname": fieldname}):
			print(f"   • Field '{fieldname}' already exists, skipping")
			continue
		
		# Check if field exists in standard Employee DocType
		meta = frappe.get_meta("Employee")
		if meta.has_field(fieldname):
			print(f"   • Field '{fieldname}' exists in standard Employee, skipping")
			continue
		
		try:
			custom_field = create_custom_field("Employee", field_dict, ignore_validate=False)
			print(f"   ✓ Created field: {fieldname}")
		except Exception as e:
			print(f"   ⚠ Error creating field '{fieldname}': {str(e)}")
	
	# Set default employee_type for existing employees
	try:
		frappe.db.sql("""
			UPDATE `tabEmployee`
			SET custom_employee_type = 'Regular'
			WHERE (custom_employee_type IS NULL OR custom_employee_type = '')
			AND EXISTS (SELECT 1 FROM `tabCustom Field` WHERE dt='Employee' AND fieldname='custom_employee_type')
		""")
		frappe.db.commit()
	except Exception as e:
		print(f"   ⚠ Could not set default custom_employee_type: {str(e)}")
	
	print("✅ Added custom fields to Employee")
