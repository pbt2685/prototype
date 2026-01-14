# Copyright (c) 2026, Your Organization and contributors
# For license information, please see license.txt

"""
Unit tests for Exam Session Lifecycle (F005)
Tests all business rules and calculations
"""

import frappe
import unittest
from frappe.utils import now_datetime, add_to_date, today, add_days
from prototype.exam_management.api import (
    start_exam_session,
    submit_exam_answers,
    end_exam_session,
    get_session_status
)


class TestExamSessionLifecycle(unittest.TestCase):
    """Test exam session lifecycle functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.setup_test_data()
    
    def tearDown(self):
        """Clean up test data"""
        frappe.db.rollback()
    
    def setup_test_data(self):
        """Create test exam, paper, and session"""
        
        # Create test question
        if not frappe.db.exists("Exam Question", "TEST-Q-001"):
            question = frappe.get_doc({
                "doctype": "Exam Question",
                "question_text": "Test Question 1",
                "question_type": "Multiple Choice",
                "option_a": "A",
                "option_b": "B",
                "option_c": "C",
                "option_d": "D",
                "correct_answer": "A",
                "difficulty_level": "Easy"
            }).insert(ignore_permissions=True)
        
        # Create test paper
        if not frappe.db.exists("Exam Paper", "TEST-PAPER-001"):
            paper = frappe.get_doc({
                "doctype": "Exam Paper",
                "paper_name": "Test Paper",
                "paper_code": "TEST-001",
                "subject": "Test Subject",
                "duration": 60,
                "total_points": 10,
                "questions": [
                    {
                        "question": "TEST-Q-001",
                        "points": 10
                    }
                ]
            }).insert(ignore_permissions=True)
        
        # Create test classroom
        if not frappe.db.exists("Exam Classroom", "TEST-ROOM-001"):
            classroom = frappe.get_doc({
                "doctype": "Exam Classroom",
                "classroom_name": "Test Room",
                "room_number": "101",
                "capacity": 30
            }).insert(ignore_permissions=True)
    
    def create_test_session(self, status="Scheduled", start_offset_minutes=0):
        """Helper to create test session"""
        
        start_datetime = add_to_date(now_datetime(), minutes=start_offset_minutes)
        
        session = frappe.get_doc({
            "doctype": "Exam Session",
            "exam_paper": "TEST-PAPER-001",
            "exam_date": start_datetime.date(),
            "start_time": start_datetime.strftime("%H:%M:%S"),
            "duration": 60,
            "classroom": "TEST-ROOM-001",
            "status": status,
            "participants": [
                {
                    "participant": "test@example.com",
                    "status": "Registered"
                }
            ]
        }).insert(ignore_permissions=True)
        
        if status == "In Progress":
            session.actual_start_time = start_datetime
            session.started_by = frappe.session.user
            session.save(ignore_permissions=True)
        
        return session
    
    # ============================================================
    # TEST: Start Session (API001)
    # ============================================================
    
    def test_start_session_success(self):
        """TEST: Successfully start scheduled session"""
        
        # Create session scheduled for now (within grace period)
        session = self.create_test_session(start_offset_minutes=-10)
        
        # Start session
        result = start_exam_session(session.name)
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["session_id"], session.name)
        self.assertIsNotNone(result["started_at"])
        
        # Verify session status changed
        session.reload()
        self.assertEqual(session.status, "In Progress")
        self.assertIsNotNone(session.actual_start_time)
        self.assertEqual(session.started_by, frappe.session.user)
    
    def test_cannot_start_too_early(self):
        """TEST: BR-SES-001 - Cannot start before scheduled time"""
        
        # Create session scheduled for future (outside grace period)
        session = self.create_test_session(start_offset_minutes=30)
        
        # Try to start
        with self.assertRaises(frappe.ValidationError) as cm:
            start_exam_session(session.name)
        
        self.assertIn("Chưa đến giờ thi", str(cm.exception))
    
    def test_cannot_start_already_started(self):
        """TEST: Cannot start session that's already in progress"""
        
        session = self.create_test_session(status="In Progress", start_offset_minutes=-10)
        
        with self.assertRaises(frappe.ValidationError) as cm:
            start_exam_session(session.name)
        
        self.assertIn("đã được bắt đầu", str(cm.exception))
    
    def test_cannot_start_without_paper(self):
        """TEST: Cannot start session without exam paper"""
        
        session = self.create_test_session(start_offset_minutes=-10)
        session.exam_paper = None
        session.save(ignore_permissions=True)
        
        with self.assertRaises(frappe.ValidationError) as cm:
            start_exam_session(session.name)
        
        self.assertIn("chưa có đề thi", str(cm.exception))
    
    # ============================================================
    # TEST: Submit Answers (API002)
    # ============================================================
    
    def test_submit_answers_success(self):
        """TEST: Successfully submit exam answers"""
        
        session = self.create_test_session(status="In Progress", start_offset_minutes=-10)
        
        answers = {
            "TEST-Q-001": "A"
        }
        
        # Mock user as participant
        frappe.set_user("test@example.com")
        
        result = submit_exam_answers(session.name, answers)
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["submitted_at"])
        self.assertEqual(result["answered_questions"], 1)
        
        # Verify participant status updated
        participant = frappe.get_doc("Exam Session Participant", {
            "parent": session.name,
            "participant": "test@example.com"
        })
        self.assertEqual(participant.status, "Submitted")
        self.assertIsNotNone(participant.answers)
        self.assertIsNotNone(participant.submitted_at)
        
        frappe.set_user("Administrator")
    
    def test_cannot_submit_if_session_not_started(self):
        """TEST: BR-SES-002 - Cannot submit if session not in progress"""
        
        session = self.create_test_session(status="Scheduled")
        
        answers = {"TEST-Q-001": "A"}
        
        frappe.set_user("test@example.com")
        
        with self.assertRaises(frappe.ValidationError) as cm:
            submit_exam_answers(session.name, answers)
        
        self.assertIn("chưa bắt đầu hoặc đã kết thúc", str(cm.exception))
        
        frappe.set_user("Administrator")
    
    def test_cannot_submit_twice(self):
        """TEST: BR-SES-005 - Cannot submit answers twice"""
        
        session = self.create_test_session(status="In Progress", start_offset_minutes=-10)
        
        answers = {"TEST-Q-001": "A"}
        
        frappe.set_user("test@example.com")
        
        # First submission
        submit_exam_answers(session.name, answers)
        
        # Try second submission
        with self.assertRaises(frappe.ValidationError) as cm:
            submit_exam_answers(session.name, answers)
        
        self.assertIn("đã nộp bài rồi", str(cm.exception))
        
        frappe.set_user("Administrator")
    
    def test_cannot_submit_incomplete_answers(self):
        """TEST: Must answer all questions"""
        
        session = self.create_test_session(status="In Progress", start_offset_minutes=-10)
        
        # Empty answers
        answers = {}
        
        frappe.set_user("test@example.com")
        
        with self.assertRaises(frappe.ValidationError) as cm:
            submit_exam_answers(session.name, answers)
        
        self.assertIn("câu hỏi chưa trả lời", str(cm.exception))
        
        frappe.set_user("Administrator")
    
    # ============================================================
    # TEST: End Session (API003)
    # ============================================================
    
    def test_end_session_success(self):
        """TEST: Successfully end session"""
        
        # Create session started 60 minutes ago (meets minimum time)
        session = self.create_test_session(status="In Progress", start_offset_minutes=-60)
        
        result = end_exam_session(session.name)
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["ended_at"])
        
        # Verify session status changed
        session.reload()
        self.assertEqual(session.status, "Completed")
        self.assertIsNotNone(session.actual_end_time)
        self.assertEqual(session.ended_by, frappe.session.user)
    
    def test_cannot_end_too_early(self):
        """TEST: BR-SES-003 - Cannot end before minimum time"""
        
        # Create session started 20 minutes ago (need 30 minimum for 60-min exam)
        session = self.create_test_session(status="In Progress", start_offset_minutes=-20)
        
        with self.assertRaises(frappe.ValidationError) as cm:
            end_exam_session(session.name, force=False)
        
        self.assertIn("chưa đạt thời gian tối thiểu", str(cm.exception))
    
    def test_force_end_session(self):
        """TEST: Can force end session early"""
        
        session = self.create_test_session(status="In Progress", start_offset_minutes=-10)
        
        result = end_exam_session(session.name, force=True)
        
        self.assertTrue(result["success"])
        
        session.reload()
        self.assertEqual(session.status, "Completed")
    
    def test_end_session_processes_incomplete_participants(self):
        """TEST: Non-submitted participants marked as incomplete"""
        
        session = self.create_test_session(status="In Progress", start_offset_minutes=-60)
        
        # Don't submit answers - participant should be marked incomplete
        result = end_exam_session(session.name)
        
        # Check participant status
        participant = frappe.get_doc("Exam Session Participant", {
            "parent": session.name,
            "participant": "test@example.com"
        })
        
        self.assertEqual(participant.status, "Incomplete")
        self.assertIsNotNone(participant.submitted_at)
    
    # ============================================================
    # TEST: Get Session Status (API004)
    # ============================================================
    
    def test_get_session_status(self):
        """TEST: Get session status and statistics"""
        
        session = self.create_test_session(status="In Progress", start_offset_minutes=-10)
        
        result = get_session_status(session.name)
        
        # Assertions
        self.assertEqual(result["status"], "In Progress")
        self.assertIsNotNone(result["remaining_time"])
        self.assertIsNotNone(result["progress"])
        self.assertEqual(result["stats"]["total"], 1)
        self.assertEqual(result["stats"]["submitted"], 0)
        self.assertEqual(result["stats"]["pending"], 1)
    
    def test_remaining_time_calculation(self):
        """TEST: CR-SES-001 - Calculate remaining time"""
        
        session = self.create_test_session(status="In Progress", start_offset_minutes=-10)
        
        remaining = session.get_remaining_time()
        
        # Should have ~50 minutes remaining (60 - 10)
        self.assertGreater(remaining, 2900)  # 48+ minutes
        self.assertLess(remaining, 3100)     # 52- minutes
    
    def test_progress_calculation(self):
        """TEST: CR-SES-002 - Calculate session progress"""
        
        session = self.create_test_session(status="In Progress", start_offset_minutes=-30)
        
        progress = session.get_progress_percentage()
        
        # Should be ~50% progress (30 of 60 minutes)
        self.assertGreater(progress, 45)
        self.assertLess(progress, 55)
    
    def test_submission_rate_calculation(self):
        """TEST: CR-SES-003 - Calculate submission rate"""
        
        session = self.create_test_session(status="In Progress", start_offset_minutes=-10)
        
        # Initially 0% submitted
        rate = session.get_submission_rate()
        self.assertEqual(rate, 0)
        
        # Submit one answer
        frappe.set_user("test@example.com")
        submit_exam_answers(session.name, {"TEST-Q-001": "A"})
        frappe.set_user("Administrator")
        
        # Should be 100% now (1/1 participants)
        session.reload()
        rate = session.get_submission_rate()
        self.assertEqual(rate, 100)


def run_tests():
    """Run all tests"""
    frappe.flags.in_test = True
    unittest.main()