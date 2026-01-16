# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Team(Document):
	def autoname(self):
		"""Auto-generate name from team_code"""
		self.name = self.team_code

	def validate(self):
		"""Validate team data"""
		self.validate_team_code_unique()
		self.validate_team_lead_department()

	def validate_team_code_unique(self):
		"""BR-TEAM-002: Team code must be unique"""
		if self.is_new():
			existing = frappe.db.exists(
				"Team",
				{
					"team_code": self.team_code,
					"name": ["!=", self.name]
				}
			)
			if existing:
				frappe.throw(
					_("Mã nhóm {0} đã tồn tại").format(
						frappe.bold(self.team_code)
					),
					title=_("Mã Trùng Lặp")
				)

	def validate_team_lead_department(self):
		"""BR-TEAM-001: Validate team lead belongs to same department"""
		if self.team_lead:
			employee_dept = frappe.db.get_value("Employee", self.team_lead, "department")
			if employee_dept and employee_dept != self.department:
				frappe.throw(
					_("Trưởng nhóm {0} không thuộc phòng ban {1}").format(
						frappe.bold(self.team_lead),
						frappe.bold(self.department)
					),
					title=_("Lỗi Xác Thực")
				)

	def on_update(self):
		"""Update related records when team is updated"""
		if self.active == 0:
			self.deactivate_team_assignments()

	def deactivate_team_assignments(self):
		"""Remove team assignment from employees when team is deactivated"""
		employees = frappe.get_all(
			"Employee",
			filters={"primary_team": self.name, "status": "Active"},
			fields=["name", "employee_name"]
		)

		if employees:
			for emp in employees:
				frappe.db.set_value("Employee", emp.name, "primary_team", None, update_modified=False)

			frappe.msgprint(
				_("Đã xóa nhóm {0} khỏi {1} nhân viên").format(
					frappe.bold(self.team_name),
					frappe.bold(len(employees))
				),
				indicator="orange"
			)

	def on_trash(self):
		"""Check before deletion"""
		self.check_active_employees()
		self.check_assigned_projects()

	def check_active_employees(self):
		"""Cannot delete team with active employees"""
		employees = frappe.get_all(
			"Employee",
			filters={"primary_team": self.name, "status": "Active"},
			fields=["name", "employee_name"]
		)

		if employees:
			employee_list = ", ".join([f"{e.name} ({e.employee_name})" for e in employees[:5]])
			if len(employees) > 5:
				employee_list += f" và {len(employees) - 5} nhân viên khác"

			frappe.throw(
				_("Không thể xóa nhóm {0}. Còn {1} nhân viên đang hoạt động: {2}").format(
					frappe.bold(self.team_name),
					frappe.bold(len(employees)),
					employee_list
				),
				title=_("Không Thể Xóa")
			)

	def check_assigned_projects(self):
		"""Cannot delete team with assigned projects"""
		projects = frappe.get_all(
			"Project",
			filters={"assigned_team": self.name, "status": ["not in", ["Completed", "Cancelled"]]},
			fields=["name", "project_name"]
		)

		if projects:
			project_list = ", ".join([f"{p.name} ({p.project_name})" for p in projects[:5]])
			if len(projects) > 5:
				project_list += f" và {len(projects) - 5} dự án khác"

			frappe.throw(
				_("Không thể xóa nhóm {0}. Còn {1} dự án đang hoạt động: {2}").format(
					frappe.bold(self.team_name),
					frappe.bold(len(projects)),
					project_list
				),
				title=_("Không Thể Xóa")
			)

	@frappe.whitelist()
	def get_team_members(self):
		"""Get all employees in this team"""
		return frappe.get_all(
			"Employee",
			filters={
				"primary_team": self.name,
				"status": "Active"
			},
			fields=["name", "employee_name", "designation", "employee_type", "department"],
			order_by="employee_name"
		)

	@frappe.whitelist()
	def get_team_projects(self):
		"""Get all projects assigned to this team"""
		return frappe.get_all(
			"Project",
			filters={
				"assigned_team": self.name,
				"status": ["not in", ["Completed", "Cancelled"]]
			},
			fields=["name", "project_name", "project_type", "status", "expected_end_date"],
			order_by="expected_end_date"
		)


@frappe.whitelist()
def get_team_summary(department=None):
	"""Get summary of teams by department for reporting"""
	filters = {"active": 1}
	if department:
		filters["department"] = department

	teams = frappe.get_all(
		"Team",
		filters=filters,
		fields=[
			"name",
			"team_code",
			"team_name",
			"department",
			"team_lead",
			"is_revenue_generating"
		],
		order_by="department, team_name"
	)

	# Add employee count
	for team in teams:
		team["employee_count"] = frappe.db.count(
			"Employee",
			{"primary_team": team.name, "status": "Active"}
		)
		team["project_count"] = frappe.db.count(
			"Project",
			{"assigned_team": team.name, "status": ["not in", ["Completed", "Cancelled"]]}
		)

	return teams
