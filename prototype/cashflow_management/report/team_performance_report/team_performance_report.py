"""
Team Performance Report
F013: Team-level P&L showing income, costs, profit/loss
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, get_first_day, get_last_day


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    
    return columns, data, None, chart


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "team",
            "label": _("Nhóm"),
            "fieldtype": "Link",
            "options": "Team",
            "width": 150
        },
        {
            "fieldname": "team_name",
            "label": _("Tên Nhóm"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "project_type",
            "label": _("Loại"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "income",
            "label": _("Thu Nhập"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "labor_cost",
            "label": _("Chi Phí Nhân Công"),
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "fieldname": "direct_expenses",
            "label": _("Chi Phí Trực Tiếp"),
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "fieldname": "shared_expenses",
            "label": _("Chi Phí Chung"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "total_cost",
            "label": _("Tổng Chi Phí"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "profit",
            "label": _("Lợi Nhuận"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "margin",
            "label": _("Biên (%)"),
            "fieldtype": "Percent",
            "width": 100
        }
    ]


def get_data(filters):
    """
    Calculate team performance data
    BR-REPORT-001: R&D teams show negative profit (investment)
    BR-REPORT-002: Team margin % not applicable for R&D
    """
    teams = get_teams(filters)
    data = []
    
    for team in teams:
        row = calculate_team_performance(team, filters)
        data.append(row)
    
    return data


def get_teams(filters):
    """Get filtered teams"""
    conditions = {"active": 1}
    
    if filters.get("department"):
        conditions["department"] = filters.get("department")
    
    if filters.get("team"):
        conditions["name"] = filters.get("team")
    
    teams = frappe.get_all(
        "Team",
        filters=conditions,
        fields=["name", "team_name", "is_revenue_generating"]
    )
    
    return teams


def calculate_team_performance(team, filters):
    """
    Calculate performance metrics for one team
    """
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    
    # Determine project type
    project_type = "Contract-based" if team.is_revenue_generating else "R&D"
    
    # Calculate income
    income = 0
    if team.is_revenue_generating:
        income = get_team_income(team.name, from_date, to_date)
    
    # Calculate labor costs
    labor_cost = get_team_labor_cost(team.name, from_date, to_date)
    
    # Calculate expenses
    direct_expenses = get_team_direct_expenses(team.name, from_date, to_date)
    shared_expenses = get_team_shared_expenses(from_date, to_date)
    
    total_cost = labor_cost + direct_expenses + shared_expenses
    
    # Calculate profit
    profit = income - total_cost
    
    # Calculate margin (BR-REPORT-002: N/A for R&D)
    if team.is_revenue_generating and income > 0:
        margin = (profit / income) * 100
    else:
        margin = None
    
    return {
        "team": team.name,
        "team_name": team.team_name,
        "project_type": project_type,
        "income": income,
        "labor_cost": labor_cost,
        "direct_expenses": direct_expenses,
        "shared_expenses": shared_expenses,
        "total_cost": total_cost,
        "profit": profit,
        "margin": margin
    }


def get_team_income(team, from_date, to_date):
    """
    Get income from contracts/projects assigned to team
    """
    # Get projects assigned to this team
    projects = frappe.get_all(
        "Project",
        filters={"custom_assigned_team": team},
        fields=["name", "custom_linked_contract"]
    )
    
    if not projects:
        return 0
    
    total_income = 0
    
    for project in projects:
        if project.custom_linked_contract:
            # Get contract value
            contract_value = frappe.db.get_value(
                "Contract",
                project.custom_linked_contract,
                "custom_total_contract_value"
            ) or 0
            total_income += contract_value
    
    return total_income


def get_team_labor_cost(team, from_date, to_date):
    """
    Calculate labor cost for team members
    From M005: Salary calculations
    """
    # Get employees in this team
    employees = frappe.get_all(
        "Employee",
        filters={"custom_primary_team": team, "status": "Active"},
        fields=["name", "custom_employee_type", "custom_base_salary", 
                "custom_daily_rate", "custom_performance_factor"]
    )
    
    if not employees:
        return 0
    
    # For this simplified version, estimate monthly cost
    # In real system, query Salary Table for the period
    total_cost = 0
    
    for emp in employees:
        emp_type = emp.custom_employee_type
        
        if emp_type == "Regular":
            # Regular: Base + 17.5% employer SS
            monthly_cost = (emp.custom_base_salary or 0) * 1.175
        elif emp_type == "Intern":
            # Intern: Daily rate × 22 days × performance factor
            monthly_cost = (emp.custom_daily_rate or 0) * 22 * (emp.custom_performance_factor or 1.0)
        else:
            # Freelancer: Estimate from projects
            monthly_cost = 0
        
        total_cost += monthly_cost
    
    return total_cost


def get_team_direct_expenses(team, from_date, to_date):
    """
    Get expenses directly allocated to this team
    From M004: Expense Management
    """
    expenses = frappe.get_all(
        "Expense",
        filters={
            "team": team,
            "approval_status": "Approved",
            "expense_date": ["between", [from_date, to_date]]
        },
        fields=["amount"]
    )
    
    return sum([exp.amount or 0 for exp in expenses])


def get_team_shared_expenses(from_date, to_date):
    """
    Calculate shared expenses (office, marketing) divided by number of teams
    """
    # Get shared expenses (Office, Marketing without team assignment)
    shared_expenses = frappe.get_all(
        "Expense",
        filters={
            "category": ["in", ["Office", "Marketing"]],
            "team": ["is", "not set"],
            "approval_status": "Approved",
            "expense_date": ["between", [from_date, to_date]]
        },
        fields=["amount"]
    )
    
    total_shared = sum([exp.amount or 0 for exp in shared_expenses])
    
    # Divide by number of active teams
    num_teams = frappe.db.count("Team", {"active": 1})
    
    if num_teams > 0:
        return total_shared / num_teams
    
    return 0


def get_chart_data(data):
    """Generate chart for visual representation"""
    if not data:
        return None
    
    teams = [row["team_name"] for row in data]
    income = [row["income"] for row in data]
    costs = [row["total_cost"] for row in data]
    profit = [row["profit"] for row in data]
    
    chart = {
        "data": {
            "labels": teams,
            "datasets": [
                {
                    "name": "Thu Nhập",
                    "values": income
                },
                {
                    "name": "Chi Phí",
                    "values": costs
                },
                {
                    "name": "Lợi Nhuận",
                    "values": profit
                }
            ]
        },
        "type": "bar",
        "colors": ["#28a745", "#dc3545", "#007bff"]
    }
    
    return chart
