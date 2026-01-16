"""
Cashflow Forecast Report
F014: Cashflow forecast with payment delays, debt risk
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months, get_first_day, get_last_day, add_days
from datetime import datetime
from dateutil.relativedelta import relativedelta


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "month",
            "label": _("Tháng"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "expected_inflow",
            "label": _("Tiền Vào (Dự Kiến)"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "adjusted_inflow",
            "label": _("Tiền Vào (Điều Chỉnh)"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "salary_cost",
            "label": _("Chi Phí Lương"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "other_expenses",
            "label": _("Chi Phí Khác"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "total_outflow",
            "label": _("Tổng Tiền Ra"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "net_cashflow",
            "label": _("Dòng Tiền Ròng"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "cumulative_cash",
            "label": _("Tiền Tích Lũy"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "risk_level",
            "label": _("Mức Rủi Ro"),
            "fieldtype": "Data",
            "width": 100
        }
    ]


def get_data(filters):
    """
    Calculate cashflow forecast
    BR-REPORT-003: Cashflow forecast updates daily
    BR-REPORT-004: Debt risk reduces expected cash inflow
    """
    months = get_forecast_months(filters)
    data = []
    
    # Get starting cash balance
    cumulative_cash = flt(filters.get("starting_balance", 0))
    
    for month in months:
        row = calculate_monthly_cashflow(month, filters)
        
        # Calculate cumulative
        net_cashflow = row["adjusted_inflow"] - row["total_outflow"]
        cumulative_cash += net_cashflow
        
        row["net_cashflow"] = net_cashflow
        row["cumulative_cash"] = cumulative_cash
        
        # Assess risk
        row["risk_level"] = assess_risk(cumulative_cash, row["total_outflow"])
        
        data.append(row)
    
    return data


def get_forecast_months(filters):
    """Generate list of months for forecast"""
    from_date = getdate(filters.get("from_date") or frappe.utils.nowdate())
    horizon = int(filters.get("forecast_months", 6))
    
    months = []
    for i in range(horizon):
        month_date = add_months(from_date, i)
        first_day = get_first_day(month_date)
        last_day = get_last_day(month_date)
        
        months.append({
            "month": month_date.strftime("%Y-%m"),
            "first_day": first_day,
            "last_day": last_day
        })
    
    return months


def calculate_monthly_cashflow(month, filters):
    """
    Calculate cashflow for one month
    CR-CASHFLOW-ADJUSTMENT-001: Adjust for payment delays and debt risk
    """
    first_day = month["first_day"]
    last_day = month["last_day"]
    
    # Calculate expected inflows
    expected_inflow = get_expected_inflow(first_day, last_day)
    adjusted_inflow = get_adjusted_inflow(first_day, last_day)
    
    # Calculate outflows
    salary_cost = get_monthly_salary_cost()
    other_expenses = get_monthly_expenses(first_day, last_day)
    
    total_outflow = salary_cost + other_expenses
    
    return {
        "month": month["month"],
        "expected_inflow": expected_inflow,
        "adjusted_inflow": adjusted_inflow,
        "salary_cost": salary_cost,
        "other_expenses": other_expenses,
        "total_outflow": total_outflow
    }


def get_expected_inflow(from_date, to_date):
    """
    Get expected cash inflow from payment schedules
    """
    schedules = frappe.get_all(
        "Payment Schedule",
        filters={
            "expected_date": ["between", [from_date, to_date]],
            "status": ["!=", "Received"]
        },
        fields=["amount"]
    )
    
    return sum([s.amount or 0 for s in schedules])


def get_adjusted_inflow(from_date, to_date):
    """
    Adjust inflow for payment delays and debt risk
    CR-CASHFLOW-ADJUSTMENT-001
    """
    schedules = frappe.get_all(
        "Payment Schedule",
        filters={
            "expected_date": ["between", [from_date, to_date]],
            "status": ["!=", "Received"]
        },
        fields=["name", "amount", "customer", "expected_date", "status"]
    )
    
    adjusted_total = 0
    
    for schedule in schedules:
        amount = schedule.amount or 0
        
        # Check for associated debt (payment delay risk)
        debt = frappe.db.get_value(
            "Debt Management",
            {
                "payment_schedule": schedule.name,
                "current_status": ["!=", "Resolved"]
            },
            ["escalation_level", "payment_probability"]
        )
        
        if debt:
            # Apply payment probability from debt risk assessment
            # CR-DEBT-RISK-001
            probability = debt[1] / 100.0 if debt[1] else 0.95
            adjusted_amount = amount * probability
        else:
            # No debt record - check customer payment pattern
            customer_pattern = get_customer_payment_pattern(schedule.customer)
            
            # Assume 95% probability if good payment history
            if customer_pattern.get("average_delay", 0) <= 15:
                probability = 0.95
            else:
                probability = 0.80
            
            adjusted_amount = amount * probability
        
        adjusted_total += adjusted_amount
    
    return adjusted_total


def get_customer_payment_pattern(customer):
    """Get historical payment pattern for customer"""
    from prototype.cashflow_management.doctype.debt_management.debt_management import get_customer_payment_pattern
    
    try:
        return get_customer_payment_pattern(customer)
    except:
        return {"average_delay": 0}


def get_monthly_salary_cost():
    """
    Estimate monthly salary cost for all employees
    From M005: Salary Table
    """
    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["custom_employee_type", "custom_base_salary", 
                "custom_daily_rate", "custom_performance_factor"]
    )
    
    total_cost = 0
    
    for emp in employees:
        emp_type = emp.custom_employee_type
        
        if emp_type == "Regular":
            # Regular: Base + employer SS + estimated bonus
            monthly_cost = (emp.custom_base_salary or 0) * 1.175
        elif emp_type == "Intern":
            # Intern: Daily rate × 22 days × performance factor
            monthly_cost = (emp.custom_daily_rate or 0) * 22 * (emp.custom_performance_factor or 1.0)
        else:
            # Freelancer: Project-based (estimate)
            monthly_cost = 0
        
        total_cost += monthly_cost
    
    return total_cost


def get_monthly_expenses(from_date, to_date):
    """
    Get approved expenses for the month
    From M004: Expense Management
    """
    expenses = frappe.get_all(
        "Expense",
        filters={
            "approval_status": "Approved",
            "expense_date": ["between", [from_date, to_date]]
        },
        fields=["amount"]
    )
    
    return sum([exp.amount or 0 for exp in expenses])


def assess_risk(cumulative_cash, monthly_outflow):
    """
    Assess cashflow risk level
    High Risk: < 1 month operating cost
    Medium Risk: < 2 months operating cost
    Low Risk: > 2 months operating cost
    """
    if monthly_outflow == 0:
        return "Low"
    
    months_coverage = cumulative_cash / monthly_outflow
    
    if months_coverage < 1:
        return "High"
    elif months_coverage < 2:
        return "Medium"
    else:
        return "Low"


def get_chart_data(data):
    """Generate waterfall chart for cashflow"""
    if not data:
        return None
    
    months = [row["month"] for row in data]
    inflow = [row["adjusted_inflow"] for row in data]
    outflow = [-row["total_outflow"] for row in data]  # Negative for visualization
    cumulative = [row["cumulative_cash"] for row in data]
    
    chart = {
        "data": {
            "labels": months,
            "datasets": [
                {
                    "name": "Tiền Vào",
                    "values": inflow,
                    "chartType": "bar"
                },
                {
                    "name": "Tiền Ra",
                    "values": outflow,
                    "chartType": "bar"
                },
                {
                    "name": "Tiền Tích Lũy",
                    "values": cumulative,
                    "chartType": "line"
                }
            ]
        },
        "type": "axis-mixed",
        "colors": ["#28a745", "#dc3545", "#007bff"]
    }
    
    return chart


def get_summary(data):
    """Generate summary statistics"""
    if not data:
        return []
    
    total_inflow = sum([row["adjusted_inflow"] for row in data])
    total_outflow = sum([row["total_outflow"] for row in data])
    net_total = total_inflow - total_outflow
    
    high_risk_months = len([row for row in data if row["risk_level"] == "High"])
    
    summary = [
        {
            "value": total_inflow,
            "label": "Tổng Tiền Vào (Điều Chỉnh)",
            "datatype": "Currency",
            "indicator": "green" if total_inflow > 0 else "red"
        },
        {
            "value": total_outflow,
            "label": "Tổng Tiền Ra",
            "datatype": "Currency",
            "indicator": "red"
        },
        {
            "value": net_total,
            "label": "Dòng Tiền Ròng",
            "datatype": "Currency",
            "indicator": "green" if net_total > 0 else "red"
        },
        {
            "value": high_risk_months,
            "label": "Số Tháng Rủi Ro Cao",
            "indicator": "red" if high_risk_months > 0 else "green"
        }
    ]
    
    return summary
