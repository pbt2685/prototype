# Copyright (c) 2026, Prototype and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class ExamSession(Document):
    def validate(self):
        self.calculate_duration()
        self.set_proctor_name()
        self.check_classroom_availability()
        
    def calculate_duration(self):
        if self.start_time and self.end_time:
            start = datetime.strptime(self.start_time, "%H:%M:%S")
            end = datetime.strptime(self.end_time, "%H:%M:%S")
            duration = (end - start).seconds // 60
            self.duration = duration
            
    def set_proctor_name(self):
        if self.proctor:
            self.proctor_name = frappe.db.get_value("User", self.proctor, "full_name")
            
    def check_classroom_availability(self):
        # Check if classroom is already occupied during this time
        overlapping_sessions = frappe.get_all(
            "Exam Session",
            filters={
                "name": ["!=", self.name],
                "classroom": self.classroom,
                "exam_date": self.exam_date,
                "status": ["in", ["Scheduled", "In Progress"]]
            },
            fields=["start_time", "end_time"]
        )
        
        for session in overlapping_sessions:
            if (self.start_time < session.end_time and self.end_time > session.start_time):
                frappe.throw(f"Classroom {self.classroom} is already occupied during this time")