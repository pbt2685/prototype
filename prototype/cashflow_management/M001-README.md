# M001: Core Setup - Implementation Guide

## 📋 Overview

M001 provides the foundation for the Cashflow Management system with:
- **Department**: Level 1 organizational structure (customized ERPNext DocType)
- **Team**: Level 2 organizational structure (custom DocType)
- **Employee classification**: Regular, Intern, Freelancer

## 🏗️ Architecture

```
Department (ERPNext)
    ├── Custom Fields: department_code, cost_center_allocation
    └── Team (Custom DocType)
            ├── Fields: team_code, team_name, team_lead, is_revenue_generating
            └── Employee (ERPNext) - Custom Field: primary_team
```

## 📁 File Structure

```
cashflow_management/
├── doctype/
│   └── team/
│       ├── __init__.py
│       ├── team.json                    # DocType definition
│       ├── team.py                      # Controller with BR validations
│       ├── team.js                      # Client script
│       └── test_team.py                 # Unit tests
├── patches/
│   └── v1_0/
│       ├── add_department_custom_fields.py
│       └── add_employee_custom_fields.py
├── fixtures/
│   └── team.json                        # Sample team data
└── setup_m001.py                        # Setup script
```

## ✅ Business Rules Implemented

### BR-TEAM-001: Team Must Belong to Department
- **Location**: `team.py` - `validate()` method
- **Validation**: Team must have valid Department link
- **Error**: "Nhóm phải thuộc một Phòng Ban"

### BR-TEAM-002: Team Code Unique
- **Location**: `team.py` - `validate_team_code_unique()` method
- **Validation**: team_code must be unique across all teams
- **Error**: "Mã nhóm đã tồn tại"

### BR-DEPT-001: Department Code Unique
- **Location**: Custom field with unique constraint
- **Validation**: department_code must be unique
- **Auto-generation**: Patch creates codes for existing departments

## 🎯 Features

### 1. Team DocType
- **Auto-naming**: Uses team_code as primary key
- **Tree View**: Not hierarchical (flat structure under Department)
- **Revenue Flag**: Distinguishes revenue-generating vs R&D teams
- **Active Status**: Can deactivate teams without deletion

### 2. Custom Fields

#### Department (ERPNext)
- `department_code` (Data, 20 chars, unique)
- `cost_center_allocation` (Link to Cost Center)

#### Employee (ERPNext)
- `employee_type` (Select: Regular|Intern|Freelancer)
- `payment_method` (Select: Bank|Cash)
- `daily_rate` (Currency, for Interns)
- `primary_team` (Link to Team)
- `bank_name`, `bank_account_number`, `bank_account_holder`

### 3. Client Features (team.js)
- **View Team Members**: Show all employees in team
- **View Team Projects**: Show all projects assigned to team
- **Team Statistics**: Summary of team composition and workload
- **Validation**: Real-time checks for team lead department match

## 🚀 Installation

### Prerequisites
```bash
# ERPNext must be installed first
bench --site [site] list-apps
# Should show: erpnext
```

### Step 1: Navigate to Bench
```bash
cd ~/frappe-bench
```

### Step 2: Install/Migrate
```bash
# Migrate to create Team DocType
bench --site [site] migrate

# Clear cache
bench --site [site] clear-cache

# Build assets
bench build --app prototype
```

### Step 3: Setup Sample Data (Optional)
```bash
bench --site [site] console

>>> from prototype.cashflow_management.setup_m001 import setup_m001
>>> setup_m001()
```

This creates:
- 3 sample departments (Outsourcing, R&D, Internal Operations)
- 5 sample teams (FotoFinder, DGX, VTT, R&D, Support)

## 🧪 Testing

### Run Unit Tests
```bash
# Test Team DocType
bench --site [site] run-tests --doctype "Team"

# Run specific test
bench --site [site] run-tests --test "prototype.cashflow_management.doctype.team.test_team.TestTeam.test_create_team"
```

### Manual Testing Checklist

#### ✅ Create Team
1. Go to: `/app/team/new`
2. Fill required fields: team_code, team_name, department
3. Save → Should succeed

