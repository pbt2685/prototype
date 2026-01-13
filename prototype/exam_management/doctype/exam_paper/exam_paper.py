# Copyright (c) 2026, Prototype and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today

class ExamPaper(Document):
    def before_insert(self):
        self.created_by = frappe.session.user
        self.created_date = today()
        
    def validate(self):
        self.validate_passing_marks()
        self.calculate_total_marks()
        
    def validate_passing_marks(self):
        if self.passing_marks > self.total_marks:
            frappe.throw("Passing marks cannot be greater than total marks")
            
    def calculate_total_marks(self):
        total = 0
        if self.questions:
            for question in self.questions:
                if question.marks:
                    total += question.marks
        if total > 0 and total != self.total_marks:
            frappe.msgprint(f"Total marks from questions ({total}) differs from specified total marks ({self.total_marks})")