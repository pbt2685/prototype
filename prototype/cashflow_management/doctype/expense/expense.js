// Copyright (c) 2026, FaceNet and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense", {
    refresh(frm) {
        // Status indicators
        if (frm.doc.approval_status === "Draft") {
            frm.page.set_indicator(__("Nháp"), "gray");
        } else if (frm.doc.approval_status === "Pending BOD") {
            frm.page.set_indicator(__("Chờ BGĐ Duyệt"), "orange");
        } else if (frm.doc.approval_status === "Approved") {
            frm.page.set_indicator(__("Đã Duyệt"), "green");
        } else if (frm.doc.approval_status === "Rejected") {
            frm.page.set_indicator(__("Từ Chối"), "red");
        }
        
        // Submit for Approval button
        if (frm.doc.approval_status === "Draft" && !frm.is_new()) {
            frm.add_custom_button(__("Gửi Duyệt"), () => {
                frappe.call({
                    method: "prototype.cashflow_management.doctype.expense.expense.submit_for_approval",
                    args: {
                        expense_name: frm.doc.name
                    },
                    callback: (r) => {
                        frm.reload_doc();
                    }
                });
            });
        }
        
        // BOD Approval buttons
        if (frm.doc.approval_status === "Pending BOD" && frappe.user_roles.includes("System Manager")) {
            frm.add_custom_button(__("Duyệt"), () => {
                frappe.prompt([
                    {
                        fieldname: "approval_notes",
                        label: __("Ghi Chú"),
                        fieldtype: "Text Editor"
                    }
                ], (values) => {
                    frappe.call({
                        method: "prototype.cashflow_management.doctype.expense.expense.approve_expense",
                        args: {
                            expense_name: frm.doc.name,
                            approval_notes: values.approval_notes
                        },
                        callback: (r) => {
                            frm.reload_doc();
                        }
                    });
                }, __("Duyệt Chi Phí"));
            }, __("BGĐ"));
            
            frm.add_custom_button(__("Từ Chối"), () => {
                frappe.prompt([
                    {
                        fieldname: "approval_notes",
                        label: __("Lý Do Từ Chối"),
                        fieldtype: "Text Editor",
                        reqd: 1
                    }
                ], (values) => {
                    frappe.call({
                        method: "prototype.cashflow_management.doctype.expense.expense.reject_expense",
                        args: {
                            expense_name: frm.doc.name,
                            approval_notes: values.approval_notes
                        },
                        callback: (r) => {
                            frm.reload_doc();
                        }
                    });
                }, __("Từ Chối Chi Phí"));
            }, __("BGĐ"));
        }
        
        // Approved expense warning
        if (frm.doc.approval_status === "Approved") {
            frm.dashboard.add_comment(
                __("Chi phí đã được duyệt - không thể chỉnh sửa hoặc xóa"),
                "green",
                true
            );
        }
        
        // R&D budget check
        if (frm.doc.category === "R&D" && frm.doc.project) {
            frappe.db.get_value("Project", frm.doc.project, ["custom_rd_budget", "custom_project_type"])
                .then(r => {
                    if (r.message && r.message.custom_rd_budget) {
                        const budget = r.message.custom_rd_budget;
                        const usage_percent = (frm.doc.amount / budget) * 100;
                        
                        frm.dashboard.add_indicator(
                            __("R&D: {0} / {1} ({2}%)", [
                                format_currency(frm.doc.amount),
                                format_currency(budget),
                                usage_percent.toFixed(1)
                            ]),
                            usage_percent > 100 ? "red" : usage_percent > 80 ? "orange" : "blue"
                        );
                    }
                });
        }
    },
    
    expense_type(frm) {
        // Clear fields when switching type
        if (frm.doc.expense_type === "Individual") {
            frm.clear_table("grouped_items");
        } else {
            frm.set_value("expense_date", null);
            frm.set_value("amount", 0);
        }
        frm.refresh_fields();
    },
    
    category(frm) {
        // Show/hide project field
        frm.refresh_fields();
    },
    
    project(frm) {
        // Fetch project type and budget
        if (frm.doc.project) {
            frappe.db.get_value("Project", frm.doc.project, ["custom_project_type", "custom_rd_budget", "assigned_team"])
                .then(r => {
                    if (r.message) {
                        if (r.message.custom_project_type !== "Internal R&D") {
                            frappe.msgprint({
                                title: __("Cảnh Báo"),
                                message: __("Dự án này không phải là dự án R&D nội bộ"),
                                indicator: "orange"
                            });
                        }
                        
                        // Auto-fill team from project
                        if (r.message.assigned_team && !frm.doc.team) {
                            frm.set_value("team", r.message.assigned_team);
                        }
                    }
                });
        }
    }
});

frappe.ui.form.on("Grouped Expense Item", {
    amount(frm, cdt, cdn) {
        // Recalculate total
        calculate_total_grouped(frm);
    },
    
    grouped_items_remove(frm, cdt, cdn) {
        // Recalculate total when item removed
        calculate_total_grouped(frm);
    }
});

function calculate_total_grouped(frm) {
    if (frm.doc.expense_type === "Grouped") {
        let total = 0;
        (frm.doc.grouped_items || []).forEach(item => {
            total += (item.amount || 0);
        });
        frm.set_value("amount", total);
    }
}
