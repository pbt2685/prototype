frappe.ui.form.on('Debt Management', {
    refresh: function(frm) {
        // Color-code by escalation level
        let level_color = {
            "0 - Monitoring": "blue",
            "1 - Account Manager": "yellow",
            "2 - Finance Manager": "orange",
            "3 - CFO/Legal": "red"
        };
        
        let color = level_color[frm.doc.escalation_level] || "gray";
        frm.set_intro(__(`Mức độ leo thang: ${frm.doc.escalation_level}`), color);
        
        // Show days overdue prominently
        if (frm.doc.days_overdue > 0) {
            frm.dashboard.add_indicator(
                __(`Quá hạn ${frm.doc.days_overdue} ngày`), 
                "red"
            );
        }
        
        // Show payment probability
        if (frm.doc.payment_probability) {
            frm.dashboard.add_indicator(
                __(`Xác suất thu hồi: ${frm.doc.payment_probability}%`),
                frm.doc.payment_probability >= 80 ? "green" : "orange"
            );
        }
        
        // Custom buttons
        if (frm.doc.current_status !== "Resolved" && !frm.is_new()) {
            frm.add_custom_button(__('Tạo Hành Động Thu Hồi'), function() {
                create_collection_action(frm);
            });
            
            frm.add_custom_button(__('Đánh Dấu Đã Giải Quyết'), function() {
                mark_resolved(frm);
            }).addClass('btn-success');
        }
        
        // Show collection actions
        if (!frm.is_new()) {
            show_collection_actions(frm);
        }
    }
});

function create_collection_action(frm) {
    frappe.new_doc('Collection Action', {
        debt: frm.doc.name,
        customer: frm.doc.customer,
        action_date: frappe.datetime.nowdate(),
        action_status: 'Planned'
    });
}

function mark_resolved(frm) {
    if (frm.doc.outstanding_amount > 0) {
        frappe.msgprint(__('Không thể đóng công nợ khi còn số tiền chưa thanh toán'));
        return;
    }
    
    frappe.confirm(
        __('Đánh dấu công nợ này đã được giải quyết?'),
        function() {
            frappe.call({
                method: 'frappe.client.set_value',
                args: {
                    doctype: 'Debt Management',
                    name: frm.doc.name,
                    fieldname: 'current_status',
                    value: 'Resolved'
                },
                callback: function() {
                    frappe.msgprint({
                        title: __('Thành Công'),
                        message: __('Đã đánh dấu công nợ đã giải quyết'),
                        indicator: 'green'
                    });
                    frm.reload_doc();
                }
            });
        }
    );
}

function show_collection_actions(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Collection Action',
            filters: { debt: frm.doc.name },
            fields: ['name', 'action_type', 'action_date', 'action_status', 'outcome'],
            order_by: 'action_date desc',
            limit: 10
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let html = '<h4>Lịch Sử Hành Động Thu Hồi</h4><table class="table table-bordered"><thead><tr><th>Ngày</th><th>Loại</th><th>Trạng Thái</th><th>Kết Quả</th></tr></thead><tbody>';
                
                r.message.forEach(function(action) {
                    let status_color = action.action_status === 'Completed' ? 'success' : 
                                     action.action_status === 'Failed' ? 'danger' : 'warning';
                    html += `<tr>
                        <td>${action.action_date}</td>
                        <td>${action.action_type}</td>
                        <td><span class="badge badge-${status_color}">${action.action_status}</span></td>
                        <td>${action.outcome || '-'}</td>
                    </tr>`;
                });
                
                html += '</tbody></table>';
                frm.set_df_property('risk_notes', 'description', html);
            }
        }
    });
}
