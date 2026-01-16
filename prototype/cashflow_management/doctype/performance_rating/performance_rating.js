// Copyright (c) 2026, FaceNet and contributors
// For license information, please see license.txt

frappe.ui.form.on("Performance Rating", {
    refresh(frm) {
        // Status indicator
        if (frm.doc.docstatus === 1) {
            frm.page.set_indicator(__("Đã Phê Duyệt"), "green");
            
            // BOD Override button
            if (frappe.user_roles.includes("System Manager") && !frm.doc.is_overridden_by_bod) {
                frm.add_custom_button(__("Ghi Đè BOD"), () => {
                    frappe.prompt([
                        {
                            fieldname: "new_rating_score",
                            label: __("Điểm Đánh Giá Mới"),
                            fieldtype: "Select",
                            options: "1\n2\n3\n4\n5",
                            reqd: 1
                        },
                        {
                            fieldname: "bod_comments",
                            label: __("Nhận Xét BOD"),
                            fieldtype: "Text Editor",
                            reqd: 1
                        }
                    ], (values) => {
                        frappe.call({
                            method: "prototype.cashflow_management.doctype.performance_rating.performance_rating.override_rating_by_bod",
                            args: {
                                performance_rating: frm.doc.name,
                                new_rating_score: values.new_rating_score,
                                bod_comments: values.bod_comments
                            },
                            callback: (r) => {
                                if (r.message) {
                                    frappe.set_route("Form", "Performance Rating", r.message);
                                }
                            }
                        });
                    }, __("Ghi Đè Đánh Giá"));
                });
            }
        } else if (frm.doc.docstatus === 0) {
            frm.page.set_indicator(__("Nháp"), "orange");
        } else if (frm.doc.docstatus === 2) {
            frm.page.set_indicator(__("Đã Hủy"), "red");
        }
        
        // Override indicator
        if (frm.doc.is_overridden_by_bod) {
            frm.dashboard.add_indicator(__("Đã Ghi Đè Bởi BOD"), "red");
        }
        
        // Employee type warning for non-interns
        if (frm.doc.employee_type && frm.doc.employee_type !== "Intern") {
            frm.dashboard.add_comment(
                __("Lưu ý: Đánh giá hiệu suất hàng tháng chủ yếu dùng để tính lương cho Thực Tập Sinh"),
                "yellow",
                true
            );
        }
        
        // Show month format hint
        if (frm.doc.rating_period) {
            const month_year = moment(frm.doc.rating_period).format("MM/YYYY");
            frm.set_df_property("rating_period", "description", 
                __("Tháng đánh giá: {0}", [month_year]));
        }
    },
    
    employee(frm) {
        // Fetch employee details
        if (frm.doc.employee) {
            frappe.db.get_value("Employee", frm.doc.employee, ["employee_name", "employee_type", "department", "primary_team"])
                .then(r => {
                    if (r.message) {
                        frm.set_value("employee_name", r.message.employee_name);
                        frm.set_value("employee_type", r.message.employee_type);
                        frm.set_value("department", r.message.department);
                        frm.set_value("team", r.message.primary_team);
                    }
                });
        }
    },
    
    rating_score(frm) {
        // Calculate performance factor
        const factor_map = {
            "1": 0.6,
            "2": 0.8,
            "3": 1.0,
            "4": 1.2,
            "5": 1.5
        };
        
        if (frm.doc.rating_score) {
            const factor = factor_map[frm.doc.rating_score] || 1.0;
            frm.set_value("performance_factor", factor);
            
            // Show visual feedback
            let color = "red";
            let message = "";
            
            if (frm.doc.rating_score === "1") {
                color = "red";
                message = "Kém: 60% lương";
            } else if (frm.doc.rating_score === "2") {
                color = "orange";
                message = "Dưới Trung Bình: 80% lương";
            } else if (frm.doc.rating_score === "3") {
                color = "blue";
                message = "Trung Bình: 100% lương";
            } else if (frm.doc.rating_score === "4") {
                color = "green";
                message = "Tốt: 120% lương";
            } else if (frm.doc.rating_score === "5") {
                color = "darkgreen";
                message = "Xuất Sắc: 150% lương";
            }
            
            frappe.show_alert({
                message: message,
                indicator: color
            }, 5);
        }
    }
});
