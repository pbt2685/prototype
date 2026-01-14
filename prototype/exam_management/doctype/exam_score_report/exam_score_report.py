# Copyright (c) 2025, Your Organization and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint
import json


class ExamScoreReport(Document):
    def validate(self):
        self.validate_exam_session()      # BR-SCR-001
        self.validate_all_submitted()     # BR-SCR-002
        self.validate_passing_threshold() # BR-SCR-003
        self.check_duplicate_report()     # BR-SCR-004
    
    def before_save(self):
        self.set_report_name()
        self.load_session_data()
        self.calculate_all_scores()
        self.calculate_statistics()
        self.analyze_questions()
        self.determine_rankings()
    
    def after_insert(self):
        self.send_notification()
    
    def on_trash(self):
        self.validate_can_delete()

    def validate_exam_session(self):
        """
        BR-SCR-001: Session completion check
        Rule: Report chỉ được tạo cho phiên thi đã hoàn thành
        Error: "Không thể tạo báo cáo cho phiên thi chưa hoàn thành"
        """
        if not self.exam_session:
            return
            
        session = frappe.get_doc("Exam Session", self.exam_session)
        if session.status != "Completed":
            frappe.throw(_("Không thể tạo báo cáo cho phiên thi chưa hoàn thành"))

    def validate_all_submitted(self):
        """
        BR-SCR-002: All participants submitted
        Rule: Tất cả participants phải có status = "Submitted"
        Error: "Còn học sinh chưa nộp bài. Vui lòng chờ tất cả hoàn thành"
        """
        if not self.exam_session:
            return
            
        pending = frappe.db.count("Exam Session Participant", {
            "parent": self.exam_session,
            "status": ["!=", "Submitted"]
        })
        if pending > 0:
            frappe.throw(_("Còn {0} học sinh chưa nộp bài. Vui lòng chờ tất cả hoàn thành").format(pending))

    def validate_passing_threshold(self):
        """
        BR-SCR-003: Passing threshold range
        Rule: 0 <= passing_threshold <= 100
        Error: "Điểm chuẩn phải từ 0 đến 100"
        """
        threshold = flt(self.passing_threshold)
        if not (0 <= threshold <= 100):
            frappe.throw(_("Điểm chuẩn phải từ 0 đến 100"))

    def check_duplicate_report(self):
        """
        BR-SCR-004: Duplicate report prevention
        Rule: Mỗi exam_session chỉ có 1 active report
        Error: "Báo cáo cho phiên thi này đã tồn tại"
        """
        if self.is_new() and self.exam_session:
            existing = frappe.db.exists("Exam Score Report", {
                "exam_session": self.exam_session,
                "status": ["!=", "Archived"],
                "name": ["!=", self.name]
            })
            if existing:
                frappe.throw(_("Báo cáo cho phiên thi này đã tồn tại"))

    def validate_can_delete(self):
        """Validate if report can be deleted"""
        if self.status == "Published":
            frappe.throw(_("Không thể xóa báo cáo đã công bố"))

    def set_report_name(self):
        """Set report name from exam session"""
        if not self.report_name and self.exam_session:
            session = frappe.get_doc("Exam Session", self.exam_session)
            self.report_name = f"Báo Cáo Điểm - {session.session_name}"

    def load_session_data(self):
        """Load exam session metadata"""
        if not self.exam_session:
            return
            
        session = frappe.get_doc("Exam Session", self.exam_session)
        
        if not session.exam_paper:
            frappe.throw(_("Phiên thi chưa có đề thi"))
            
        paper = frappe.get_doc("Exam Paper", session.exam_paper)
        
        self.max_score = flt(paper.total_marks)
        self.total_questions = len(paper.questions) if paper.questions else 0
        self.total_participants = frappe.db.count("Exam Session Participant", {
            "parent": self.exam_session
        })

    def calculate_all_scores(self):
        """
        Calculate scores for all participants
        Uses: CR-SCR-001, CR-SCR-002, CR-SCR-003
        """
        if not self.exam_session:
            return
            
        participants = frappe.get_all("Exam Session Participant", {
            "parent": self.exam_session,
            "status": "Submitted"
        }, ["name", "participant", "answers", "time_taken"])
        
        # Clear existing scores
        self.participant_scores = []
        
        # Calculate each participant's score
        for participant in participants:
            score_data = self.calculate_participant_score(participant)
            if score_data:
                self.append("participant_scores", score_data)

    def calculate_participant_score(self, participant_data):
        """
        CR-SCR-001: Calculate total score
        Formula: total_score = SUM(points_earned for correct answers)
        
        CR-SCR-002: Calculate percentage
        Formula: percentage = (total_score / max_possible_score) * 100
        
        CR-SCR-003: Determine pass/fail
        Formula: pass_status = "Pass" if percentage >= passing_threshold else "Fail"
        """
        try:
            participant_doc = frappe.get_doc("Exam Session Participant", participant_data.name)
            session = frappe.get_doc("Exam Session", self.exam_session)
            paper = frappe.get_doc("Exam Paper", session.exam_paper)
            
            total_score = 0
            correct_count = 0
            
            # Parse answers JSON
            answers = {}
            if participant_doc.answers:
                try:
                    answers = json.loads(participant_doc.answers)
                except:
                    answers = {}
            
            # Calculate score for each question
            for paper_question in paper.questions:
                question = frappe.get_doc("Exam Question", paper_question.question)
                participant_answer = answers.get(paper_question.question)
                
                if participant_answer == question.correct_answer:
                    total_score += flt(paper_question.points)
                    correct_count += 1
            
            # CR-SCR-002: Calculate percentage
            percentage = (total_score / self.max_score) * 100 if self.max_score > 0 else 0
            
            # CR-SCR-003: Determine pass/fail
            pass_status = "Pass" if percentage >= flt(self.passing_threshold) else "Fail"
            
            # Get participant name
            participant_name = frappe.db.get_value("User", participant_doc.participant, "full_name")
            
            return {
                "participant": participant_doc.participant,
                "participant_name": participant_name,
                "total_score": total_score,
                "correct_answers": correct_count,
                "percentage": percentage,
                "pass_status": pass_status,
                "time_taken": participant_doc.time_taken
            }
        
        except Exception as e:
            frappe.log_error(f"Error calculating score for {participant_data.name}: {str(e)}")
            return None

    def calculate_statistics(self):
        """
        Calculate overall statistics
        Uses: CR-SCR-004, CR-SCR-005
        """
        if not self.participant_scores:
            return
        
        scores = [flt(row.total_score) for row in self.participant_scores]
        
        if not scores:
            return
        
        # CR-SCR-004: Calculate average
        self.average_score = sum(scores) / len(scores)
        
        self.highest_score = max(scores)
        self.lowest_score = min(scores)
        
        # CR-SCR-005: Calculate standard deviation
        if len(scores) > 1:
            variance = sum((x - self.average_score) ** 2 for x in scores) / len(scores)
            self.std_deviation = variance ** 0.5
        else:
            self.std_deviation = 0
        
        # Calculate pass rate
        self.pass_count = sum(1 for row in self.participant_scores if row.pass_status == "Pass")
        self.pass_rate = (self.pass_count / len(self.participant_scores)) * 100 if self.participant_scores else 0

    def analyze_questions(self):
        """
        CR-SCR-007: Calculate question statistics
        Formula: correct_rate = (correct_count / total_attempts) * 100
        """
        if not self.exam_session:
            return
            
        session = frappe.get_doc("Exam Session", self.exam_session)
        
        if not session.exam_paper:
            return
            
        paper = frappe.get_doc("Exam Paper", session.exam_paper)
        
        # Clear existing analysis
        self.question_analysis = []
        
        for paper_question in paper.questions:
            try:
                question = frappe.get_doc("Exam Question", paper_question.question)
                
                correct_count = 0
                total_attempts = len(self.participant_scores)
                
                # Count correct answers
                for score_row in self.participant_scores:
                    participant_doc = frappe.get_doc("Exam Session Participant", {
                        "exam_session": self.exam_session,
                        "participant": score_row.participant
                    })
                    
                    answers = {}
                    if participant_doc.answers:
                        try:
                            answers = json.loads(participant_doc.answers)
                        except:
                            pass
                    
                    if answers.get(paper_question.question) == question.correct_answer:
                        correct_count += 1
                
                # Calculate correct percentage
                correct_percentage = (correct_count / total_attempts) * 100 if total_attempts > 0 else 0
                
                # Determine difficulty level
                if correct_percentage >= 80:
                    difficulty = "Easy"
                elif correct_percentage >= 50:
                    difficulty = "Medium"
                else:
                    difficulty = "Hard"
                
                self.append("question_analysis", {
                    "question": paper_question.question,
                    "question_text": question.question_text[:100] if question.question_text else "",
                    "correct_count": correct_count,
                    "total_attempts": total_attempts,
                    "correct_percentage": correct_percentage,
                    "difficulty_level": difficulty
                })
            
            except Exception as e:
                frappe.log_error(f"Error analyzing question {paper_question.question}: {str(e)}")
                continue

    def determine_rankings(self):
        """
        CR-SCR-006: Calculate ranking
        Formula: rank = ORDER BY total_score DESC
        """
        if not self.participant_scores:
            return
        
        # Sort by score descending
        sorted_scores = sorted(
            self.participant_scores,
            key=lambda x: flt(x.total_score),
            reverse=True
        )
        
        # Assign ranks (handle ties)
        current_rank = 1
        previous_score = None
        
        for idx, score_row in enumerate(sorted_scores):
            if previous_score is not None and flt(score_row.total_score) < previous_score:
                current_rank = idx + 1
            
            score_row.rank = current_rank
            previous_score = flt(score_row.total_score)

    def send_notification(self):
        """Send notification to teachers"""
        try:
            session = frappe.get_doc("Exam Session", self.exam_session)
            
            # Get teachers - adjust based on your permission structure
            teachers = frappe.get_all("User", {
                "role_profile_name": ["in", ["Teacher", "Exam Administrator"]]
            }, ["name", "email"])
            
            for teacher in teachers:
                if teacher.email:
                    frappe.sendmail(
                        recipients=[teacher.email],
                        subject=_("Báo cáo điểm đã sẵn sàng - {0}").format(session.session_name),
                        message=_("Báo cáo điểm cho phiên thi {0} đã được tạo. Vui lòng kiểm tra.").format(
                            session.session_name
                        ),
                        reference_doctype=self.doctype,
                        reference_name=self.name
                    )
        except Exception as e:
            frappe.log_error(f"Error sending notification: {str(e)}")


