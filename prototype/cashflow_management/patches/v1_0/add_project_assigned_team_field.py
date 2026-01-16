# Copyright (c) 2026, FaceNet and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Add assigned_team custom field to Project DocType"""
    
    # Check if field already exists
    if frappe.db.exists("Custom Field", {"dt": "Project", "fieldname": "assigned_team"}):
        print("✓ Custom field 'assigned_team' already exists in Project")
        return
    
    custom_fields = {
        "Project": [
            {
                "fieldname": "assigned_team",
                "label": "Nhóm Phụ Trách",
                "fieldtype": "Link",
                "options": "Team",
                "insert_after": "department",
                "translatable": 0
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    print("✓ Added custom field 'assigned_team' to Project")
