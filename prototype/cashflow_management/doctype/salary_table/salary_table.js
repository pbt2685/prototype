frappe.ui.form.on('Salary Table', {
    refresh: function(frm) {
        // Custom buttons based on status
        if (frm.doc.export_status === "Draft" && frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Tạo Danh Sách Lương'), function() {
                generate_salary_items(frm);
            });
            
            frm.add_custom_button(__('Duyệt Bảng Lương'), function() {
                approve_salary_table(frm);
            }).addClass('btn-primary');
        }
        
        if (frm.doc.export_status === "Approved" && frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Xuất File Ngân Hàng'), function() {
                export_to_bank(frm);
            }).addClass('btn-success');
        }
        
        // Show summary
        if (frm.doc.salary_items && frm.doc.salary_items.length > 0) {
            let message = `
                <div class="alert alert-info">
                    <strong>Tổng quan:</strong><br>
                    - Số nhân viên: ${frm.doc.salary_items.length}<br>
                    - Tổng tiền: ${format_currency(frm.doc.total_amount, frm.doc.currency)}<br>
                    - Trạng thái: ${frm.doc.export_status}
                </div>
            `;
            frm.set_intro(message);
        }
    },
    
    period_month: function(frm) {
        update_salary_table_name(frm);
    },
    
    period_year: function(frm) {
        update_salary_table_name(frm);
    }
});

function update_salary_table_name(frm) {
    // Auto-generate name based on period
    if (frm.doc.period_month && frm.doc.period_year && frm.is_new()) {
        frm.set_value('__newname', `SAL-TABLE-${frm.doc.period_year}-${frm.doc.period_month}`);
    }
}

function generate_salary_items(frm) {
    if (!frm.doc.period_month || !frm.doc.period_year) {
        frappe.msgprint(__('Vui lòng chọn tháng và năm'));
        return;
    }
    
    frappe.confirm(
        __('Tạo danh sách lương cho tất cả nhân viên?<br>Dữ liệu hiện tại sẽ bị xóa.'),
        function() {
            frappe.call({
                method: 'prototype.cashflow_management.doctype.salary_table.salary_table.generate_salary_items',
                args: {
                    salary_table_name: frm.doc.name,
                    period_month: frm.doc.period_month,
                    period_year: frm.doc.period_year
                },
                freeze: true,
                freeze_message: __('Đang tính lương...'),
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Thành Công'),
                            message: r.message.message,
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                }
            });
        }
    );
}

function approve_salary_table(frm) {
    if (frm.doc.salary_items.length === 0) {
        frappe.msgprint(__('Không có nhân viên nào trong bảng lương'));
        return;
    }
    
    frappe.confirm(
        __('Duyệt bảng lương này? Sau khi duyệt sẽ không thể chỉnh sửa.'),
        function() {
            frappe.call({
                method: 'prototype.cashflow_management.doctype.salary_table.salary_table.approve_salary_table',
                args: {
                    salary_table_name: frm.doc.name
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Thành Công'),
                            message: r.message.message,
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                }
            });
        }
    );
}

function export_to_bank(frm) {
    frappe.confirm(
        __('Xuất file Excel cho ngân hàng?'),
        function() {
            frappe.call({
                method: 'prototype.cashflow_management.doctype.salary_table.salary_table.export_to_bank_file',
                args: {
                    salary_table_name: frm.doc.name
                },
                freeze: true,
                freeze_message: __('Đang xuất file...'),
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Thành Công'),
                            message: r.message.message + '<br><a href="' + r.message.file_url + '" target="_blank">Tải file</a>',
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                }
            });
        }
    );
}

// Child table formatting
frappe.ui.form.on('Salary Table Item', {
    net_pay: function(frm, cdt, cdn) {
        // Recalculate total when net_pay changes
        frm.trigger('calculate_total');
    }
});
