// Copyright (c) 2026, FaceNet and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance", {
    refresh(frm) {
        // Show late indicator
        if (frm.doc.late_minutes && frm.doc.late_minutes > 0) {
            frm.dashboard.add_indicator(__("Trễ {0} phút", [frm.doc.late_minutes]), "red");
        }
        
        // Show half-day indicator
        if (frm.doc.is_half_day) {
            frm.dashboard.add_indicator(__("Nửa Ngày"), "orange");
        }
        
        // Employee type indicator
        if (frm.doc.employee) {
            frappe.db.get_value("Employee", frm.doc.employee, "employee_type")
                .then(r => {
                    if (r.message && r.message.employee_type === "Intern") {
                        frm.dashboard.add_comment(
                            __("Thực tập sinh: Chấm công ảnh hưởng trực tiếp đến tính lương"),
                            "blue",
                            true
                        );
                    }
                });
        }
        
        // Calculate work hours button
        if (!frm.is_new() && frm.doc.check_in_time && frm.doc.check_out_time) {
            frm.add_custom_button(__("Tính Giờ Làm"), () => {
                calculate_work_hours(frm);
            });
        }
    },
    
    check_in_time(frm) {
        // Auto-calculate late minutes
        if (frm.doc.check_in_time && frm.doc.status === "Present") {
            calculate_late_minutes(frm);
        }
    },
    
    status(frm) {
        // Reset late minutes if not present
        if (frm.doc.status !== "Present") {
            frm.set_value("late_minutes", 0);
            frm.set_value("check_in_time", null);
            frm.set_value("check_out_time", null);
        }
    }
});

function calculate_late_minutes(frm) {
    // Get company start time (default 08:00)
    const company_start_time = "08:00:00";
    
    if (!frm.doc.check_in_time) {
        return;
    }
    
    // Parse times
    const check_in = moment(frm.doc.check_in_time, "HH:mm:ss");
    const start_time = moment(company_start_time, "HH:mm:ss");
    
    // Calculate difference in minutes
    const diff_minutes = check_in.diff(start_time, "minutes");
    
    // Apply 15-minute grace period
    if (diff_minutes > 15) {
        frm.set_value("late_minutes", diff_minutes);
        
        frappe.show_alert({
            message: __("Trễ {0} phút", [diff_minutes]),
            indicator: "red"
        }, 5);
    } else {
        frm.set_value("late_minutes", 0);
    }
}

function calculate_work_hours(frm) {
    if (!frm.doc.check_in_time || !frm.doc.check_out_time) {
        frappe.msgprint(__("Vui lòng nhập cả giờ vào và giờ ra"));
        return;
    }
    
    const check_in = moment(frm.doc.check_in_time, "HH:mm:ss");
    const check_out = moment(frm.doc.check_out_time, "HH:mm:ss");
    
    const work_hours = check_out.diff(check_in, "hours", true).toFixed(2);
    
    let message = __("Tổng giờ làm: {0} giờ", [work_hours]);
    
    // Check if half day
    if (work_hours < 4) {
        message += "<br>" + __("Cảnh báo: Dưới 4 giờ - xem xét đánh dấu Nửa Ngày");
        frappe.msgprint({
            title: __("Thời Gian Làm Việc"),
            message: message,
            indicator: "orange"
        });
    } else {
        frappe.msgprint({
            title: __("Thời Gian Làm Việc"),
            message: message,
            indicator: "blue"
        });
    }
}
