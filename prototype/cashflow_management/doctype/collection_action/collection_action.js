frappe.ui.form.on('Collection Action', {
    refresh: function(frm) {
        // Show guidance based on action status
        if (frm.doc.action_status === "Planned") {
            frm.set_intro(__('Hành động đã lên kế hoạch. Cập nhật trạng thái sau khi thực hiện.'), 'blue');
        } else if (frm.doc.action_status === "Completed") {
            frm.set_intro(__('Hành động đã hoàn thành'), 'green');
        } else if (frm.doc.action_status === "Failed") {
            frm.set_intro(__('Hành động thất bại. Vui lòng đặt lịch theo dõi lại.'), 'red');
        }
        
        // Quick complete button
        if (frm.doc.action_status === "Planned" && !frm.is_new()) {
            frm.add_custom_button(__('Đánh Dấu Hoàn Thành'), function() {
                quick_complete(frm);
            }).addClass('btn-success');
            
            frm.add_custom_button(__('Đánh Dấu Thất Bại'), function() {
                quick_fail(frm);
            }).addClass('btn-danger');
        }
    },
    
    action_status: function(frm) {
        // Show/hide fields based on status
        frm.toggle_reqd('outcome', frm.doc.action_status === 'Completed');
        frm.toggle_reqd('followup_date', frm.doc.action_status === 'Failed');
    }
});

function quick_complete(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Hoàn Thành Hành Động'),
        fields: [
            {
                fieldname: 'outcome',
                fieldtype: 'Text',
                label: __('Kết Quả'),
                reqd: 1
            },
            {
                fieldname: 'followup_date',
                fieldtype: 'Date',
                label: __('Ngày Theo Dõi Tiếp (nếu cần)')
            }
        ],
        primary_action_label: __('Lưu'),
        primary_action(values) {
            frm.set_value('action_status', 'Completed');
            frm.set_value('outcome', values.outcome);
            if (values.followup_date) {
                frm.set_value('followup_date', values.followup_date);
            }
            frm.save();
            d.hide();
        }
    });
    d.show();
}

function quick_fail(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Hành Động Thất Bại'),
        fields: [
            {
                fieldname: 'action_notes',
                fieldtype: 'Text',
                label: __('Lý Do'),
                reqd: 1
            },
            {
                fieldname: 'followup_date',
                fieldtype: 'Date',
                label: __('Ngày Thử Lại'),
                reqd: 1
            }
        ],
        primary_action_label: __('Lưu'),
        primary_action(values) {
            frm.set_value('action_status', 'Failed');
            frm.set_value('action_notes', values.action_notes);
            frm.set_value('followup_date', values.followup_date);
            frm.save();
            d.hide();
        }
    });
    d.show();
}
