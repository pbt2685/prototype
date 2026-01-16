# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
import os


def setup_m001():
	"""Setup M001: Core Setup - Department & Team Master"""
	print("\n" + "="*60)
	print("🚀 Setting up M001: Core Setup")
	print("="*60 + "\n")
	
	# Check prerequisites
	check_prerequisites()
	
	# Create sample departments
	create_sample_departments()
	
	# Create sample teams
	create_sample_teams()
	
	# Create roles if needed
	create_roles()
	
	print("\n✅ M001 setup completed successfully!\n")


def check_prerequisites():
	"""Check if ERPNext is installed"""
	print("📋 Checking prerequisites...")
	
	if not frappe.db.exists("DocType", "Department"):
		frappe.throw(
			_("Department DocType not found. Please install ERPNext first."),
			title=_("Missing Dependency")
		)
	
	if not frappe.db.exists("DocType", "Employee"):
		frappe.throw(
			_("Employee DocType not found. Please install ERPNext first."),
			title=_("Missing Dependency")
		)
	
	print("   ✓ ERPNext is installed")


def create_sample_departments():
	"""Create sample departments for demo"""
	print("\n📁 Creating sample departments...")
	
	departments = [
		{
			"department_name": "Outsourcing",
			"department_code": "OUTSRC",
			"company": frappe.defaults.get_defaults().get("company")
		},
		{
			"department_name": "R&D",
			"department_code": "RND",
			"company": frappe.defaults.get_defaults().get("company")
		},
		{
			"department_name": "Internal Operations",
			"department_code": "INTERNAL",
			"company": frappe.defaults.get_defaults().get("company")
		}
	]
	
	for dept_data in departments:
		if not frappe.db.exists("Department", dept_data["department_name"]):
			try:
				dept = frappe.get_doc({
					"doctype": "Department",
					**dept_data
				})
				dept.insert(ignore_permissions=True)
				print(f"   ✓ Created department: {dept_data['department_name']}")
			except Exception as e:
				print(f"   ⚠ Error creating department {dept_data['department_name']}: {str(e)}")
		else:
			print(f"   • Department already exists: {dept_data['department_name']}")


def create_sample_teams():
	"""Create sample teams from fixtures"""
	print("\n👥 Creating sample teams...")
	
	teams = [
		{
			"team_code": "FF-TEAM",
			"team_name": "FotoFinder Team",
			"department": "Outsourcing",
			"is_revenue_generating": 1,
			"active": 1,
			"description": "<p>Đội ngũ phát triển dự án FotoFinder - hệ thống quản lý ảnh chụp da liễu</p>"
		},
		{
			"team_code": "DGX-TEAM",
			"team_name": "DGX Team",
			"department": "Outsourcing",
			"is_revenue_generating": 1,
			"active": 1,
			"description": "<p>Đội ngũ phát triển dự án DGX - hệ thống quản lý dữ liệu y tế</p>"
		},
		{
			"team_code": "VTT-TEAM",
			"team_name": "VTT Team",
			"department": "Outsourcing",
			"is_revenue_generating": 1,
			"active": 1,
			"description": "<p>Đội ngũ phát triển dự án VTT - hệ thống quản lý vận tải</p>"
		},
		{
			"team_code": "RND-TEAM",
			"team_name": "Internal R&D Team",
			"department": "R&D",
			"is_revenue_generating": 0,
			"active": 1,
			"description": "<p>Đội ngũ nghiên cứu và phát triển sản phẩm nội bộ</p>"
		},
		{
			"team_code": "SUPPORT-TEAM",
			"team_name": "Support Team",
			"department": "Internal Operations",
			"is_revenue_generating": 0,
			"active": 1,
			"description": "<p>Đội ngũ hỗ trợ kỹ thuật và chăm sóc khách hàng</p>"
		}
	]
	
	for team_data in teams:
		if not frappe.db.exists("Team", team_data["team_code"]):
			try:
				team = frappe.get_doc({
					"doctype": "Team",
					**team_data
				})
				team.insert(ignore_permissions=True)
				print(f"   ✓ Created team: {team_data['team_name']}")
			except Exception as e:
				print(f"   ⚠ Error creating team {team_data['team_name']}: {str(e)}")
		else:
			print(f"   • Team already exists: {team_data['team_name']}")


def create_roles():
	"""Create custom roles if needed"""
	print("\n🔐 Checking roles...")
	
	roles = [
		{
			"role_name": "Team Manager",
			"desk_access": 1
		}
	]
	
	for role_data in roles:
		if not frappe.db.exists("Role", role_data["role_name"]):
			try:
				role = frappe.get_doc({
					"doctype": "Role",
					**role_data
				})
				role.insert(ignore_permissions=True)
				print(f"   ✓ Created role: {role_data['role_name']}")
			except Exception as e:
				print(f"   ⚠ Error creating role {role_data['role_name']}: {str(e)}")
		else:
			print(f"   • Role already exists: {role_data['role_name']}")


if __name__ == "__main__":
	# For testing
	setup_m001()
