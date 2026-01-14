# Copyright (c) 2025, Your Organization and Contributors
# See license.txt

import unittest
import frappe
import json
from frappe.utils import today, now_datetime, add_days


class TestExamScoreReport(unittest.TestCase):
    def setUp(self):
        """Create test data"""
        self.cleanup_test_data()
        self.create_test_questions()
        self.create_test_paper()
        self.create_test_session()
        self.create_test_participants()
    
    def tearDown(self):
        """Clean up test data"""
        self.cleanup_test_data()
    
    def cleanup_test_data(self):
        """Remove test data"""
        frappe.db.delete("Exam Score Report", {"report_name": ["like", "Test%"]})
        frappe.db.delete("Exam Session", {"session_name": ["like", "Test%"]})
        frappe.db.delete("Exam Paper", {"exam_name": ["like", "Test%"]})
        frappe.db.delete("Exam Question", {"question_text": ["like", "Test%"]})
        frappe.db.commit()
    
    def create_test_questions(self):
        """Create test questions"""
        self.questions = []
        
        for i in range(1, 11):
            question = frappe.get_doc({
                "doctype": "Exam Question",
                "question_code": f"Test Question {i}",
                "marks": 1,
                "question_text": f"Test Question {i}",
                "question_type": "Trắc nghiệm",
                "option_a": "A",
                "option_b": "B",
                "option_c": "C",
                "option_d": "D",
                "correct_answer": "A"
            })
            question.insert(ignore_permissions=True)
            self.questions.append(question.name)
        
        frappe.db.commit()
    
    def create_test_paper(self):
        """Create test exam paper"""
        paper = frappe.get_doc({
            "doctype": "Exam Paper",
            "exam_code": "Test Exam Paper Code",
            "exam_name": "Test Exam Paper Name",
            "total_points": 100,
            "questions": [],
            "duration": 120,
        })
        
        # Add questions
        for question in self.questions:
            paper.append("questions", {
                "question": question,
                "question_number": len(paper.questions) + 1,
                "points": 10
            })
        
        paper.insert(ignore_permissions=True)
        self.paper_name = paper.name
        frappe.db.commit()
    
    def create_test_session(self):
        """Create test exam session"""
        session = frappe.get_doc({
            "doctype": "Exam Session",
            "session_name": "Test Session for Report",
            "exam_paper": self.paper_name,
            "exam_date": today(),
            "start_time": "09:00:00",
            "end_time": "11:00:00",
            "duration": 120,
            "status": "Completed"
        })
        session.insert(ignore_permissions=True)
        self.session_name = session.name
        frappe.db.commit()
    
    def create_test_participants(self):
        """Create test participants with answers"""
        # Create users if they don't exist
        for i in range(1, 6):
            email = f"teststudent{i}@example.com"
            if not frappe.db.exists("User", email):
                user = frappe.get_doc({
                    "doctype": "User",
                    "email": email,
                    "first_name": f"Test Student {i}",
                    "send_welcome_email": 0
                })
                user.insert(ignore_permissions=True)
        
        # Create participants
        for i in range(1, 6):
            # Simulate different score levels
            answers = {}
            for j, question in enumerate(self.questions):
                # First 3 students get all correct
                # 4th student gets 50% correct
                # 5th student gets 20% correct
                if i <= 3:
                    answers[question] = "A"  # All correct
                elif i == 4:
                    answers[question] = "A" if j % 2 == 0 else "B"  # 50% correct
                else:
                    answers[question] = "A" if j < 2 else "B"  # 20% correct
            
            participant = frappe.get_doc({
                "doctype": "Exam Session Participant",
                "exam_session": self.session_name,
                "participant": f"teststudent{i}@example.com",
                "status": "Submitted",
                "parent": self.session_name,
                "parenttype": "Exam Session",
                "answers": json.dumps(answers),
                "time_taken": 3600  # 1 hour
            })
            participant.insert(ignore_permissions=True)
        
        frappe.db.commit()
    
    # ============================================================
    # TEST CASES
    # ============================================================
    
    def test_creation(self):
        """TEST: Create report with valid session"""
        report = frappe.get_doc({
            "doctype": "Exam Score Report",
            "exam_session": self.session_name,
            "passing_threshold": 50
        })
        report.insert(ignore_permissions=True)
        
        self.assertTrue(report.name)
        self.assertEqual(report.total_participants, 5)
        self.assertEqual(report.total_questions, 10)
        self.assertEqual(report.max_score, 100)
    
    def test_validation_incomplete_session(self):
        """TEST: BR-SCR-001 - Cannot create for incomplete session"""
        # Create incomplete session
        session = frappe.get_doc({
            "doctype": "Exam Session",
            "session_name": "Test Incomplete Session",
            "exam_paper": self.paper_name,
            "session_date": today(),
            "status": "In Progress"
        })
        session.insert(ignore_permissions=True)
        
        report = frappe.get_doc({
            "doctype": "Exam Score Report",
            "exam_session": session.name,
            "passing_threshold": 50
        })
        
        with self.assertRaises(frappe.ValidationError):
            report.insert(ignore_permissions=True)
    
    def test_validation_passing_threshold(self):
        """TEST: BR-SCR-003 - Passing threshold range"""
        report = frappe.get_doc({
            "doctype": "Exam Score Report",
            "exam_session": self.session_name,
            "passing_threshold": 150
        })
        
        with self.assertRaises(frappe.ValidationError):
            report.insert(ignore_permissions=True)
        
        # Test negative threshold
        report2 = frappe.get_doc({
            "doctype": "Exam Score Report",
            "exam_session": self.session_name,
            "passing_threshold": -10
        })
        
        with self.assertRaises(frappe.ValidationError):
            report2.insert(ignore_permissions=True)
    
    def test_duplicate_prevention(self):
        """TEST: BR-SCR-004 - Prevent duplicate reports"""
        # Create first report
        report1 = frappe.get_doc({
            "doctype": "Exam Score Report",
            "exam_session": self.session_name,
            "passing_threshold": 50
        })
        report1.insert(ignore_permissions=True)
        
        # Try to create second report
        report2 = frappe.get_doc({
            "doctype": "Exam Score Report",
            "exam_session": self.session_name,
            "passing_threshold": 50
        })
        
        with self.assertRaises(frappe.ValidationError):
            report2.insert(ignore_permissions=True)
    
    def test_score_calculation(self):
        """TEST: CR-SCR-001, CR-SCR-002, CR-SCR-003"""
        report = frappe.get_doc({
            "doctype": "Exam Score Report",
            "exam_session": self.session_name,
            "passing_threshold": 50,
            "participant_scores": []
        })
        report.insert(ignore_permissions=True)
        
        # Check participant scores calculated
        self.assertEqual(len(report.participant_scores), 5)
        
        # Check first 3 students have 100%
        for i in range(3):
            score = report.participant_scores[i]
            self.assertEqual(score.total_score, 100)
            self.assertEqual(score.percentage, 100)
            self.assertEqual(score.pass_status, "Pass")
            self.assertEqual(score.correct_answers, 10)
        
        # Check 4th student has 50%
        score4 = report.participant_scores[3]
        self.assertEqual(score4.total_score, 50)
        self.assertEqual(score4.percentage, 50)
        self.assertEqual(score4.pass_status, "Pass")
        
        # Check 5th student has 20%
        score5 = report.participant_scores[4]
        self.assertEqual(score5.total_score, 20)
        self.assertEqual(score5.percentage, 20)
        self.assertEqual(score5.pass_status, "Fail")
    
    def test_statistics_calculation(self):
        """TEST: CR-SCR-004, CR-SCR-005"""
        report = frappe.get_doc({
            "doctype": "Exam Score Report",
            "exam_session": self.session_name,
            "passing_threshold": 50
        })
        report.insert(ignore_permissions=True)
        
        # Average = (100 + 100 + 100 + 50 + 20) / 5 = 74
        self.assertEqual(report.average_score, 74)
        self.assertEqual(report.highest_score, 100)
        self.assertEqual(report.lowest_score, 20)
        
        # Pass count = 4 (first 4 students)
        self.assertEqual(report.pass_count, 4)
        self.assertEqual(report.pass_rate, 80)
        
        # Standard deviation should be calculated
        self.assertGreater(report.std_deviation, 0)
    
    def test_ranking_calculation(self):
        """TEST: CR-SCR-006"""
        report = frappe.get_doc({
            "doctype": "Exam Score Report",
            "exam_session": self.session_name,
            "passing_threshold": 50
        })
        report.insert(ignore_permissions=True)
        
        # Check ranks are assigned
        ranks = [score.rank for score in report.participant_scores]
        self.assertTrue(all(rank is not None for rank in ranks))
        
        # Check ranks are sequential
        sorted_ranks = sorted(ranks)
        self.assertEqual(sorted_ranks, list(range(1, 6)))
        
        # Check highest scorers have rank 1 (may be tied)
        for score in report.participant_scores:
            if score.total_score == 100:
                self.assertEqual(score.rank, 1)
    
    def test_question_analysis(self):
        """TEST: CR-SCR-007"""
        report = frappe.get_doc({
            "doctype": "Exam Score Report",
            "exam_session": self.session_name,
            "passing_threshold": 50
        })
        report.insert(ignore_permissions=True)
        
        # Should have analysis for all questions
        self.assertEqual(len(report.question_analysis), 10)
        
        # Check analysis fields
        for analysis in report.question_analysis:
            self.assertIsNotNone(analysis.correct_count)
            self.assertIsNotNone(analysis.total_attempts)
            self.assertIsNotNone(analysis.correct_percentage)
            self.assertIn(analysis.difficulty_level, ["Easy", "Medium", "Hard"])
            self.assertEqual(analysis.total_attempts, 5)
    
    def test_api_generate_report(self):
        """TEST: API generate_report_for_session"""
        from prototype.exam_management.doctype.exam_score_report.exam_score_report import generate_report_for_session
        
        result = generate_report_for_session(self.session_name)
        
        self.assertFalse(result["exists"])
        self.assertTrue(result["name"])
        
        # Try to generate again - should return existing
        result2 = generate_report_for_session(self.session_name)
        self.assertTrue(result2["exists"])
    
    def test_api_get_student_score(self):
        """TEST: API get_student_score and BR-SCR-005"""
        from prototype.exam_management.doctype.exam_score_report.exam_score_report import get_student_score, publish_report
        
        # Create and publish report
        report = frappe.get_doc({
            "doctype": "Exam Score Report",
            "exam_session": self.session_name,
            "passing_threshold": 50
        })
        report.insert(ignore_permissions=True)
        
        publish_report(report.name)
        
        # Get student score
        frappe.set_user("teststudent1@example.com")
        score = get_student_score(self.session_name)
        
        self.assertIsNotNone(score)
        self.assertEqual(score["total_score"], 100)
        self.assertEqual(score["percentage"], 100)
        self.assertEqual(score["pass_status"], "Pass")
        
        # Reset user
        frappe.set_user("Administrator")


# Run tests
def run_tests():
    """Helper to run tests"""
    frappe.test_runner.run_tests("prototype.exam_management.doctype.exam_score_report.test_exam_score_report")