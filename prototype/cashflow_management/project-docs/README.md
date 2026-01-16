# Cashflow Management System - Complete L1 Documentation

**Version**: 1.0  
**Date**: January 15, 2026  
**Phase**: Phase 1 (7 Modules, 14 Features)  
**Documentation Level**: L1 (Schema + Business Rules + Features)

---

## 📦 PACKAGE CONTENTS

This package contains complete **L1 documentation** for the Cashflow Management System:

### 1. **shared/** - Technical Foundation
- **schema.sql** (25KB) - Complete database schema with all tables, relationships, indexes
- **business-rules.yml** (14KB) - All validation rules and calculation formulas

### 2. **modules/** - Module Specifications
- **_registry.yml** - Master registry of all 7 modules
- **README.md** - Module overview and dependencies
- **M001-M007.yml** - Individual module specifications

### 3. **features/** - Feature Specifications
- **ALL-FEATURES-SPECIFICATION.md** (37KB) - **Complete specifications for all 14 features**
- **features-summary.md** - Quick reference for all features
- **_README.md** - Feature documentation guide

---

## 📋 QUICK START

### 1. Understand the Structure
```
Start here → modules/README.md
Then read → shared/schema.sql (understand data model)
Then read → features/ALL-FEATURES-SPECIFICATION.md (all features)
```

### 2. For Developers
- **Database**: `shared/schema.sql` - Execute to create all tables
- **Business Logic**: `shared/business-rules.yml` - Reference for validation/calculation code
- **Features**: `features/ALL-FEATURES-SPECIFICATION.md` - User stories and acceptance criteria

### 3. For Project Managers
- **Scope**: `modules/_registry.yml` - 7 modules, 30 days effort
- **Features**: `features/features-summary.md` - Quick feature overview
- **Priorities**: See implementation phases in feature spec

---

## 🗂️ FILE GUIDE

### **shared/schema.sql** (CRITICAL)
Complete database schema for ERPNext/Frappe:
- 12 new custom tables
- 8 ERPNext tables to customize
- All foreign keys and indexes
- Vietnamese charset support (utf8mb4)
- Naming series definitions

**Tables Created:**
1. `tabTeam` - 2-level org structure
2. `tabPerformance Rating` - Employee ratings
3. `tabPayment Schedule` - Contract milestones
4. `tabExpense` + `tabGrouped Expense Item` - Expense management
5. `tabSalary Table` + `tabSalary Table Item` - Payroll consolidation
6. `tabCustomer Contact Hierarchy` - 3-level escalation
7. `tabDebt Management` - Overdue tracking
8. `tabCollection Action` - Debt collection log
9. `tabEscalation Rule` - Auto-escalation rules

**ERPNext Tables Customized:**
1. `tabDepartment` - Add department_code
2. `tabEmployee` - Add employee_type, daily_rate, payment_method, primary_team
3. `tabAttendance` - Add late_minutes, is_half_day
4. `tabContract` - Add payment_type, total_contract_value
5. `tabProject` - Add project_type, rd_budget, bonus_policy, assigned_team
6. `tabSalary Slip` - Add payment_method, payment_note, is_cash_payment
7. `tabCustomer` - Link to contact hierarchy
8. `tabContact` - Add contact_level for escalation

