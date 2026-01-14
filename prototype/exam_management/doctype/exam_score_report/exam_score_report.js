// Copyright (c) 2025, Your Organization and contributors
// For license information, please see license.txt

frappe.ui.form.on('Exam Score Report', {
    refresh: function(frm) {
        // Add custom buttons
        if (!frm.is_new()) {
            // Export buttons
            frm.add_custom_button(__('Xuất PDF'), function() {
                export_full_report(frm);
            }, __('Báo Cáo'));
            
            frm.add_custom_button(__('Xuất Excel'), function() {
                export_to_excel(frm);
            }, __('Báo Cáo'));
            
            // Publish button for Generated status
            if (frm.doc.status === 'Generated') {
                frm.add_custom_button(__('Công Bố Điểm'), function() {
                    publish_scores(frm);
                });
            }
            
            // View statistics button
            frm.add_custom_button(__('Xem Biểu Đồ'), function() {
                show_statistics_dialog(frm);
            });
        }
        
        // Add chart if data available
        if (frm.doc.participant_scores && frm.doc.participant_scores.length > 0) {
            render_score_distribution_chart(frm);
        }
        
        // Set color indicator for pass rate
        if (frm.doc.pass_rate) {
            set_pass_rate_indicator(frm);
        }
    },
    
    exam_session: function(frm) {
        if (frm.doc.exam_session) {
            validate_exam_session(frm);
        }
    },
    
    passing_threshold: function(frm) {
        if (frm.doc.passing_threshold < 0 || frm.doc.passing_threshold > 100) {
            frappe.msgprint(__('Điểm chuẩn phải từ 0 đến 100'));
            frm.set_value('passing_threshold', 50);
        }
    },
    
    onload: function(frm) {
        // Filter exam session to only show completed sessions
        frm.set_query('exam_session', function() {
            return {
                filters: {
                    'status': 'Completed'
                }
            };
        });
    }
});

frappe.ui.form.on('Participant Score', {
    participant: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.participant) {
            frappe.db.get_value('User', row.participant, 'full_name')
                .then(r => {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'participant_name', r.message.full_name);
                    }
                });
        }
    },
    
    participant_scores_add: function(frm, cdt, cdn) {
        // Optional: Auto-populate based on session participants
    }
});

// ============================================================
// VALIDATION FUNCTIONS
// ============================================================

function validate_exam_session(frm) {
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Exam Session',
            name: frm.doc.exam_session
        },
        callback: function(r) {
            if (r.message) {
                if (r.message.status !== 'Completed') {
                    frappe.msgprint({
                        title: __('Lỗi'),
                        indicator: 'red',
                        message: __('Phiên thi chưa hoàn thành')
                    });
                    frm.set_value('exam_session', '');
                }
            }
        }
    });
}

// ============================================================
// EXPORT FUNCTIONS
// ============================================================

function export_full_report(frm) {
    frappe.call({
        method: 'prototype.exam_management.doctype.exam_score_report.exam_score_report.generate_pdf_report',
        args: {
            report_name: frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.url) {
                window.open(r.message.url);
            }
        }
    });
}

function export_to_excel(frm) {
    frappe.call({
        method: 'prototype.exam_management.doctype.exam_score_report.exam_score_report.export_to_excel',
        args: {
            report_name: frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.url) {
                window.open(r.message.url);
            }
        }
    });
}

// ============================================================
// PUBLISH FUNCTION
// ============================================================

