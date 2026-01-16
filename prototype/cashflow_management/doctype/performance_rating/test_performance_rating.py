# Copyright (c) 2026, FaceNet and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_months, get_first_day, get_last_day


class TestPerformanceRating(FrappeTestCase):
    def setUp(self):
        """Setup test data"""
        self.create_test_employee()
    
    def tearDown(self):
        """Clean up test data"""
        if hasattr(self, 'test_employee'):
            frappe.db.delete("Performance Rating", {"employee": self.test_employee})
            frappe.db.commit()
    
    def create_test_employee(self):
        """Create test employee"""
        # Check if test employee already exists
        existing = frappe.db.get_value("Employee", {"employee_name": "Test Employee Performance"}, "name")
        if existing:
            self.test_employee = existing
            return
        
        # Get or create test department
        dept_name = frappe.db.get_value("Department", {"department_name": "Test Department"}, "name")
        if not dept_name:
            dept = frappe.get_doc({
                "doctype": "Department",
                "department_name": "Test Department",
                "company": frappe.defaults.get_defaults().get("company")
            })
            dept.insert(ignore_permissions=True)
            dept_name = dept.name
        
        emp = frappe.get_doc({
            "doctype": "Employee",
            "employee_name": "Test Employee Performance",
            "first_name": "Test",
            "last_name": "Performance",
            "gender": "Male",
            "date_of_birth": "1995-01-01",
            "date_of_joining": today(),
            "status": "Active",
            "employee_type": "Intern",
            "daily_rate": 100000,
            "payment_method": "Cash",
            "department": dept_name,
            "company": frappe.defaults.get_defaults().get("company")
        })
        emp.insert(ignore_permissions=True)
        self.test_employee = emp.name
        frappe.db.commit()
    
    def test_create_performance_rating(self):
        """Test creating a performance rating"""
        rating = frappe.get_doc({
            "doctype": "Performance Rating",
            "employee": self.test_employee,
            "rating_period": today(),
            "rating_score": "4",
            "manager_comments": "Good performance"
        })
        rating.insert()
        
        self.assertEqual(rating.rating_score, "4")
        self.assertEqual(rating.performance_factor, 1.2)
        self.assertIsNotNone(rating.rating_by)
        self.assertIsNotNone(rating.rating_date)
    
    def test_performance_factor_calculation(self):
        """Test performance factor calculation for all scores (monthly ratings)"""
        test_cases = [
            ("1", 0.6),
            ("2", 0.8),
            ("3", 1.0),
            ("4", 1.2),
            ("5", 1.5)
        ]
        
        for idx, (score, expected_factor) in enumerate(test_cases):
            # Use different months for each test
            rating = frappe.get_doc({
                "doctype": "Performance Rating",
                "employee": self.test_employee,
                "rating_period": add_months(today(), -(idx + 1)),  # Different month for each
                "rating_score": score
            })
            rating.insert()
            
            self.assertEqual(
                rating.performance_factor, 
                expected_factor,
                f"Score {score} should have factor {expected_factor}"
            )
            
            rating.delete()
    
    def test_duplicate_rating_prevention(self):
        """Test BR-PERF-001: Prevent duplicate rating for same month"""
        rating1 = frappe.get_doc({
            "doctype": "Performance Rating",
            "employee": self.test_employee,
            "rating_period": today(),
            "rating_score": "3"
        })
        rating1.insert()
        
        # Try to create another rating in the same month (different day)
        from frappe.utils import add_days
        rating2 = frappe.get_doc({
            "doctype": "Performance Rating",
            "employee": self.test_employee,
            "rating_period": add_days(today(), 5),  # 5 days later, same month
            "rating_score": "4"
        })
        
        # Both ValidationError (month-level check) and DuplicateEntryError (autoname) prevent duplicates
        with self.assertRaises((frappe.exceptions.ValidationError, frappe.exceptions.DuplicateEntryError)):
            rating2.insert()
    
    def test_update_employee_on_submit(self):
        """Test employee last rating update on submit"""
        rating = frappe.get_doc({
            "doctype": "Performance Rating",
            "employee": self.test_employee,
            "rating_period": today(),
            "rating_score": "5",
            "manager_comments": "Excellent work"
        })
        rating.insert()
        rating.submit()
        
        # Check employee was updated
        emp = frappe.get_doc("Employee", self.test_employee)
        self.assertEqual(emp.custom_last_performance_rating, "5")
        self.assertEqual(emp.custom_performance_factor, 1.5)
        self.assertIsNotNone(emp.custom_last_rating_date)