### **shared/business-rules.yml** (CRITICAL)
All validation rules and calculations:
- 60+ business rules (BR-xxx-###)
- 25+ calculation rules (CR-xxx-###)
- Organized by module (M001-M007)
- Vietnamese error messages
- Trigger conditions

**Rule Categories:**
- Validation: Data integrity checks
- Alerts: Manager notifications
- Calculations: Salary, cost, profit formulas
- Workflows: Auto-escalation, approval flows

### **features/ALL-FEATURES-SPECIFICATION.md** (COMPREHENSIVE)
Complete specifications for all 14 features in one document:
- User stories with acceptance criteria
- Business rules by feature
- UI mockups and field definitions
- Testing scenarios
- Integration points
- Vietnamese labels
- Implementation notes

**Features Covered:**
1. F001: Department & Team Master
2. F002: Employee Management (3 types)
3. F003: Contract Management
4. F004: Project Types (Contract vs R&D)
5. F005: Attendance & Leave
6. F006: Performance Rating
7. F007: Expense Management
8. F008: Salary Processing
9. F009: Salary Table & Bank Export
10. F010: Customer Contact Management
11. F011: Debt Management & Escalation
12. F012: Collection Actions
13. F013: Team Performance Report
14. F014: Cashflow Forecast

---

## 🎯 SCOPE SUMMARY

### Phase 1 Included (7 Modules)
✅ M001: Core Setup  
✅ M002: Employee Management  
✅ M003: Contract & Project Management  
✅ M004: Expense Management  
✅ M005: Salary & Payroll  
✅ M006: Debt Management & CRM  
✅ M007: Reporting & Analytics  

### Phase 2 Deferred
❌ M008: Cash Reconciliation & Compliance (removed for simplicity)

### Effort Estimate
- **Total**: 30 days
- **Critical Path**: M001 → M002+M003 → M004+M005 → M006 → M007
- **Parallel Work**: M002 and M003 can run simultaneously

---

## 🔑 KEY FEATURES HIGHLIGHTS

### 1. Three Employee Types
- **Regular**: Bank payment, tax-deductible, social security
- **Intern**: Cash payment, non-deductible, attendance-based
- **Freelancer**: Bank payment, 10% tax withholding

### 2. Two Project Types
- **Contract-based**: Revenue generating, profit tracking
- **Internal R&D**: Cost center, budget tracking

### 3. Automated Debt Escalation
- **Level 0** (0-15 days): Monitor
- **Level 1** (16-30 days): Account Manager
- **Level 2** (31-60 days): Finance Manager
- **Level 3** (61+ days): CFO/Legal

### 4. Team-Level Profitability
- Track income and costs by team
- R&D teams as cost centers (investment)
- Margin % for revenue teams

### 5. Cashflow Forecasting
- Adjust for payment delays
- Apply debt risk probability
- 3/6/12 month horizon

### 6. Vietnamese Localization
- All DocTypes in Vietnamese
- Error messages in Vietnamese
- Reports in Vietnamese
- Payment notes in Vietnamese

---

## 💡 IMPLEMENTATION GUIDANCE

### Database Setup
```sql
-- 1. Backup existing ERPNext database
bench --site [sitename] backup

-- 2. Execute schema
mysql -u [user] -p [database] < shared/schema.sql

-- 3. Or use Frappe migration
# Add custom fields via UI or fixtures
# Create new doctypes via UI or JSON
```

### Testing Strategy
Each feature requires:
- **Unit tests**: Python business logic
- **UI tests**: JavaScript client code
- **Integration tests**: Cross-module workflows
- **UAT**: User acceptance testing

---

## 📊 DATA MODEL OVERVIEW

```
Department (1) ←─── (N) Team
    ↓
Team (1) ←─── (N) Employee
    ↓                  ↓
Project (N)        Attendance
    ↓                  ↓
Payment Schedule   Performance Rating
    ↓                  ↓
Debt Management    Salary Slip
    ↓                  ↓
Collection Action  Salary Table
```

**Key Relationships:**
- Department → Team → Employee (org structure)
- Contract → Payment Schedule → Debt (revenue tracking)
- Employee → Attendance → Performance → Salary (payroll)
- Team → Project → Expense (cost allocation)

---

## 🌐 VIETNAMESE LOCALIZATION

All modules include complete Vietnamese translations:

| English | Vietnamese |
|---------|------------|
| Department | Phòng Ban |
| Team | Nhóm |
| Employee | Nhân Viên |
| Regular | Chính Thức |
| Intern | Thực Tập Sinh |
| Freelancer | Cộng Tác Viên |
| Attendance | Chấm Công |
| Performance Rating | Đánh Giá Hiệu Suất |
| Salary | Lương |
| Expense | Chi Phí |
| Contract | Hợp Đồng |
| Project | Dự Án |
| Debt Management | Quản Lý Công Nợ |
| Collection Action | Hành Động Thu Hồi |
| Team Performance | Hiệu Suất Nhóm |
| Cashflow Forecast | Dự Báo Dòng Tiền |

---

## ⚙️ TECHNOLOGY STACK

- **Framework**: Frappe Framework / ERPNext v14/v15
- **Database**: MariaDB 10.3+
- **Backend**: Python 3.7+
- **Frontend**: JavaScript (Frappe Desk)
- **UI Framework**: Bootstrap 4
- **Character Set**: utf8mb4 (Vietnamese support)
- **Currency**: VND (Vietnamese Dong)

---

## 📞 NEXT STEPS

After reviewing L1 documentation:

### Option 1: Proceed to Code Generation
Generate actual Frappe/ERPNext code:
- DocType JSON definitions
- Python server-side code (validation, calculations)
- JavaScript client-side code (UI, forms)
- Unit tests

### Option 2: Request Modifications
Provide feedback on:
- Schema adjustments
- Business rule changes
- Feature additions/removals
- Priority changes

### Option 3: Implementation Planning
Use documentation for:
- Resource allocation
- Timeline planning
- Cost estimation
- Risk assessment

---

## 📝 DOCUMENT VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-15 | Initial L1 documentation (Phase 1) |

---

## ⚠️ IMPORTANT NOTES

1. **Cash Reconciliation Excluded**: M008 removed from Phase 1 to reduce complexity. Can be added in Phase 2.

2. **ERPNext Compatibility**: Schema designed for ERPNext v14/v15. May need adjustments for other versions.

3. **Custom vs Standard**: Uses mix of ERPNext standard doctypes (customized) and new custom doctypes.

4. **Data Migration**: Existing ERPNext data can be migrated using provided schema.

5. **Testing Required**: All features must be tested in development environment before production deployment.

6. **Vietnamese Support**: Requires utf8mb4 character set in MariaDB for proper Vietnamese text support.

---

## 📧 SUPPORT

For questions about this documentation:
- Review module README files first
- Check feature specifications for detailed info
- Refer to business rules for validation logic
- Consult schema for data relationships

---

**Documentation Status**: ✅ Complete and Ready for Implementation  
**Last Updated**: January 15, 2026  
**Generated By**: Claude AI - Frappe Development Assistant

---

**🚀 Ready to build a world-class cashflow management system for Vietnamese software companies!**