# ============================================================
# WHITELISTED METHODS (API)
# ============================================================

@frappe.whitelist()
def generate_report_for_session(exam_session):
    """
    API: Generate score report for exam session
    Permission: Exam Administrator, Teacher
    """
    # Validate session
    session = frappe.get_doc("Exam Session", exam_session)
    if session.status != "Completed":
        frappe.throw(_("Phiên thi chưa hoàn thành"))
    
    # Check if report exists
    existing = frappe.db.exists("Exam Score Report", {
        "exam_session": exam_session,
        "status": ["!=", "Archived"]
    })
    
    if existing:
        return {"exists": True, "name": existing}
    
    # Create report
    report = frappe.get_doc({
        "doctype": "Exam Score Report",
        "exam_session": exam_session,
        "passing_threshold": 50
    })
    report.insert()
    frappe.db.commit()
    
    return {"exists": False, "name": report.name}


@frappe.whitelist()
def get_student_score(exam_session, student=None):
    """
    API: Get student's own score
    Permission: Student (own only)
    BR-SCR-005: Access control
    """
    if not student:
        student = frappe.session.user
    
    # Validate student can only see their own score
    if frappe.session.user != student and "Exam Administrator" not in frappe.get_roles():
        frappe.throw(_("Bạn không có quyền xem điểm của học sinh khác"))
    
    report_name = frappe.db.get_value("Exam Score Report", {
        "exam_session": exam_session,
        "status": "Published"
    })
    
    if not report_name:
        frappe.throw(_("Báo cáo điểm chưa được công bố"))
    
    report = frappe.get_doc("Exam Score Report", report_name)
    
    for score in report.participant_scores:
        if score.participant == student:
            return {
                "total_score": score.total_score,
                "percentage": score.percentage,
                "rank": score.rank,
                "pass_status": score.pass_status,
                "correct_answers": score.correct_answers,
                "total_questions": report.total_questions
            }
    
    frappe.throw(_("Không tìm thấy điểm"))


@frappe.whitelist()
def publish_report(report_name):
    """Publish report to students"""
    report = frappe.get_doc("Exam Score Report", report_name)
    
    if report.status == "Published":
        frappe.throw(_("Báo cáo đã được công bố"))
    
    report.status = "Published"
    report.save()
    frappe.db.commit()
    
    return {"success": True}


@frappe.whitelist()
def generate_pdf_report(report_name):
    """Generate PDF report"""
    # TODO: Implement PDF generation using frappe.utils.pdf
    frappe.throw(_("Chức năng xuất PDF đang được phát triển"))


@frappe.whitelist()
def export_to_excel(report_name):
    """Export to Excel"""
    # TODO: Implement Excel export
    frappe.throw(_("Chức năng xuất Excel đang được phát triển"))