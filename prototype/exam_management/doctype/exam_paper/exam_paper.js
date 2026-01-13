// Copyright (c) 2026, Prototype and contributors
// For license information, please see license.txt

frappe.ui.form.on('Exam Paper', {
    refresh: function(frm) {
        if (frm.doc.status === 'Draft') {
            frm.add_custom_button(__('Publish'), function() {
                frappe.call({
                    method: 'frappe.client.set_value',
                    args: {
                        doctype: 'Exam Paper',
                        name: frm.doc.name,
                        fieldname: 'status',
                        value: 'Published'
                    },
                    callback: function() {
                        frm.reload_doc();
                    }
                });
            });
        }
    }
});