// Copyright (c) 2026, FaceNet and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Schedule", {
    refresh(frm) {
        // Status indicator
        if (frm.doc.status === "Received") {
            frm.page.set_indicator(__("Đã Nhận"), "green");
        } else if (frm.doc.status === "Overdue") {
            frm.page.set_indicator(__("Quá Hạn"), "red");
        } else {
            frm.page.set_indicator(__("Chờ Thanh Toán"), "orange");
        }
        
        // Mark as Received button
        if (frm.doc.status !== "Received" && !frm.is_new()) {
            frm.add_custom_button(__("Đánh Dấu Đã Nhận"), () => {
                frappe.prompt([
                    {
                        fieldname: "actual_date",
                        label: __("Ngày Nhận Thực Tế"),
                        fieldtype: "Date",
                        default: frappe.datetime.get_today(),
                        reqd: 1
                    }
                ], (values) => {
                    frappe.call({
                        method: "prototype.cashflow_management.doctype.payment_schedule.payment_schedule.mark_as_received",
                        args: {
                            payment_schedule: frm.doc.name,
                            actual_date: values.actual_date
                        },
                        callback: (r) => {
                            frm.reload_doc();
                        }
                    });
                }, __("Đánh Dấu Đã Nhận"));
            });
        }
        
        // Delay warning
        if (frm.doc.delay_days && frm.doc.delay_days > 0) {
            frm.dashboard.add_indicator(__("Trễ {0} ngày", [frm.doc.delay_days]), "red");
        }
        
        // Calculate days until/overdue
        if (frm.doc.expected_date && frm.doc.status !== "Received") {
            const today = frappe.datetime.get_today();
            const expected = frm.doc.expected_date;
            const days_diff = frappe.datetime.get_day_diff(expected, today);
            
            if (days_diff < 0) {
                const days_overdue = Math.abs(days_diff);
                frm.dashboard.add_comment(
                    __("Quá hạn {0} ngày", [days_overdue]),
                    "red",
                    true
                );
            } else if (days_diff <= 7) {
                frm.dashboard.add_comment(
                    __("Sắp đến hạn trong {0} ngày", [days_diff]),
                    "orange",
                    true
                );
            }
        }
    },
    
    contract(frm) {
        // Fetch contract details
        if (frm.doc.contract) {
            frappe.db.get_value("Contract", frm.doc.contract, ["party_name", "custom_total_contract_value"])
                .then(r => {
                    if (r.message) {
                        frm.set_value("contract_name", r.message.party_name);
                        
                        // Suggest next milestone number
                        if (!frm.doc.milestone_number) {
                            frappe.call({
                                method: "frappe.client.get_count",
                                args: {
                                    doctype: "Payment Schedule",
                                    filters: {
                                        contract: frm.doc.contract
                                    }
                                },
                                callback: (r) => {
                                    if (r.message !== undefined) {
                                        frm.set_value("milestone_number", r.message + 1);
                                    }
                                }
                            });
                        }
                    }
                });
        }
    },
    
    amount(frm) {
        // Calculate percentage
        if (frm.doc.amount && frm.doc.contract) {
            frappe.db.get_value("Contract", frm.doc.contract, "custom_total_contract_value")
                .then(r => {
                    if (r.message && r.message.custom_total_contract_value) {
                        const percentage = (frm.doc.amount / r.message.custom_total_contract_value) * 100;
                        frm.set_value("percentage", percentage);
                    }
                });
        }
    },
    
    actual_date(frm) {
        // Auto-calculate delay when actual date is set
        if (frm.doc.actual_date && frm.doc.expected_date) {
            const delay = frappe.datetime.get_day_diff(frm.doc.actual_date, frm.doc.expected_date);
            frm.set_value("delay_days", delay > 0 ? delay : 0);
            
            if (delay > 0) {
                frappe.show_alert({
                    message: __("Thanh toán trễ {0} ngày", [delay]),
                    indicator: "orange"
                }, 5);
            }
        }
    }
});
