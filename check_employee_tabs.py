#!/usr/bin/env python3
import frappe

frappe.init(site='localhost')
frappe.connect()

meta = frappe.get_meta('Employee')

print('\n=== Employee Tabs/Sections ===')
for field in meta.fields:
    if field.fieldtype in ['Tab Break', 'Section Break']:
        print(f'{field.fieldtype}: {field.fieldname} - "{field.label}"')

print('\n=== Custom Fields ===')
for field in meta.fields:
    if field.fieldname.startswith('custom_'):
        print(f'{field.fieldtype}: {field.fieldname} - "{field.label}" (insert_after: {getattr(field, "insert_after", "N/A")})')
