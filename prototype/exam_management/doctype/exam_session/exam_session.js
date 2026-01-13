// Copyright (c) 2026, Prototype and contributors
// For license information, please see license.txt

frappe.ui.form.on('Exam Session', {
    refresh: function(frm) {
        if (frm.doc.status === 'Scheduled') {
            frm.add_custom_button(__('Start Exam'), function() {
                frappe.call({
                    method: 'frappe.client.set_value',
                    args: {
                        doctype: 'Exam Session',
                        name: frm.doc.name,
                        fieldname: 'status',
                        value: 'In Progress'
                    },
                    callback: function() {
                        frm.reload_doc();
                    }
                });
            });
        }
        
        if (frm.doc.status === 'In Progress') {
            frm.add_custom_button(__('Complete Exam'), function() {
                frappe.call({
                    method: 'frappe.client.set_value',
                    args: {
                        doctype: 'Exam Session',
                        name: frm.doc.name,
                        fieldname: 'status',
                        value: 'Completed'
                    },
                    callback: function() {
                        frm.reload_doc();
                    }
                });
            });
        }
    }
});