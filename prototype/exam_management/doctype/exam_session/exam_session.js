// Copyright (c) 2026, Your Organization and contributors
// For license information, please see license.txt

frappe.ui.form.on('Exam Session', {
    refresh: function(frm) {
        // Add custom buttons based on status
        add_lifecycle_buttons(frm);
        
        // Add dashboard button
        frm.add_custom_button(__('Xem Dashboard'), function() {
            show_session_dashboard(frm);
        }, __('Giám Sát'));
        
        // Show status indicator
        show_status_indicator(frm);
        
        // Auto-refresh if in progress
        if (frm.doc.status === 'In Progress') {
            setup_auto_refresh(frm);
        }
    },
    
    exam_paper: function(frm) {
        if (frm.doc.exam_paper) {
            load_exam_paper_info(frm);
        }
    },
    
    start_time: function(frm) {
        calculate_end_time(frm);
    },
    
    duration: function(frm) {
        calculate_end_time(frm);
    },
    
    classroom: function(frm) {
        if (frm.doc.classroom) {
            check_classroom_capacity(frm);
        }
    }
});

frappe.ui.form.on('Exam Session Participant', {
    participants_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.status = 'Registered';
    },
    
    participants_remove: function(frm) {
        update_participant_count(frm);
    }
});

// ============================================================
// LIFECYCLE BUTTONS
// ============================================================

function add_lifecycle_buttons(frm) {
    // Start Session button
    if (frm.doc.status === 'Scheduled') {
        frm.add_custom_button(__('Bắt Đầu Thi'), function() {
            start_exam_session(frm);
        }).addClass('btn-primary');
    }
    
    // End Session button
    if (frm.doc.status === 'In Progress') {
        frm.add_custom_button(__('Kết Thúc Thi'), function() {
            end_exam_session(frm);
        }).addClass('btn-danger');
        
        // Force End button (with permission check)
        if (frappe.user.has_role(['System Manager', 'Exam Administrator'])) {
            frm.add_custom_button(__('Kết Thúc Ngay'), function() {
                end_exam_session(frm, true);
            }, __('Hành Động')).addClass('btn-warning');
        }
    }
}

function start_exam_session(frm) {
    frappe.confirm(
        __('Bạn có chắc muốn bắt đầu phiên thi này?<br><br>' +
           'Tất cả {0} thí sinh sẽ nhận được thông báo.',
           [frm.doc.total_participants || 0]),
        function() {
            frappe.call({
                method: 'prototype.exam_management.api.start_exam_session',
                args: {
                    session_id: frm.doc.name
                },
                freeze: true,
                freeze_message: __('Đang bắt đầu phiên thi...'),
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: __('Đã bắt đầu phiên thi thành công!<br>' +
                                      'Đã thông báo {0} thí sinh.',
                                      [r.message.participants_notified]),
                            indicator: 'green'
                        }, 5);
                        frm.reload_doc();
                    }
                },
                error: function(r) {
                    frappe.msgprint({
                        title: __('Lỗi'),
                        indicator: 'red',
                        message: r.message || __('Không thể bắt đầu phiên thi')
                    });
                }
            });
        }
    );
}

function end_exam_session(frm, force = false) {
    // Get current stats first
    frappe.call({
        method: 'prototype.exam_management.api.get_session_status',
        args: {
            session_id: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                let stats = r.message.stats;
                let warning = '';
                
                if (stats.pending > 0) {
                    warning = __('<br><br><span style="color: red;">Cảnh báo: {0} thí sinh chưa nộp bài ' +
                               'sẽ được đánh dấu chưa hoàn thành.</span>',
                               [stats.pending]);
                }
                
                let msg = __('Bạn có chắc muốn kết thúc phiên thi?<br><br>' +
                           'Đã nộp: {0}/{1}<br>' +
                           'Chưa nộp: {2}' + warning,
                           [stats.submitted, stats.total, stats.pending]);
                
                frappe.confirm(msg, function() {
                    frappe.call({
                        method: 'prototype.exam_management.api.end_exam_session',
                        args: {
                            session_id: frm.doc.name,
                            force: force
                        },
                        freeze: true,
                        freeze_message: __('Đang kết thúc phiên thi...'),
                        callback: function(r) {
                            if (r.message && r.message.success) {
                                let result = r.message;
                                let msg = __('Đã kết thúc phiên thi!<br><br>');
                                
                                if (result.report_generated) {
                                    msg += __('Báo cáo điểm: {0}', [result.report_name]);
                                } else {
                                    msg += __('Đang tạo báo cáo điểm...');
                                }
                                
                                frappe.show_alert({
                                    message: msg,
                                    indicator: 'green'
                                }, 7);
                                
                                frm.reload_doc();
                            }
                        }
                    });
                });
            }
        }
    });
}

// ============================================================
// DASHBOARD & MONITORING
// ============================================================

function show_session_dashboard(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Dashboard Phiên Thi'),
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'dashboard_html'
            }
        ],
        size: 'large'
    });
    
    load_dashboard_data(frm, d);
    d.show();
    
    // Auto-refresh every 30 seconds
    let interval = setInterval(function() {
        if (d.is_visible) {
            load_dashboard_data(frm, d);
        } else {
            clearInterval(interval);
        }
    }, 30000);
}

