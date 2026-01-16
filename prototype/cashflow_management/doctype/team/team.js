// Copyright (c) 2026, FaceNet and contributors
// For license information, please see license.js

frappe.ui.form.on('Team', {
	refresh: function(frm) {
		// Set status indicator
		set_status_indicator(frm);

		// Add custom buttons
		if (!frm.is_new()) {
			frm.add_custom_button(__('Xem Thành Viên'), function() {
				show_team_members(frm);
			}, __('Nhóm'));

			frm.add_custom_button(__('Xem Dự Án'), function() {
				show_team_projects(frm);
			}, __('Nhóm'));

			frm.add_custom_button(__('Thống Kê Nhóm'), function() {
				show_team_statistics(frm);
			}, __('Nhóm'));
		}

		// Set query filters
		set_query_filters(frm);

		// Refresh field display
		frm.trigger('is_revenue_generating');
	},

	department: function(frm) {
		// Clear team lead if changing department
		if (frm.doc.team_lead) {
			frappe.db.get_value('Employee', frm.doc.team_lead, 'department', (r) => {
				if (r && r.department !== frm.doc.department) {
					frm.set_value('team_lead', '');
					frappe.show_alert({
						message: __('Đã xóa Trưởng Nhóm vì không thuộc phòng ban mới'),
						indicator: 'orange'
					});
				}
			});
		}
	},

	team_lead: function(frm) {
		// Validate team lead department
		if (frm.doc.team_lead && frm.doc.department) {
			frappe.db.get_value('Employee', frm.doc.team_lead, ['department', 'employee_name'], (r) => {
				if (r && r.department !== frm.doc.department) {
					frappe.msgprint({
						title: __('Cảnh Báo'),
						indicator: 'red',
						message: __('Nhân viên {0} không thuộc phòng ban {1}', [r.employee_name, frm.doc.department])
					});
					frm.set_value('team_lead', '');
				}
			});
		}
	},

	is_revenue_generating: function(frm) {
		// Update field display based on revenue generating status
		if (frm.doc.is_revenue_generating) {
			frm.set_df_property('description', 'description', 
				'Nhóm tạo doanh thu từ hợp đồng dự án với khách hàng');
		} else {
			frm.set_df_property('description', 'description', 
				'Nhóm nghiên cứu phát triển nội bộ hoặc hỗ trợ');
		}
	},

	active: function(frm) {
		set_status_indicator(frm);
		
		if (frm.doc.active === 0 && !frm.is_new()) {
			frappe.confirm(
				__('Bạn có chắc muốn ngừng hoạt động nhóm này? Tất cả nhân viên sẽ được gỡ khỏi nhóm.'),
				function() {
					// Continue
				},
				function() {
					frm.set_value('active', 1);
				}
			);
		}
	}
});

function set_query_filters(frm) {
	// Filter team lead by department
	frm.set_query('team_lead', function() {
		if (!frm.doc.department) {
			frappe.msgprint(__('Vui lòng chọn Phòng Ban trước'));
			return;
		}
		return {
			filters: {
				'department': frm.doc.department,
				'status': 'Active'
			}
		};
	});
}

function set_status_indicator(frm) {
	if (frm.doc.active) {
		frm.page.set_indicator(__('Đang Hoạt Động'), 'green');
	} else {
		frm.page.set_indicator(__('Ngừng Hoạt Động'), 'red');
	}
}

function show_team_members(frm) {
	frappe.call({
		method: 'get_team_members',
		doc: frm.doc,
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				let html = '<table class="table table-bordered table-hover">' +
					'<thead class="table-light">' +
					'<tr>' +
					'<th>Mã NV</th>' +
					'<th>Tên</th>' +
					'<th>Loại</th>' +
					'<th>Chức Danh</th>' +
					'<th>Phòng Ban</th>' +
					'</tr>' +
					'</thead>' +
					'<tbody>';

				r.message.forEach(function(emp) {
					html += `<tr>
						<td><a href="/app/employee/${emp.name}" target="_blank">${emp.name}</a></td>
						<td>${emp.employee_name}</td>
						<td><span class="badge badge-info">${emp.employee_type || ''}</span></td>
						<td>${emp.designation || ''}</td>
						<td>${emp.department || ''}</td>
					</tr>`;
				});

				html += '</tbody></table>';

				frappe.msgprint({
					title: __('Thành Viên Nhóm {0}', [frm.doc.team_name]),
					message: html,
					indicator: 'blue',
					wide: true
				});
			} else {
				frappe.msgprint({
					message: __('Nhóm chưa có thành viên nào'),
					indicator: 'yellow'
				});
			}
		}
	});
}

