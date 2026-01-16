# M001 Installation Checklist

## 📋 Pre-Installation

- [ ] **Frappe bench is running**
  ```bash
  cd ~/frappe-bench
  bench --version
  ```

- [ ] **Python version compatible** (3.10+, 3.12 recommended)
  ```bash
  python3 --version
  ```

- [ ] **Site exists**
  ```bash
  bench --site [your-site] list-apps
  ```

## 🚀 Installation Steps

### Step 1: Install ERPNext
- [ ] **Check if ERPNext installed**
  ```bash
  bench --site [your-site] list-apps | grep erpnext
  ```

- [ ] **If not installed, install ERPNext v15**
  ```bash
  bench get-app erpnext --branch version-15
  bench --site [your-site] install-app erpnext
  ```
  ⏱️ Estimated time: 5-10 minutes

### Step 2: Run M001 Installation
- [ ] **Option A: Automated Script**
  ```bash
  cd ~/frappe-bench/apps/prototype/prototype/cashflow_management
  ./install_m001.sh [your-site]
  ```

- [ ] **Option B: Manual Installation**
  ```bash
  cd ~/frappe-bench
  bench --site [your-site] migrate
  bench --site [your-site] clear-cache
  bench build --app prototype
  ```

### Step 3: Verify Installation
- [ ] **Team DocType exists**
  ```bash
  bench --site [your-site] console
  >>> frappe.get_meta("Team")
  >>> exit()
  ```

- [ ] **Access Team List** → http://localhost:8000/app/team
  - Should load without errors
  - Should show "Create" button

- [ ] **Check Department custom fields**
  - Go to `/app/department`
  - Open any department
  - Should see "Mã Phòng Ban" field

- [ ] **Check Employee custom fields**
  - Go to `/app/employee`
  - Open any employee
  - Should see "Loại Nhân Viên" and "Nhóm Chính" fields

## 🧪 Testing

### Automated Tests
- [ ] **Run unit tests**
  ```bash
  bench --site [your-site] run-tests --doctype "Team"
  ```
  - All 6 tests should pass ✅

### Manual Testing

#### Test 1: Create Team
- [ ] Go to `/app/team/new`
- [ ] Fill fields:
  - Mã Nhóm: `TEST-001`
  - Tên Nhóm: `Test Team`
  - Phòng Ban: Select any
- [ ] Click Save → ✅ Should succeed

#### Test 2: BR-TEAM-002 (Duplicate Code)
- [ ] Try creating another team with code `TEST-001`
- [ ] Should show error: ❌ "Mã nhóm đã tồn tại"

#### Test 3: BR-TEAM-001 (Team Lead Department)
- [ ] Create team in "Department A"
- [ ] Try to set team_lead from "Department B"
- [ ] Should show error: ❌ "Trưởng nhóm không thuộc phòng ban"

#### Test 4: View Team Members
- [ ] Open any team
- [ ] Click **Nhóm** → **Xem Thành Viên**
- [ ] Should show popup with member list (or "Nhóm chưa có thành viên")

#### Test 5: Deactivation
- [ ] Create team and save
- [ ] Uncheck "Đang Hoạt Động"
- [ ] Save → ✅ Should succeed
- [ ] Status indicator should turn red

#### Test 6: Delete Protection
- [ ] Assign employee to team:
  ```bash
  bench --site [your-site] console
  >>> frappe.db.set_value("Employee", "EMP-001", "primary_team", "TEST-001")
  >>> exit()
  ```
- [ ] Try to delete team `TEST-001`
- [ ] Should show error: ❌ "Không thể xóa nhóm. Còn X nhân viên"

## 📊 Sample Data Setup (Optional)

- [ ] **Create sample data**
  ```bash
  bench --site [your-site] console
  >>> from prototype.cashflow_management.setup_m001 import setup_m001
  >>> setup_m001()
  >>> exit()
  ```

- [ ] **Verify sample data created**
  - 3 Departments: Outsourcing, R&D, Internal Operations
  - 5 Teams: FotoFinder, DGX, VTT, R&D, Support

## 🔍 Troubleshooting

### Issue: "Department DocType not found"
- [ ] **Install ERPNext**
  ```bash
  bench get-app erpnext --branch version-15
  bench --site [your-site] install-app erpnext
  ```

### Issue: Custom fields not showing
- [ ] **Clear cache and rebuild**
  ```bash
  bench --site [your-site] clear-cache
  bench build --app prototype --force
  bench restart
  ```

### Issue: Patches not running
- [ ] **Check patches.txt**
  ```bash
  cat apps/prototype/prototype/patches.txt
  # Should show M001 patches
  ```
- [ ] **Run migrate again**
  ```bash
  bench --site [your-site] migrate --skip-failing
  ```

### Issue: Team not in dropdown
- [ ] **Check permissions**
  ```bash
  bench --site [your-site] console
  >>> frappe.has_permission("Team", "read")
  >>> frappe.get_all("Team", fields=["name", "team_name"])
  ```

### Issue: Tests failing
- [ ] **Check employee exists**
  ```bash
  bench --site [your-site] console
  >>> frappe.db.exists("Employee", "TEST-EMP-001")
  ```
- [ ] **Check department exists**
  ```bash
  >>> frappe.db.exists("Department", "Test Department")
  ```

## ✅ Post-Installation

### Configuration
- [ ] **Review Team permissions**
  - Go to `/app/doctype/Team`
  - Check Role Permissions
  - Adjust as needed

- [ ] **Configure workspace** (Optional)
  - Add Team to Cashflow Management workspace
  - Create shortcuts for quick access

### Documentation Review
- [ ] Read [M001-README.md](./M001-README.md)
- [ ] Review [business-rules.yml](./project-docs/shared/business-rules.yml)
- [ ] Check [schema.sql](./project-docs/shared/schema.sql)

### Data Entry
- [ ] **Create real departments**
  - Go to `/app/department`
  - Create your organization's departments
  - Set department codes

- [ ] **Create real teams**
  - Go to `/app/team`
  - Create teams matching your organization
  - Assign team leads

- [ ] **Update employees**
  - Go to `/app/employee`
  - Set employee_type (Regular/Intern/Freelancer)
  - Assign to primary_team

## 📈 Next Steps

- [ ] **Test in production-like environment**
  - Create various team configurations
  - Test with multiple employees
  - Verify reporting works

- [ ] **Proceed to M002**
  - Read M002 specification
  - Review M002 requirements
  - Plan M002 implementation

- [ ] **Integration testing**
  - Create sample projects
  - Assign projects to teams
  - Test team-based expense allocation

## 📝 Sign-off

| Item | Status | Date | Notes |
|------|--------|------|-------|
| Prerequisites verified | ⬜ | | |
| Installation completed | ⬜ | | |
| Tests passed | ⬜ | | |
| Manual testing done | ⬜ | | |
| Sample data created | ⬜ | | |
| Documentation reviewed | ⬜ | | |
| Ready for M002 | ⬜ | | |

---

**Installation performed by**: ________________  
**Date**: ________________  
**Site**: ________________  
**Version**: M001 v1.0  
**Status**: ⬜ Complete / ⬜ Issues (see notes)
