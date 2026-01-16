frappe.query_reports["Team Performance Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("Từ Ngày"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("Đến Ngày"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "department",
            "label": __("Phòng Ban"),
            "fieldtype": "Link",
            "options": "Department"
        },
        {
            "fieldname": "team",
            "label": __("Nhóm"),
            "fieldtype": "Link",
            "options": "Team"
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Color code profit/loss
        if (column.fieldname == "profit") {
            if (data.profit < 0) {
                value = `<span style="color: red">${value}</span>`;
            } else if (data.profit > 0) {
                value = `<span style="color: green">${value}</span>`;
            }
        }
        
        // Show N/A for R&D margin
        if (column.fieldname == "margin" && data.project_type == "R&D") {
            value = "N/A";
        }
        
        return value;
    }
};
