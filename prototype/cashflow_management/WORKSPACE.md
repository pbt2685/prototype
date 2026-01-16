# Cashflow Management Workspace

## 📊 Workspace Structure

The Cashflow Management workspace organizes all modules systematically into 8 functional sections:

### 🔷 M001: Core Setup
**Purpose**: Foundation - Team structure and organizational hierarchy
- **Team** - Manage teams and assignments
- **Department** - Department structure
- **Employee** - Employee master data
- **Project** - Project management

**Data Flow**: Department → Team → Employee → Project

---

### 🔷 M002: Employee Management
**Purpose**: Performance tracking and attendance
- **Performance Rating** - Monthly intern performance ratings
- **Attendance** - Daily attendance tracking

**Data Flow**: Employee → Attendance → Performance Rating → Salary Calculation

---

### 🔷 M003: Contract & Project Management
**Purpose**: Revenue tracking and payment schedules
- **Contract** - Client contracts
- **Payment Schedule** - Milestone-based payments
- **Customer** - Customer master data

**Data Flow**: Customer → Contract → Payment Schedule → Cash Inflow / Debt

---

### 🔷 M004: Expense Management
**Purpose**: Cost control with BOD approval
- **Expense** - All company expenses
- **Expense Pending BOD** (filtered view) - Expenses awaiting approval

**Data Flow**: Expense Request → BOD Approval → Approved Expense → Cost Allocation

---

### 🔷 M005: Salary & Payroll
**Purpose**: Monthly salary processing and bank payments
- **Salary Table** - Monthly consolidated salary
- **Create Salary Table** (quick action) - Generate new salary table

**Data Flow**: Employee + Attendance + Performance → Salary Calculation → Bank Export

---

### 🔷 M006: Debt & CRM
**Purpose**: Overdue payment tracking with escalation
- **Debt Management** - Track overdue payments
- **Collection Action** - Log collection efforts
- **Overdue Debts** (filtered view) - Active debts requiring action

**Data Flow**: Payment Schedule (Overdue) → Debt Record → Auto-Escalation → Collection Actions

---

### 🔷 M007: Reports & Analytics
**Purpose**: Decision-making insights
- **Team Performance Report** - Team P&L analysis
- **Cashflow Forecast Report** - Multi-month cash forecast

**Data Flow**: All Modules → Data Aggregation → Reports

---

### ⚡ Quick Actions
**Purpose**: Fast access to common tasks
- **New Team** - Create team quickly
- **New Performance Rating** - Rate intern performance
- **New Expense** - Submit expense for approval
- **New Payment Schedule** - Add payment milestone

---

## 📈 Dashboard Statistics (Live Counters)

The workspace displays real-time statistics:

1. **Active Teams** (Blue badge)
2. **Active Employees** (Green badge)
3. **Performance Ratings This Month** (Orange badge)
4. **Active Payment Schedules** (Yellow badge)
5. **Expenses Pending BOD Approval** (Red badge)
6. **Salary Tables This Month** (Purple badge)
7. **Active Debts** (Red badge - excluding resolved)

---

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORGANIZATIONAL SETUP (M001)                  │
│                                                                   │
│  Department → Team → Employee → Project                          │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE TRACKING (M002)                   │
│                                                                   │
│  Attendance (daily) → Performance Rating (monthly)               │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                  CONTRACT MANAGEMENT (M003)                      │
│                                                                   │
│  Customer → Contract → Payment Schedule                          │
│                           ↓                                       │
│                    (if overdue) → Debt Management (M006)         │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   EXPENSE CONTROL (M004)                         │
│                                                                   │
│  Expense Request → BOD Approval → Approved Expense               │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PAYROLL PROCESSING (M005)                     │
│                                                                   │
│  Employee + Attendance + Performance → Salary Table → Bank File  │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DEBT MANAGEMENT (M006)                        │
│                                                                   │
│  Overdue Payment → Debt Record → Auto-Escalation →              │
│  Collection Action → Payment Received                            │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                 REPORTING & ANALYTICS (M007)                     │
│                                                                   │
│  All Data → Team Performance Report                              │
│          → Cashflow Forecast Report                              │
│          → Decision Making                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Module Dependencies

```
M001 (Core Setup)
  ↓
M002 (Employee Management) ─────┐
  ↓                             ↓
M003 (Contract & Project) ───→ M005 (Salary & Payroll)
  ↓                             ↓
M004 (Expense Management) ───→ M007 (Reports & Analytics)
  ↓                             ↑
M006 (Debt & CRM) ──────────────┘
```

**Key Dependency Rules**:
- M001 must be set up first (foundational data)
- M002 feeds into M005 (attendance → salary)
- M003 feeds into M006 (overdue payments → debt)
- M007 consumes data from all other modules

---

## 🔐 Access Control

**System Manager**: Full access to all modules  
**Accounts Manager**: Full access to M003, M004, M005, M006, M007  
**Sales Manager**: Access to M001, M002, M003, M006  
**Sales User**: Limited access to M003, M006  
**HR Manager**: Access to M001, M002, M005  

---

## 🚀 Getting Started

1. **Setup Phase** (M001):
   - Create Departments
   - Create Teams
   - Add Employees
   - Create Projects

2. **Operations Phase** (M002-M006):
   - Track attendance daily
   - Rate intern performance monthly
   - Log expenses and get BOD approval
   - Manage contracts and payment schedules
   - Process monthly salaries
   - Track and collect debts

3. **Analysis Phase** (M007):
   - Review team performance
   - Forecast cashflow
   - Make data-driven decisions

---

## 📱 Access the Workspace

Navigate to: **Desk → Cashflow Management** workspace

Or use quick link: `/app/cashflow-management`