function publish_scores(frm) {
    frappe.confirm(
        __('Bạn có chắc muốn công bố điểm? Học sinh sẽ nhìn thấy kết quả.'),
        function() {
            frappe.call({
                method: 'prototype.exam_management.doctype.exam_score_report.exam_score_report.publish_report',
                args: {
                    report_name: frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: __('Đã công bố điểm thành công'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                }
            });
        }
    );
}

// ============================================================
// CHART & VISUALIZATION
// ============================================================

function render_score_distribution_chart(frm) {
    if (!frm.doc.participant_scores || frm.doc.participant_scores.length === 0) {
        return;
    }
    
    let scores = frm.doc.participant_scores.map(row => row.total_score);
    
    // Create bins for histogram
    let bins = [0, 20, 40, 60, 80, 100];
    let counts = new Array(bins.length - 1).fill(0);
    
    scores.forEach(score => {
        for (let i = 0; i < bins.length - 1; i++) {
            if (score >= bins[i] && score < bins[i + 1]) {
                counts[i]++;
                break;
            }
        }
    });
    
    // Remove existing chart
    $('.score-distribution-chart').remove();
    
    // Add chart container
    let chart_html = `
        <div class="score-distribution-chart" style="margin: 20px 0;">
            <h5>${__('Phân Bố Điểm')}</h5>
            <div id="score_distribution_chart"></div>
        </div>
    `;
    
    $(frm.fields_dict.participant_scores.wrapper).before(chart_html);
    
    // Render chart
    new frappe.Chart('#score_distribution_chart', {
        title: '',
        data: {
            labels: bins.slice(0, -1).map((bin, i) => `${bin}-${bins[i+1]}`),
            datasets: [{
                name: __('Số Thí Sinh'),
                values: counts
            }]
        },
        type: 'bar',
        height: 250,
        colors: ['#4C8BF5']
    });
}

function show_statistics_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Thống Kê Chi Tiết'),
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'statistics_html'
            }
        ],
        size: 'large'
    });
    
    let html = `
        <div class="statistics-container">
            <div class="row">
                <div class="col-md-6">
                    <h5>${__('Thống Kê Điểm')}</h5>
                    <table class="table table-bordered">
                        <tr>
                            <td>${__('Điểm Trung Bình')}</td>
                            <td><strong>${frm.doc.average_score.toFixed(2)}</strong></td>
                        </tr>
                        <tr>
                            <td>${__('Điểm Cao Nhất')}</td>
                            <td><strong>${frm.doc.highest_score.toFixed(2)}</strong></td>
                        </tr>
                        <tr>
                            <td>${__('Điểm Thấp Nhất')}</td>
                            <td><strong>${frm.doc.lowest_score.toFixed(2)}</strong></td>
                        </tr>
                        <tr>
                            <td>${__('Độ Lệch Chuẩn')}</td>
                            <td><strong>${frm.doc.std_deviation.toFixed(2)}</strong></td>
                        </tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h5>${__('Thống Kê Đậu/Rớt')}</h5>
                    <table class="table table-bordered">
                        <tr>
                            <td>${__('Tổng Số Thí Sinh')}</td>
                            <td><strong>${frm.doc.total_participants}</strong></td>
                        </tr>
                        <tr>
                            <td>${__('Số Thí Sinh Đạt')}</td>
                            <td><strong>${frm.doc.pass_count}</strong></td>
                        </tr>
                        <tr>
                            <td>${__('Số Thí Sinh Rớt')}</td>
                            <td><strong>${frm.doc.total_participants - frm.doc.pass_count}</strong></td>
                        </tr>
                        <tr>
                            <td>${__('Tỷ Lệ Đạt')}</td>
                            <td><strong>${frm.doc.pass_rate.toFixed(2)}%</strong></td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
    `;
    
    d.fields_dict.statistics_html.$wrapper.html(html);
    d.show();
}

function set_pass_rate_indicator(frm) {
    let indicator = 'orange';
    let message = __('Trung Bình');
    
    if (frm.doc.pass_rate >= 80) {
        indicator = 'green';
        message = __('Tốt');
    } else if (frm.doc.pass_rate < 50) {
        indicator = 'red';
        message = __('Cần Cải Thiện');
    }
    
    frm.dashboard.add_indicator(
        __('Tỷ Lệ Đạt: {0}% - {1}', [frm.doc.pass_rate.toFixed(2), message]),
        indicator
    );
}