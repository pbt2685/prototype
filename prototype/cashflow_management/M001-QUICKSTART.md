# M001: Quick Start Guide

## ⚡ Fast Installation

### Option 1: Automated Script (Recommended)
```bash
cd ~/frappe-bench/apps/prototype/prototype/cashflow_management
./install_m001.sh [your-site-name]
```

### Option 2: Manual Installation
```bash
cd ~/frappe-bench

# 1. Install ERPNext (if not already installed)
bench get-app erpnext --branch version-15
bench --site [site] install-app erpnext

# 2. Migrate prototype
bench --site [site] migrate

# 3. Clear cache and build
bench --site [site] clear-cache
bench build --app prototype

# 4. Setup sample data (optional)
bench --site [site] console
>>> from prototype.cashflow_management.setup_m001 import setup_m001
>>> setup_m001()
>>> exit()
```

## 🎯 Quick Test

### 1. Access Team List
```
http://localhost:8000/app/team
```

### 2. Create First Team
```
Team Code: ALPHA-TEAM
Team Name: Alpha Development Team
Department: [Select from dropdown]
Team Lead: [Select employee]
Is Revenue Generating: ✓
Active: ✓
```

### 3. Verify Installation
```bash
# Check if Team DocType exists
bench --site [site] console
>>> frappe.get_meta("Team")
>>> exit()

# Run tests
bench --site [site] run-tests --doctype "Team"
```

## 📊 Sample Data Created

After running `setup_m001()`, you'll have:

### Departments
- **Outsourcing** (OUTSRC): Revenue-generating contract teams
- **R&D** (RND): Internal research and development
- **Internal Operations** (INTERNAL): Support and operations

### Teams
1. **FotoFinder Team** (FF-TEAM) - Revenue generating
2. **DGX Team** (DGX-TEAM) - Revenue generating
3. **VTT Team** (VTT-TEAM) - Revenue generating
4. **Internal R&D Team** (RND-TEAM) - Non-revenue
5. **Support Team** (SUPPORT-TEAM) - Non-revenue

## 🔧 Common Tasks

### Assign Employee to Team
```python
import frappe

frappe.db.set_value(
    "Employee",
    "EMP-001",
    "primary_team",
    "FF-TEAM"
)
```

### Get Team Statistics
```python
from prototype.cashflow_management.doctype.team.team import get_team_summary

# All teams
teams = get_team_summary()

# Teams in specific department
outsourcing_teams = get_team_summary(department="Outsourcing")

for team in teams:
    print(f"{team.team_name}:")
    print(f"  Employees: {team.employee_count}")
    print(f"  Projects: {team.project_count}")
```

### View Team Members (UI)
1. Open Team form
2. Click **Nhóm** → **Xem Thành Viên**
3. See list of all employees in team

### View Team Projects (UI)
1. Open Team form
2. Click **Nhóm** → **Xem Dự Án**
3. See list of all projects assigned to team

## 🐛 Troubleshooting

### "Department DocType not found"
```bash
# Install ERPNext
bench get-app erpnext --branch version-15
bench --site [site] install-app erpnext
```

### Custom fields not visible
```bash
# Clear cache and rebuild
bench --site [site] clear-cache
bench build --app prototype --force
bench restart
```

### Patches didn't run
```bash
# Check patches
cat apps/prototype/prototype/patches.txt

# Run migrate again
bench --site [site] migrate --skip-failing
```

### Permission denied on script
```bash
chmod +x prototype/cashflow_management/install_m001.sh
```

## ✅ Verification Checklist

After installation, verify:

- [ ] Can access `/app/team` without errors
- [ ] Can create new team successfully
- [ ] Department has "Mã Phòng Ban" field
- [ ] Employee has "Nhóm Chính" field
- [ ] Employee has "Loại Nhân Viên" dropdown (Regular/Intern/Freelancer)
- [ ] Can assign team to employee
- [ ] Can view team members from Team form
- [ ] Vietnamese labels display correctly
- [ ] Business rules work (duplicate code, wrong department lead)

## 📈 What's Next?

Once M001 is working:

1. **Populate Real Data**
   - Create your actual departments
   - Create teams matching your organization
   - Assign employees to teams

2. **Proceed to M002**
   - Performance Rating DocType
   - Attendance customizations
   - Leave management

3. **Test Integration**
   - Create sample projects assigned to teams
   - Test team-based expense allocation
   - Generate team reports

## 📞 Support

If you encounter issues:
1. Check [M001-README.md](./M001-README.md) for detailed documentation
2. Review business rules in `/project-docs/shared/business-rules.yml`
3. Check logs: `tail -f ~/frappe-bench/logs/bench-start.log`

## 🎓 Learning Resources

- **Frappe Framework**: https://frappeframework.com/docs
- **ERPNext HR Module**: https://docs.erpnext.com/docs/user/manual/en/human-resources
- **Custom Fields**: https://frappeframework.com/docs/user/en/customization/custom-field