#### ✅ Test BR-TEAM-002 (Duplicate Code)
1. Create team with code "TEST-001"
2. Try creating another team with code "TEST-001"
3. Should show error: "Mã nhóm đã tồn tại"

#### ✅ Test BR-TEAM-001 (Team Lead Department)
1. Create team in "Department A"
2. Set team_lead from "Department B"
3. Should show error: "Trưởng nhóm không thuộc phòng ban"

#### ✅ Test Deactivation
1. Create team and assign employees
2. Set active = 0
3. Check employees → primary_team should be cleared

#### ✅ Test Deletion Protection
1. Create team and assign employees
2. Try to delete team
3. Should show error: "Không thể xóa nhóm. Còn X nhân viên"

## 📊 Usage Examples

### Create Team via API
```python
import frappe

team = frappe.get_doc({
    "doctype": "Team",
    "team_code": "PROJ-001",
    "team_name": "Project Alpha Team",
    "department": "Outsourcing",
    "team_lead": "EMP-001",
    "is_revenue_generating": 1,
    "active": 1,
    "description": "Team handling Project Alpha development"
})
team.insert()
```

### Get Team Members
```python
team = frappe.get_doc("Team", "PROJ-001")
members = team.get_team_members()

for emp in members:
    print(f"{emp.name}: {emp.employee_name} ({emp.employee_type})")
```

### Get Team Summary
```python
from prototype.cashflow_management.doctype.team.team import get_team_summary

teams = get_team_summary(department="Outsourcing")
for team in teams:
    print(f"{team.team_name}: {team.employee_count} employees, {team.project_count} projects")
```

## 🔗 Integration Points

### M002: Employee Management
- Employees assigned to Teams via `primary_team` field
- Employee type validation uses custom fields
- Salary calculations consider team allocation

### M003: Contract & Project
- Projects linked to Teams via `assigned_team` field
- Team profitability tracking
- Resource allocation by team

### M004: Expense Management
- Expenses can be allocated to specific teams
- Team-based cost tracking
- Budget allocation by team

### M007: Reporting & Analytics
- Team performance reports
- Cost per team analysis
- Revenue attribution to teams

## 🐛 Troubleshooting

### Issue: "Department DocType not found"
**Solution**: Install ERPNext first
```bash
bench get-app erpnext --branch version-15
bench --site [site] install-app erpnext
```

### Issue: Custom fields not showing
**Solution**: Clear cache and rebuild
```bash
bench --site [site] clear-cache
bench build --app prototype --force
```

### Issue: Patches not running
**Solution**: Check patches.txt and run migrate
```bash
# Check if patches are listed
cat apps/prototype/prototype/patches.txt

# Force migrate
bench --site [site] migrate --skip-failing
```

### Issue: Team not appearing in dropdown
**Solution**: Check permissions and reload
```bash
bench --site [site] console

>>> frappe.get_all("Team", fields=["name", "team_name"])
# Should show teams

# Check permissions
>>> frappe.has_permission("Team", "read")
```

## 📈 Performance Considerations

- Team list is cached for 1 hour
- Employee count is computed on-demand (not stored)
- Use `get_team_summary()` for bulk operations
- Index on `department` field for fast filtering

## 🔐 Security

### Roles & Permissions
- **System Manager**: Full access
- **HR Manager**: Create, edit, delete teams
- **HR User**: View and edit teams
- **Employee**: View only

### Field-level Security
- `department_code`: Only System Manager can edit
- `team_lead`: Restricted to active employees in same department

## 📝 Next Steps

After M001 is working:
1. **M002**: Implement Performance Rating DocType
2. **M002**: Add Attendance tracking customizations
3. **M003**: Create Contract and Payment Schedule DocTypes
4. **M004**: Implement Expense management workflow

## 📚 References

- [Frappe DocType](https://frappeframework.com/docs/user/en/basics/doctypes)
- [Custom Fields](https://frappeframework.com/docs/user/en/customization/custom-field)
- [Database Migrations](https://frappeframework.com/docs/user/en/database-migrations)
- [Unit Testing](https://frappeframework.com/docs/user/en/testing)