function load_dashboard_data(frm, dialog) {
    frappe.call({
        method: 'prototype.exam_management.api.get_session_status',
        args: {
            session_id: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                render_dashboard(dialog, r.message);
            }
        }
    });
}

function render_dashboard(dialog, data) {
    let stats = data.stats;
    let remaining = data.remaining_time || 0;
    let progress = data.progress || 0;
    
    // Format remaining time
    let hours = Math.floor(remaining / 3600);
    let minutes = Math.floor((remaining % 3600) / 60);
    let seconds = remaining % 60;
    let time_str = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    
    let html = `
        <div class="session-dashboard">
            <div class="row">
                <div class="col-md-6">
                    <div class="dashboard-card">
                        <h4>⏱️ Thời Gian Còn Lại</h4>
                        <h2 style="color: ${remaining < 600 ? 'red' : '#333'};">${time_str}</h2>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="dashboard-card">
                        <h4>📊 Tiến Độ</h4>
                        <div class="progress" style="height: 30px;">
                            <div class="progress-bar" role="progressbar" 
                                 style="width: ${progress}%;">${Math.round(progress)}%</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row" style="margin-top: 20px;">
                <div class="col-md-4">
                    <div class="dashboard-stat">
                        <h5>Tổng Thí Sinh</h5>
                        <h3>${stats.total}</h3>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="dashboard-stat" style="background: #d4edda;">
                        <h5>✅ Đã Nộp</h5>
                        <h3>${stats.submitted}</h3>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="dashboard-stat" style="background: #f8d7da;">
                        <h5>⏳ Chưa Nộp</h5>
                        <h3>${stats.pending}</h3>
                    </div>
                </div>
            </div>
            
            ${stats.pending_participants && stats.pending_participants.length > 0 ? `
                <div class="row" style="margin-top: 20px;">
                    <div class="col-md-12">
                        <h5>Thí Sinh Chưa Nộp:</h5>
                        <ul>
                            ${stats.pending_participants.map(p => `<li>${p}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            ` : ''}
        </div>
        
        <style>
            .dashboard-card {
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            .dashboard-stat {
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
                background: #f8f9fa;
            }
            .dashboard-stat h3 {
                margin: 10px 0 0 0;
                font-size: 36px;
                font-weight: bold;
            }
        </style>
    `;
    
    dialog.fields_dict.dashboard_html.$wrapper.html(html);
}

function setup_auto_refresh(frm) {
    // Refresh every 30 seconds
    if (frm.__refresh_interval) {
        clearInterval(frm.__refresh_interval);
    }
    
    frm.__refresh_interval = setInterval(function() {
        if (frm.doc.status === 'In Progress') {
            frm.reload_doc();
        } else {
            clearInterval(frm.__refresh_interval);
        }
    }, 30000);
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

function show_status_indicator(frm) {
    let indicator = 'blue';
    let status_text = frm.doc.status;
    
    if (frm.doc.status === 'In Progress') {
        indicator = 'orange';
        
        // Show remaining time
        if (frm.doc.actual_start_time) {
            frappe.call({
                method: 'prototype.exam_management.api.get_session_status',
                args: { session_id: frm.doc.name },
                callback: function(r) {
                    if (r.message && r.message.remaining_time) {
                        let remaining = r.message.remaining_time;
                        let minutes = Math.floor(remaining / 60);
                        status_text = __('Đang Diễn Ra - Còn {0} phút', [minutes]);
                        frm.dashboard.add_indicator(status_text, indicator);
                    }
                }
            });
        }
    } else if (frm.doc.status === 'Completed') {
        indicator = 'green';
    } else if (frm.doc.status === 'Cancelled') {
        indicator = 'red';
    }
    
    frm.dashboard.add_indicator(__(status_text), indicator);
}

function calculate_end_time(frm) {
    if (frm.doc.start_time && frm.doc.duration) {
        // Calculate end time
        let start_parts = frm.doc.start_time.split(':');
        let start_minutes = parseInt(start_parts[0]) * 60 + parseInt(start_parts[1]);
        let end_minutes = start_minutes + parseInt(frm.doc.duration);
        
        let end_hours = Math.floor(end_minutes / 60) % 24;
        let end_mins = end_minutes % 60;
        
        frm.set_value('end_time', 
            String(end_hours).padStart(2, '0') + ':' + 
            String(end_mins).padStart(2, '0') + ':00'
        );
    }
}

function load_exam_paper_info(frm) {
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Exam Paper',
            name: frm.doc.exam_paper
        },
        callback: function(r) {
            if (r.message) {
                let paper = r.message;
                if (!frm.doc.duration && paper.duration) {
                    frm.set_value('duration', paper.duration);
                }
            }
        }
    });
}

function check_classroom_capacity(frm) {
    if (!frm.doc.classroom) return;
    
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Exam Classroom',
            name: frm.doc.classroom
        },
        callback: function(r) {
            if (r.message) {
                let capacity = r.message.capacity;
                let participants = frm.doc.total_participants || 0;
                
                if (participants > capacity) {
                    frappe.msgprint({
                        title: __('Cảnh Báo'),
                        indicator: 'orange',
                        message: __('Số lượng thí sinh ({0}) vượt quá sức chứa phòng ({1})',
                                  [participants, capacity])
                    });
                }
            }
        }
    });
}

function update_participant_count(frm) {
    frm.set_value('total_participants', frm.doc.participants ? frm.doc.participants.length : 0);
}