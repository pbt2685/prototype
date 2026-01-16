# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add custom fields to Department DocType"""
	
	# Check if Department DocType exists (requires ERPNext)
	if not frappe.db.exists("DocType", "Department"):
		print("⚠️  Department DocType not found. Please install ERPNext first.")
		return
	
	custom_fields = {
		"Department": [
			{
				"fieldname": "department_code",
				"label": "Mã Phòng Ban",
				"fieldtype": "Data",
				"insert_after": "department_name",
				"length": 20,
				"unique": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"reqd": 0
			},
			{
				"fieldname": "cost_center_allocation",
				"label": "Phân Bổ Trung Tâm Chi Phí",
				"fieldtype": "Link",
				"options": "Cost Center",
				"insert_after": "department_code",
				"in_list_view": 0
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	
	# Auto-generate department codes for existing departments without codes
	departments = frappe.get_all(
		"Department",
		filters={"department_code": ["is", "not set"]},
		fields=["name", "department_name"]
	)
	
	for dept in departments:
		# Generate code from department name
		code = generate_department_code(dept.department_name)
		
		try:
			frappe.db.set_value(
				"Department",
				dept.name,
				"department_code",
				code,
				update_modified=False
			)
		except Exception as e:
			print(f"⚠️  Could not set code for {dept.name}: {str(e)}")
	
	frappe.db.commit()
	print("✅ Added custom fields to Department and generated codes")


def generate_department_code(department_name):
	"""Generate unique department code from name"""
	# Convert to uppercase and remove special characters
	code = frappe.scrub(department_name).upper().replace("_", "-")[:20]
	
	# Ensure uniqueness
	counter = 1
	original_code = code
	
	while frappe.db.exists("Department", {"department_code": code}):
		code = f"{original_code[:17]}-{counter:02d}"
		counter += 1
	
	return code
