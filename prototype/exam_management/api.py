# Copyright (c) 2026, Your Organization and contributors
# For license information, please see license.txt

"""
API methods for Exam Session Lifecycle (F005)
Provides whitelisted methods for session management
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date, get_datetime, time_diff_in_seconds
import json


# ============================================================
# API001: Start Exam Session
# ============================================================

@frappe.whitelist()
def start_exam_session(session_id):
    """
    Start an exam session and enable answer submission
    
    Args:
        session_id: Name of Exam Session document
    
    Returns:
        {
            "success": True,
            "session_id": str,
            "started_at": datetime,
            "participants_notified": int
        }
    
    Permission: Exam Administrator, Teacher
    Business Rule: BR-SES-001
    """
    
    # Validation 1: Session exists
    if not frappe.db.exists("Exam Session", session_id):
        frappe.throw(_("Phiên thi không tồn tại"))
    
    # Validation 2: Permission
    if not has_permission_to_start_session():
        frappe.throw(_("Bạn không có quyền bắt đầu phiên thi"), frappe.PermissionError)
    
    # Get session
    session = frappe.get_doc("Exam Session", session_id)
    
    # Validation 3: Can start check
    can_start, message = session.can_start()
    if not can_start:
        frappe.throw(message)
    
    # Start the session
    session.start_session()
    
    # Send notifications
    participant_count = send_session_start_notifications(session)
    
    # Log action
    frappe.logger().info(f"Session {session_id} started by {frappe.session.user}")
    
    return {
        "success": True,
        "session_id": session_id,
        "started_at": session.actual_start_time,
        "participants_notified": participant_count
    }


def has_permission_to_start_session():
    """Check if user has permission to start session"""
    roles = frappe.get_roles()
    return "Exam Administrator" in roles or "Teacher" in roles


def send_session_start_notifications(session):
    """Send notifications to participants about session start"""
    participant_count = 0
    
    for participant_row in session.participants:
        try:
            # Create notification
            frappe.get_doc({
                "doctype": "Notification Log",
                "for_user": participant_row.participant,
                "type": "Alert",
                "document_type": "Exam Session",
                "document_name": session.name,
                "subject": _("Phiên thi {0} đã bắt đầu").format(session.name),
                "email_content": _("""
                    Phiên thi đã bắt đầu. Vui lòng truy cập để làm bài.
                    
                    Đề thi: {0}
                    Thời gian: {1} phút
                    Bắt đầu: {2}
                    
                    Truy cập: /exam/{3}/take
                """).format(
                    session.exam_paper,
                    session.duration,
                    session.actual_start_time,
                    session.name
                )
            }).insert(ignore_permissions=True)
            participant_count += 1
        except Exception as e:
            frappe.log_error(f"Failed to send notification to {participant_row.participant}: {str(e)}")
    
    return participant_count


# ============================================================
# API002: Submit Exam Answers
# ============================================================

@frappe.whitelist()
def submit_exam_answers(session_id, answers):
    """
    Submit exam answers for a participant
    
    Args:
        session_id: Name of Exam Session document
        answers: Dict or JSON string of {question_id: answer_value}
    
    Returns:
        {
            "success": True,
            "submitted_at": datetime,
            "time_taken": int (seconds),
            "total_questions": int,
            "answered_questions": int
        }
    
    Permission: Student (own only)
    Business Rules: BR-SES-002, BR-SES-005
    """
    
    # Parse answers if string
    if isinstance(answers, str):
        try:
            answers = json.loads(answers)
        except:
            frappe.throw(_("Dữ liệu câu trả lời không hợp lệ"))
    
    # Validation 1: Session exists
    if not frappe.db.exists("Exam Session", session_id):
        frappe.throw(_("Phiên thi không tồn tại"))
    
    session = frappe.get_doc("Exam Session", session_id)
    
    # Validation 2: Session status (BR-SES-002)
    if session.status != "In Progress":
        frappe.throw(_("Phiên thi chưa bắt đầu hoặc đã kết thúc. Không thể nộp bài"))
    
    # Validation 3: User is participant
    participant_name = frappe.db.get_value("Exam Session Participant", {
        "parent": session_id,
        "participant": frappe.session.user
    })
    
    if not participant_name:
        frappe.throw(_("Bạn không phải thí sinh của phiên thi này"), frappe.PermissionError)
    
    participant = frappe.get_doc("Exam Session Participant", participant_name)
    
    # Validation 4: Not already submitted (BR-SES-005)
    if participant.status == "Submitted":
        frappe.throw(_("Bạn đã nộp bài rồi. Không thể nộp lại"))
    
    # Validation 5: Check time limit
    if session.actual_end_time and now_datetime() > session.actual_end_time:
        frappe.throw(_("Phiên thi đã kết thúc. Không thể nộp bài"))
    
    # Validation 6: Validate all questions answered
    paper = frappe.get_doc("Exam Paper", session.exam_paper)
    required_questions = set([q.question for q in paper.questions])
    answered_questions = set(answers.keys())
    
    missing = required_questions - answered_questions
    if missing:
        frappe.throw(_("Còn {0} câu hỏi chưa trả lời").format(len(missing)))
    
    # Update participant
    submission_time = now_datetime()
    time_taken = time_diff_in_seconds(submission_time, session.actual_start_time)
    
    participant.status = "Submitted"
    participant.answers = json.dumps(answers)
    participant.submitted_at = submission_time
    participant.time_taken = time_taken
    participant.save(ignore_permissions=True)
    
    # Update session submitted count
    session.reload()
    session.update_participant_count()
    session.save(ignore_permissions=True)
    
    # Log submission
    frappe.logger().info(
        f"Participant {frappe.session.user} submitted answers for session {session_id}"
    )
    
    # Check if all submitted
    all_submitted = (session.submitted_count == session.total_participants)
    
    frappe.db.commit()
    
    return {
        "success": True,
        "submitted_at": submission_time,
        "time_taken": time_taken,
        "total_questions": len(required_questions),
        "answered_questions": len(answered_questions),
        "all_submitted": all_submitted
    }


# ============================================================
# API003: End Exam Session
# ============================================================

@frappe.whitelist()
def end_exam_session(session_id, force=False):
    """
    End exam session and generate score report
    
    Args:
        session_id: Name of Exam Session document
        force: Skip minimum time validation (default: False)
    
    Returns:
        {
            "success": True,
            "ended_at": datetime,
            "report_generated": bool,
            "report_name": str,
            "stats": {
                "submitted": int,
                "incomplete": int,
                "total": int
            }
        }
    
    Permission: Exam Administrator, Teacher
    Business Rules: BR-SES-003, BR-SES-006
    """
    
    # Convert force to bool
    force = frappe.parse_json(force) if isinstance(force, str) else force
    
    # Validation 1: Session exists
    if not frappe.db.exists("Exam Session", session_id):
        frappe.throw(_("Phiên thi không tồn tại"))
    
    # Validation 2: Permission
    if not has_permission_to_end_session():
        frappe.throw(_("Bạn không có quyền kết thúc phiên thi"), frappe.PermissionError)
    
    # Get session
    session = frappe.get_doc("Exam Session", session_id)
    
    # Validation 3: Can end check
    can_end, message = session.can_end(force)
    if not can_end:
        frappe.throw(message)
    
    # End the session
    session.end_session(force)
    
    # Get final stats
    stats = {
        "total": session.total_participants,
        "submitted": session.submitted_count,
        "incomplete": session.total_participants - session.submitted_count
    }
    
    # Try to generate score report (BR-SES-006)
    report_name = None
    report_generated = False
    
    try:
        from prototype.exam_management.doctype.exam_score_report.exam_score_report import generate_report_for_session
        
        report_result = generate_report_for_session(session_id)
        report_name = report_result.get("name")
        report_generated = not report_result.get("exists", False)
    except Exception as e:
        frappe.log_error(f"Failed to generate report: {str(e)}")
    
    # Send notifications
    send_session_end_notifications(session, stats)
    
    # Log action
    frappe.logger().info(
        f"Session {session_id} ended by {frappe.session.user}. Stats: {stats}"
    )
    
    return {
        "success": True,
        "ended_at": session.actual_end_time,
        "report_generated": report_generated,
        "report_name": report_name,
        "stats": stats
    }


def has_permission_to_end_session():
    """Check if user has permission to end session"""
    roles = frappe.get_roles()
    return "Exam Administrator" in roles or "Teacher" in roles


def send_session_end_notifications(session, stats):
    """Send notifications about session end"""
    
    # Notify organizers
    organizers = frappe.get_all("User", {
        "role_profile_name": ["in", ["Exam Administrator", "Teacher"]]
    }, ["name"])
    
    for org in organizers:
        try:
            frappe.get_doc({
                "doctype": "Notification Log",
                "for_user": org.name,
                "type": "Alert",
                "document_type": "Exam Session",
                "document_name": session.name,
                "subject": _("Phiên thi {0} đã kết thúc").format(session.name),
                "email_content": _("""
                    Phiên thi đã kết thúc.
                    
                    Tổng số: {total}
                    Đã nộp: {submitted}
                    Chưa hoàn thành: {incomplete}
                    
                    Báo cáo điểm đang được tạo.
                """).format(**stats)
            }).insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Failed to send notification: {str(e)}")


# ============================================================
# API004: Get Session Status
# ============================================================

@frappe.whitelist()
def get_session_status(session_id):
    """
    Get current session status and statistics
    
    Args:
        session_id: Name of Exam Session document
    
    Returns:
        {
            "status": str,
            "remaining_time": int (seconds),
            "progress": float (percentage),
            "stats": {
                "total": int,
                "submitted": int,
                "pending": int,
                "pending_participants": [names]
            }
        }
    
    Permission: Exam Administrator, Teacher, Participant
    Calculation Rules: CR-SES-001, CR-SES-002, CR-SES-003
    """
    
    # Validation: Session exists
    if not frappe.db.exists("Exam Session", session_id):
        frappe.throw(_("Phiên thi không tồn tại"))
    
    session = frappe.get_doc("Exam Session", session_id)
    
    # Check permission
    is_organizer = has_permission_to_view_session(session)
    is_participant = frappe.db.exists("Exam Session Participant", {
        "parent": session_id,
        "participant": frappe.session.user
    })
    
    if not (is_organizer or is_participant):
        frappe.throw(_("Bạn không có quyền xem thông tin phiên thi này"), frappe.PermissionError)
    
    # Calculate remaining time (CR-SES-001)
    remaining_time = session.get_remaining_time()
    
    # Calculate progress (CR-SES-002)
    progress = session.get_progress_percentage()
    
    # Get statistics
    session.update_participant_count()
    
    stats = {
        "total": session.total_participants,
        "submitted": session.submitted_count,
        "pending": session.total_participants - session.submitted_count
    }
    
    # Get pending participant names (only for organizers)
    if is_organizer:
        pending_participants = frappe.get_all("Exam Session Participant", {
            "parent": session_id,
            "status": ["!=", "Submitted"]
        }, ["participant"])
        
        stats["pending_participants"] = [
            frappe.db.get_value("User", p.participant, "full_name") 
            for p in pending_participants
        ]
    
    return {
        "status": session.status,
        "remaining_time": remaining_time,
        "progress": progress,
        "stats": stats
    }


def has_permission_to_view_session(session):
    """Check if user can view full session details"""
    roles = frappe.get_roles()
    return ("Exam Administrator" in roles or 
            "Teacher" in roles or 
            session.proctor == frappe.session.user)


# ============================================================
# Scheduled Job: Auto-End Expired Sessions
# ============================================================

def auto_end_expired_sessions():
    """
    Auto-end sessions that have exceeded duration (BR-SES-004)
    
    Scheduled: Every 1 minute (cron: * * * * *)
    """
    
    # Find sessions that should be ended
    sessions = frappe.get_all("Exam Session", {
        "status": "In Progress"
    }, ["name", "actual_start_time", "duration"])
    
    for s in sessions:
        try:
            expected_end = add_to_date(
                s.actual_start_time,
                minutes=s.duration
            )
            
            if now_datetime() >= expected_end:
                frappe.logger().info(f"Auto-ending expired session {s.name}")
                end_exam_session(s.name, force=True)
        
        except Exception as e:
            frappe.log_error(
                f"Failed to auto-end session {s.name}: {str(e)}",
                "Auto End Session Error"
            )


# ============================================================
# Utility: Get Exam Questions for Participant
# ============================================================

@frappe.whitelist()
def get_exam_questions(session_id):
    """
    Get exam questions for participant to display in exam interface
    
    Args:
        session_id: Name of Exam Session
    
    Returns:
        {
            "session_name": str,
            "duration": int,
            "questions": [
                {
                    "id": str,
                    "text": str,
                    "question_type": str,
                    "options": [str],
                    "points": float
                }
            ]
        }
    
    Permission: Participant only, session must be In Progress
    """
    
    # Validation: Session exists and is active
    session = frappe.get_doc("Exam Session", session_id)
    
    if session.status != "In Progress":
        frappe.throw(_("Phiên thi chưa bắt đầu hoặc đã kết thúc"))
    
    # Validation: User is participant
    is_participant = frappe.db.exists("Exam Session Participant", {
        "parent": session_id,
        "participant": frappe.session.user
    })
    
    if not is_participant:
        frappe.throw(_("Bạn không phải thí sinh của phiên thi này"), frappe.PermissionError)
    
    # Get exam paper
    paper = frappe.get_doc("Exam Paper", session.exam_paper)
    
    # Build questions list
    questions = []
    for pq in paper.questions:
        question = frappe.get_doc("Exam Question", pq.question)
        
        questions.append({
            "id": question.name,
            "text": question.question_text,
            "question_type": question.question_type,
            "options": [
                question.option_a,
                question.option_b,
                question.option_c,
                question.option_d
            ] if question.question_type == "Multiple Choice" else [],
            "points": pq.points
        })
    
    return {
        "session_name": session.name,
        "duration": session.duration,
        "questions": questions,
        "remaining_time": session.get_remaining_time()
    }