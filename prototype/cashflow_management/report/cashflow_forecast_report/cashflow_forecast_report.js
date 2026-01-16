frappe.query_reports["Cashflow Forecast Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("Từ Ngày"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "forecast_months",
            "label": __("Số Tháng Dự Báo"),
            "fieldtype": "Select",
            "options": "3\n6\n12",
            "default": "6",
            "reqd": 1
        },
        {
            "fieldname": "starting_balance",
            "label": __("Số Dư Đầu Kỳ"),
            "fieldtype": "Currency",
            "default": 0
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Color code net cashflow
        if (column.fieldname == "net_cashflow") {
            if (data.net_cashflow < 0) {
                value = `<span style="color: red; font-weight: bold">${value}</span>`;
            } else {
                value = `<span style="color: green; font-weight: bold">${value}</span>`;
            }
        }
        
        // Color code risk level
        if (column.fieldname == "risk_level") {
            let color = "gray";
            if (data.risk_level == "High") {
                color = "red";
            } else if (data.risk_level == "Medium") {
                color = "orange";
            } else if (data.risk_level == "Low") {
                color = "green";
            }
            value = `<span class="indicator ${color}">${value}</span>`;
        }
        
        // Highlight negative cumulative cash
        if (column.fieldname == "cumulative_cash") {
            if (data.cumulative_cash < 0) {
                value = `<span style="color: red; font-weight: bold">${value}</span>`;
            }
        }
        
        return value;
    }
};