function show_team_projects(frm) {
	frappe.call({
		method: 'get_team_projects',
		doc: frm.doc,
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				let html = '<table class="table table-bordered table-hover">' +
					'<thead class="table-light">' +
					'<tr>' +
					'<th>Mã Dự Án</th>' +
					'<th>Tên Dự Án</th>' +
					'<th>Loại</th>' +
					'<th>Trạng Thái</th>' +
					'<th>Ngày Kết Thúc</th>' +
					'</tr>' +
					'</thead>' +
					'<tbody>';

				r.message.forEach(function(proj) {
					let status_color = 'secondary';
					if (proj.status === 'Open') status_color = 'success';
					else if (proj.status === 'Completed') status_color = 'primary';
					else if (proj.status === 'Cancelled') status_color = 'danger';

					html += `<tr>
						<td><a href="/app/project/${proj.name}" target="_blank">${proj.name}</a></td>
						<td>${proj.project_name || ''}</td>
						<td>${proj.project_type || ''}</td>
						<td><span class="badge badge-${status_color}">${proj.status}</span></td>
						<td>${proj.expected_end_date ? frappe.datetime.str_to_user(proj.expected_end_date) : ''}</td>
					</tr>`;
				});

				html += '</tbody></table>';

				frappe.msgprint({
					title: __('Dự Án Của Nhóm {0}', [frm.doc.team_name]),
					message: html,
					indicator: 'blue',
					wide: true
				});
			} else {
				frappe.msgprint({
					message: __('Nhóm chưa được gán dự án nào'),
					indicator: 'yellow'
				});
			}
		}
	});
}

function show_team_statistics(frm) {
	frappe.call({
		method: 'get_team_members',
		doc: frm.doc,
		callback: function(members_res) {
			frappe.call({
				method: 'get_team_projects',
				doc: frm.doc,
				callback: function(projects_res) {
					let members = members_res.message || [];
					let projects = projects_res.message || [];

					// Count by employee type
					let type_count = {};
					members.forEach(emp => {
						let type = emp.employee_type || 'Không xác định';
						type_count[type] = (type_count[type] || 0) + 1;
					});

					let html = '<div class="row">';
					html += '<div class="col-md-6">';
					html += '<h5>📊 Thống Kê Nhân Sự</h5>';
					html += '<table class="table table-sm">';
					html += `<tr><td><strong>Tổng nhân viên:</strong></td><td>${members.length}</td></tr>`;
					
					for (let type in type_count) {
						html += `<tr><td>${type}:</td><td>${type_count[type]}</td></tr>`;
					}
					
					html += '</table>';
					html += '</div>';

					html += '<div class="col-md-6">';
					html += '<h5>📁 Thống Kê Dự Án</h5>';
					html += '<table class="table table-sm">';
					html += `<tr><td><strong>Tổng dự án:</strong></td><td>${projects.length}</td></tr>`;
					html += `<tr><td>Loại nhóm:</td><td>${frm.doc.is_revenue_generating ? '<span class="badge badge-success">Tạo doanh thu</span>' : '<span class="badge badge-secondary">R&D/Hỗ trợ</span>'}</td></tr>`;
					html += `<tr><td>Phòng ban:</td><td>${frm.doc.department}</td></tr>`;
					html += `<tr><td>Trưởng nhóm:</td><td>${frm.doc.team_lead || '<i>Chưa có</i>'}</td></tr>`;
					html += '</table>';
					html += '</div>';
					html += '</div>';

					frappe.msgprint({
						title: __('Thống Kê Nhóm {0}', [frm.doc.team_name]),
						message: html,
						indicator: 'blue',
						wide: true
					});
				}
			});
		}
	});
}
