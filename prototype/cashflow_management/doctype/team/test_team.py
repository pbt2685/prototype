# Copyright (c) 2026, FaceNet and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestTeam(FrappeTestCase):
    def setUp(self):
        """Setup test data before each test"""
        self.create_test_department()
        self.create_test_employee()

    def tearDown(self):
        """Clean up test data after each test"""
        frappe.db.delete("Team", {"team_code": ["like", "TEST-%"]})
        frappe.db.commit()

    def create_test_department(self):
        """Create test department if not exists"""
        if not frappe.db.exists("Department", {"department_name": "Test Department"}):
            dept = frappe.get_doc({
                "doctype": "Department",
                "department_name": "Test Department",
                "company": frappe.defaults.get_defaults().get("company")
            })
            dept.insert(ignore_permissions=True)
            frappe.db.commit()

    def create_test_employee(self):
        """Create test employee if not exists"""
        dept_name = frappe.db.get_value("Department", {"department_name": "Test Department"}, "name")
        
        if not frappe.db.exists("Employee", {"employee_name": "Test Employee Alpha"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_name": "Test Employee Alpha",
                "department": dept_name,
                "status": "Active",
                "first_name": "Test",
                "last_name": "Employee",
                "gender": "Male",
                "date_of_birth": "1990-01-01",
                "date_of_joining": "2024-01-01",
                "company": frappe.defaults.get_defaults().get("company")
            })
            emp.insert(ignore_permissions=True)
            frappe.db.commit()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"employee_name": "Test Employee Alpha"}, "name")

    def test_create_team(self):
        """Test create team successfully"""
        dept_name = frappe.db.get_value("Department", {"department_name": "Test Department"}, "name")
        
        team = frappe.get_doc({
            "doctype": "Team",
            "team_code": "TEST-ALPHA",
            "team_name": "Test Team Alpha",
            "department": dept_name,
            "team_lead": self.test_employee,
            "is_revenue_generating": 1,
            "active": 1
        })
        team.insert()

        self.assertEqual(team.name, "TEST-ALPHA")
        self.assertEqual(team.department, dept_name)
        self.assertEqual(team.team_lead, self.test_employee)

    def test_duplicate_team_code(self):
        """Test BR-TEAM-002: Team code must be unique"""
        dept_name = frappe.db.get_value("Department", {"department_name": "Test Department"}, "name")
        
        team1 = frappe.get_doc({
            "doctype": "Team",
            "team_code": "TEST-BETA",
            "team_name": "Test Team Beta",
            "department": dept_name,
            "active": 1
        })
        team1.insert()

        team2 = frappe.get_doc({
            "doctype": "Team",
            "team_code": "TEST-BETA",
            "team_name": "Test Team Beta Duplicate",
            "department": dept_name,
            "active": 1
        })

        with self.assertRaises(frappe.exceptions.DuplicateEntryError):
            team2.insert()
