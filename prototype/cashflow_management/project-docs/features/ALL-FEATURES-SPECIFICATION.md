# Complete Feature Specifications - Phase 1
# Cashflow Management System

**Version**: 1.0  
**Date**: January 15, 2026  
**Features**: F001-F014

---

## TABLE OF CONTENTS

1. [F001: Department & Team Master](#f001-department--team-master)
2. [F002: Employee Management](#f002-employee-management)
3. [F003: Contract Management](#f003-contract-management)
4. [F004: Project Types](#f004-project-types)
5. [F005: Attendance & Leave](#f005-attendance--leave)
6. [F006: Performance Rating](#f006-performance-rating)
7. [F007: Expense Management](#f007-expense-management)
8. [F008: Salary Processing](#f008-salary-processing)
9. [F009: Salary Table & Bank Export](#f009-salary-table--bank-export)
10. [F010: Customer Contact Management](#f010-customer-contact-management)
11. [F011: Debt Management & Escalation](#f011-debt-management--escalation)
12. [F012: Collection Actions](#f012-collection-actions)
13. [F013: Team Performance Report](#f013-team-performance-report)
14. [F014: Cashflow Forecast](#f014-cashflow-forecast)

---

# F001: Department & Team Master

**Module**: M001 | **Priority**: Critical | **Uses**: tabDepartment, tabTeam

## Labels
- Department → "Phòng Ban"
- Team → "Nhóm"
- team_code → "Mã Nhóm"
- team_lead → "Trưởng Nhóm"
- is_revenue_generating → "Tạo Ra Doanh Thu"

## Key User Stories

**US-001: Create 2-Level Organization Structure**
- Admin creates departments (Level 1: Outsourcing, R&D, Internal)
- Admin creates teams under departments (Level 2: FotoFinder, DGX, VTT)
- Each team has: code, name, team lead, revenue flag
- Validation: Team must have department (BR-TEAM-001)

**US-002: Assign Team Lead**
- Select employee as team lead
- System auto-fetches employee name

**US-003: Mark Revenue Generating Teams**
- Contract teams: is_revenue_generating = Yes
- R&D teams: is_revenue_generating = No
- Impacts profitability calculations

## Business Rules
- BR-TEAM-001: Team must belong to department
- BR-TEAM-002: Team code must be unique

## Testing
```
✓ Create dept "Outsourcing" → Success
✓ Create team "FotoFinder" under Outsourcing → Success
✗ Create team without department → Error
✗ Create team with duplicate code → Error
```

---

# F002: Employee Management

**Module**: M002 | **Priority**: Critical | **Uses**: tabEmployee (customized)

## Labels
- Employee → "Nhân Viên"
- employee_type → "Loại Nhân Viên"
- Regular → "Chính Thức"
- Intern → "Thực Tập Sinh"
- Freelancer → "Cộng Tác Viên"
- payment_method → "Phương Thức Thanh Toán"

## Key User Stories

**US-001: Register Regular Employee**
- Enter details: name, DOB, contact
- Set type = "Regular"
- Upload employment contract (required: BR-EMP-002)
- Enter base salary
- Payment method = Bank (auto)
- Enter bank account details
- Validation: Contract must exist

**US-002: Register Intern**
- Enter details
- Set type = "Intern"
- Enter daily_rate (required: BR-EMP-003)
- Payment method = Cash (auto)
- No contract needed
- Flag as non-tax-deductible

**US-003: Register Freelancer**
- Enter details
- Set type = "Freelancer"
- Enter hourly rate OR project fee
- Upload freelance agreement
- Payment method = Bank
- 10% tax withholding auto-configured

**US-004: Prevent Type Change**
- Employee type locked after first save (BR-EMP-001)
- Must create new record if type changes

## Business Rules
- BR-EMP-001: Type cannot change once set
- BR-EMP-002: Regular needs contract
- BR-EMP-003: Intern needs daily_rate

## Employee Type Comparison

| Aspect | Regular | Intern | Freelancer |
|--------|---------|--------|------------|
| Contract | Required | No | Agreement |
| Payment | Bank | Cash | Bank |
| Tax | Deductible | Non-deductible | Deductible (10% withhold) |
| SS | Yes (10.5%/17.5%) | No | No |
| Calculation | Base + SS + Tax | Rate × Days × Perf | Project Fee - Tax |

---

# F003: Contract Management

**Module**: M003 | **Priority**: Critical | **Uses**: tabContract (customized), tabPayment Schedule

## Labels
- Contract → "Hợp Đồng"
- payment_type → "Hình Thức Thanh Toán"
- Long-term → "Dài Hạn"
- Monthly → "Hàng Tháng"
- One-time → "Một Lần"
- Payment Schedule → "Lịch Thanh Toán"

## Key User Stories

**US-001: Create Contract with Payment Terms**
- Enter customer, value, payment type
- Add payment milestones (child table)
- Each milestone: name, amount, expected date
- Validation: Sum of milestones = contract value (BR-CONTRACT-001)

**US-002: Track Payment Status**
- When payment received: enter actual_date
- System calculates delay_days (CR-DELAY-001)
- Status: Pending → Received or Overdue

**US-003: Flag Overdue Payments**
- If delay > 30 days → flag for follow-up (BR-PAY-001)
- Auto-create debt management record

## Business Rules
- BR-CONTRACT-001: Payment terms sum = contract value
- BR-PAY-001: Overdue > 30 days → flag

## Payment Types
- **Long-term**: Amortize revenue over period
- **Monthly**: Recognize revenue monthly
- **One-time**: Recognize on completion

---

# F004: Project Types

**Module**: M003 | **Priority**: Critical | **Uses**: tabProject (customized)

## Labels
- Project → "Dự Án"
- project_type → "Loại Dự Án"
- Contract-based → "Có Hợp Đồng"
- Internal R&D → "Nghiên Cứu Nội Bộ"
- rd_budget → "Ngân Sách R&D"
- bonus_policy → "Chính Sách Thưởng"

## Key User Stories

**US-001: Create Contract-Based Project**
- Link to contract (required: BR-PROJECT-001)
- Assign to team
- Set bonus policy % (of profit)
- Track revenue and profit

**US-002: Create Internal R&D Project**
- No contract allowed (BR-PROJECT-003)
- Set R&D budget (required: BR-PROJECT-002)
- Assign to team
- Track costs only (no revenue)

**US-003: Track Project Status**
- Status: On-time or Delayed
- If delayed → adjust payment dates (BR-PAY-002)

## Business Rules
- BR-PROJECT-001: Contract project needs contract
- BR-PROJECT-002: R&D project needs budget
- BR-PROJECT-003: R&D cannot have contract

## Project Type Comparison

| Aspect | Contract-Based | Internal R&D |
|--------|----------------|--------------|
| Revenue | Yes (contract value) | No (cost center) |
| Budget | No | Yes (R&D budget) |
| Profit Tracking | Yes | No (shows as loss/investment) |
| Bonus | Yes (% of profit) | Optional (milestone) |
| Team Impact | Profit center | Cost center |

---

# F005: Attendance & Leave

**Module**: M002 | **Priority**: Critical | **Uses**: tabAttendance (customized), tabLeave Application

## Labels
- Attendance → "Chấm Công"
- check_in → "Giờ Vào"
- late_minutes → "Số Phút Trễ"
- Leave Application → "Đơn Xin Nghỉ"
- Present → "Có Mặt"
- On Leave → "Nghỉ Phép"

## Key User Stories

**US-001: Daily Check-in**
- Employee clicks "Check In"
- System records timestamp
- If > 8:15 AM → calculate late_minutes (BR-ATT-001)
- If late_minutes > 15 → mark as late

**US-002: Manager Alert - Late Pattern**
- System checks: employee late > 3 times/month
- Send alert to manager (BR-ATT-002)
- Alert includes dates and total late minutes

**US-003: Track Intern Attendance for Salary**
- System tracks days attended (including half-days)
- Total = Full days + (Half days × 0.5)
- If < 15 days/month → alert manager (BR-ATT-003)
- Pass to salary calculation (CR-SALARY-INTERN-001)

**US-004: Submit Leave Request**
- Employee selects type, dates, reason
- System checks balance (BR-LEAVE-001)
- Submit for manager approval
- If > 10 days/month → alert manager (BR-LEAVE-002)

## Business Rules
- BR-ATT-001: Late if check-in > 15 min after start
- BR-ATT-002: Alert if late > 3 times/month
- BR-ATT-003: Alert if intern < 15 days/month
- BR-LEAVE-001: Cannot exceed balance
- BR-LEAVE-002: Alert if > 10 days/month

---

# F006: Performance Rating

**Module**: M002 | **Priority**: High | **Uses**: tabPerformance Rating (new)

## Labels
- Performance Rating → "Đánh Giá Hiệu Suất"
- rating_score → "Điểm Đánh Giá"
- rating_period → "Kỳ Đánh Giá"
- overridden_by_bod → "BGĐ Đã Điều Chỉnh"

## Key User Stories

**US-001: Manager Rates Employee**
- Select employee, period (month/quarter)
- Enter rating score (1-5, BR-PERF-003)
- Add comments
- Submit rating

**US-002: BOD Override Rating**
- BOD can modify any rating (BR-PERF-002)
- System records: original_rating, BOD user, override date
- Marked as overridden_by_bod = Yes

**US-003: Impact on Intern Salary**
- Rating required for intern salary (BR-PERF-001)
- Performance factor applied (CR-SALARY-INTERN-001):
  - Rating 1 → 0.6x
  - Rating 2 → 0.8x
  - Rating 3 → 1.0x
  - Rating 4 → 1.2x
  - Rating 5 → 1.5x

## Business Rules
- BR-PERF-001: Required for intern salary
- BR-PERF-002: BOD can override
- BR-PERF-003: Score 1-5 only

## Rating Scale
```
5 - Outstanding: 1.5x multiplier
4 - Exceeds Expectations: 1.2x multiplier
3 - Meets Expectations: 1.0x multiplier
2 - Needs Improvement: 0.8x multiplier
1 - Unsatisfactory: 0.6x multiplier
```

---

# F007: Expense Management

**Module**: M004 | **Priority**: High | **Uses**: tabExpense (new)

## Labels
- Expense → "Chi Phí"
- Category → "Danh Mục"
- Office → "Văn Phòng"
- Travel → "Đi Lại"
- Equipment → "Thiết Bị"
- approval_status → "Trạng Thái Duyệt"

## Key User Stories

**US-001: Finance Creates Expense**
- Only Finance role can create (BR-EXP-002)
- Enter date, category, amount, description
- Upload supporting documents
- Allocate to team/project (optional)
- Submit for BOD approval

**US-002: Group Small Office Expenses**
- Type = "Grouped"
- Add multiple expense items (child table)
- All same category (BR-EXP-003)
- All same month (BR-EXP-004)
- Submit batch for approval

**US-003: BOD Approves Expense**
- BOD reviews expense details
- Approve or reject with comments
- Cannot delete after approved (BR-EXP-007)

**US-004: Link R&D Expense to Project**
- If category = R&D
- Must select project (BR-EXP-006)
- Tracked against R&D budget

## Business Rules
- BR-EXP-001: ALL need BOD approval
- BR-EXP-002: Only Finance creates
- BR-EXP-003: Grouped = same category
- BR-EXP-004: Grouped = same month
- BR-EXP-006: R&D needs project
- BR-EXP-007: Cannot delete approved

---

# F008: Salary Processing

**Module**: M005 | **Priority**: Critical | **Uses**: tabSalary Slip (customized)

## Labels
- Salary → "Lương"
- Base Salary → "Lương Cơ Bản"
- Net Pay → "Thực Lĩnh"
- Payment Note → "Ghi Chú Thanh Toán"

## Key User Stories

**US-001: Process Regular Employee Salary**
- Gross = Base + Allowances
- Employee SS = Gross × 10.5%
- Tax = (Gross - 11M - Employee SS) × Rate
- Net = Gross - Employee SS - Tax + Bonus
- Payment: Bank
- Generate note (CR-PAYMENT-NOTE-001)

**US-002: Process Intern Salary**
- Check attendance exists (BR-SAL-001)
- Check performance rating exists (BR-SAL-002)
- Base = Daily Rate × Days Attended
- Adjusted = Base × Performance Factor
- Net = Adjusted + Bonus
- Payment: Cash
- Flag non-deductible (BR-SAL-007)

**US-003: Process Freelancer Payment**
- Gross = Project Fee or Hourly × Hours
- Tax Withholding = Gross × 10%
- Net = Gross - Tax
- Payment: Bank
- Require invoice

## Business Rules
- BR-SAL-001: Intern needs attendance
- BR-SAL-002: Intern needs performance
- BR-SAL-004: Note ≤ 200 chars
- BR-SAL-005: Regular needs SS calc
- BR-SAL-006: Freelancer 10% tax
- BR-SAL-007: Intern non-deductible

## Calculations
```
Regular:
  Gross = Base + Allowances
  Deductions = SS (10.5%) + Tax
  Net = Gross - Deductions + Bonus

Intern:
  Base = Daily Rate × Days × Performance Factor
  Net = Base + Bonus
  (Cash, non-deductible)

Freelancer:
  Gross = Project Fee
  Tax = Gross × 10%
  Net = Gross - Tax
```

---

# F009: Salary Table & Bank Export

**Module**: M005 | **Priority**: Critical | **Uses**: tabSalary Table (new)

## Labels
- Salary Table → "Bảng Lương"
- Export Status → "Trạng Thái Xuất"
- Bank File → "File Ngân Hàng"

## Key User Stories

**US-001: Consolidate Monthly Salaries**
- Finance clicks "Create Salary Table" for month
- System aggregates all salary slips
- Totals: employees, bank amount, cash amount
- Status: Draft

**US-002: BOD Approves Salary Table**
- BOD reviews consolidated table
- Check totals, payment notes
- Approve (BR-SAL-003)
- Status: Approved

**US-003: Export to Excel for Bank**
- Click "Export for Bank"
- System generates Excel file
- Columns: Employee Code, Name, Account, Amount, Note
- Format matches bank requirements
- Status: Exported

## Business Rules
- BR-SAL-003: Must approve before export

## Excel Format
```
| Employee Code | Employee Name | Bank Account | Amount | Payment Note |
|--------------|---------------|--------------|--------|--------------|
| EMP-001 | Nguyễn Văn A | 1234567890 | 20,004,250 | Lương tháng 01/2026: LCB 15M... |
```

---

# F010: Customer Contact Management

**Module**: M006 | **Priority**: High | **Uses**: tabCustomer Contact Hierarchy (new)

## Labels
- Customer Contact Hierarchy → "Phân Cấp Liên Hệ Khách Hàng"
- contact_level → "Cấp Độ Liên Hệ"

## Key User Stories

**US-001: Set Up Contact Hierarchy**
- For each customer, define contacts:
  - Level 1: Account Manager (daily contact)
  - Level 2: Finance Manager (escalation)
  - Level 3: CFO/Director (final escalation)
- Enter: name, role, email, phone

**US-002: Use Contacts in Escalation**
- System selects contact based on debt escalation level
- Sends notifications to appropriate level

## Contact Levels
```
Level 1: Account Manager
  - Day-to-day operations
  - 0-30 days overdue
  - Action: Call, Email

Level 2: Finance Manager
  - Escalation point
  - 31-60 days overdue
  - Action: Formal notice

Level 3: CFO/Director
  - Final escalation
  - 61+ days overdue
  - Action: Legal notice
```

---

# F011: Debt Management & Escalation

**Module**: M006 | **Priority**: High | **Uses**: tabDebt Management, tabEscalation Rule

## Labels
- Debt Management → "Quản Lý Công Nợ"
- Days Overdue → "Số Ngày Quá Hạn"
- Escalation Level → "Mức Độ Leo Thang"

## Key User Stories

**US-001: Auto-Create Debt Record**
- When payment overdue (BR-DEBT-001)
- System creates Debt Management record
- Links to contract, payment schedule
- Assigns to Account Manager

**US-002: Auto-Escalate Based on Days**
- System checks daily (BR-DEBT-002)
- Calculates days_overdue (CR-DEBT-OVERDUE-001)
- Escalates based on rules:
  - 0-15 days: Level 0 (monitor)
  - 16-30 days: Level 1
  - 31-60 days: Level 2
  - 61+ days: Level 3
- Sends notification (BR-DEBT-004)

**US-003: Adjust Cashflow Forecast**
- Apply payment probability (CR-DEBT-RISK-001):
  - Level 0-1: 95% collectible
  - Level 2: 80% collectible
  - Level 3: 50% collectible
- Reduce expected cash inflow

## Business Rules
- BR-DEBT-001: Auto-create on overdue
- BR-DEBT-002: Auto-escalate
- BR-DEBT-003: Cannot close if amount > 0
- BR-DEBT-004: Escalation triggers notification

## Escalation Timeline
```
Day 0-15: Monitor
  No action required
  Status: Pending

Day 16-30: Level 1
  Contact: Account Manager
  Action: Call customer

Day 31-60: Level 2
  Contact: Finance Manager
  Action: Formal notice

Day 61+: Level 3
  Contact: CFO
  Action: Legal consideration
```

---

# F012: Collection Actions

**Module**: M006 | **Priority**: High | **Uses**: tabCollection Action

## Labels
- Collection Action → "Hành Động Thu Hồi"
- Action Type → "Loại Hành Động"
- Call → "Gọi Điện"
- Email → "Email"
- Meeting → "Họp"

## Key User Stories

**US-001: Log Collection Action**
- Finance/Sales creates action
- Select type: Call, Email, Meeting, Legal Notice
- Enter date, customer contact
- Status: Planned

**US-002: Complete Action**
- Perform action (call customer, send email)
- Update status: Completed
- Enter outcome notes (BR-ACTION-002)
- If payment commitment: record amount and date

**US-003: Handle Failed Action**
- Status: Failed
- Must set follow-up date (BR-ACTION-003)
- Reschedule action

**US-004: No Action Reminder**
- If no action in 7 days (BR-ACTION-001)
- System sends reminder to assigned person

## Business Rules
- BR-ACTION-001: Remind if no action in 7 days
- BR-ACTION-002: Completed needs notes
- BR-ACTION-003: Failed needs followup date

---

# F013: Team Performance Report

**Module**: M007 | **Priority**: High | **Uses**: Custom Report

## Labels
- Team Performance → "Hiệu Suất Nhóm"
- Income → "Thu Nhập"
- Profit → "Lợi Nhuận"
- Margin → "Biên Lợi Nhuận"

## Key User Stories

**US-001: View Team P&L**
- Select team and period
- System calculates:
  - Income: Contract values (if contract team)
  - Labor Cost: Sum of employee costs
  - Expenses: Direct + shared allocation
  - Profit/Loss
  - Margin %

**US-002: Compare Multiple Teams**
- View all teams side-by-side
- Sort by profit, margin, cost
- Filter by department

**US-003: Track R&D Investment**
- R&D teams show as cost center (BR-REPORT-001)
- Display: "R&D Investment: -[Cost]"
- Margin: N/A (BR-REPORT-002)

## Calculations
```
Contract Team:
  Income = Sum(Contract Values)
  Cost = Labor + Expenses
  Profit = Income - Cost
  Margin % = (Profit / Income) × 100

R&D Team:
  Income = 0
  Cost = Labor + Expenses + R&D Budget
  Loss = -Cost
  Margin = N/A (Investment)
```

## Business Rules
- BR-REPORT-001: R&D shows negative profit
- BR-REPORT-002: R&D margin = N/A

---

# F014: Cashflow Forecast

**Module**: M007 | **Priority**: High | **Uses**: Custom Report

## Labels
- Cashflow Forecast → "Dự Báo Dòng Tiền"
- Cash Inflow → "Tiền Vào"
- Cash Outflow → "Tiền Ra"
- Net Cashflow → "Dòng Tiền Ròng"

## Key User Stories

**US-001: Generate 6-Month Forecast**
- Select horizon: 3, 6, or 12 months
- System calculates monthly:
  - Expected inflows (project payments)
  - Expected outflows (salaries, expenses)
  - Net cashflow
  - Cumulative balance

**US-002: Adjust for Payment Delays**
- Apply customer delay history (CR-CASHFLOW-INFLOW-001)
- Adjust dates based on past patterns
- Apply debt risk probability

**US-003: Assess Cashflow Risk**
- Calculate risk level (CR-CASHFLOW-RISK-001):
  - High: Balance < 1 month operating cost
  - Medium: Balance < 2 months
  - Low: Balance > 2 months

**US-004: Visualize Cashflow**
- Waterfall chart: Monthly movements
- Line chart: Cumulative balance
- Stacked bar: Inflow vs outflow categories

## Calculations

**Expected Inflow:**
```
For each payment milestone:
  Base Date = Milestone Due Date
  Adjusted Date = Base + Avg Customer Delay
  
  If debt level > 1:
    Probability = 95% (L0) | 80% (L2) | 50% (L3)
    Expected = Amount × Probability
  
  Monthly Inflow = Sum(Expected Amounts)
```

**Expected Outflow:**
```
Salaries = Sum(All employee net pay)
Bonuses = Sum(Project bonuses if milestone met)
Social Security = Sum(Regular employee SS)
Expenses = Sum(Approved expenses)
R&D = Sum(R&D budgets / duration)

Monthly Outflow = Salaries + Bonuses + SS + Expenses + R&D
```

**Net & Risk:**
```
Net Cashflow = Inflow - Outflow
Cumulative = Previous + Net

Risk:
  High if Cumulative < Monthly Operating Cost
  Medium if Cumulative < 2x Monthly Operating Cost
  Low otherwise
```

## Business Rules
- BR-REPORT-003: Updates daily
- BR-REPORT-004: Debt risk reduces inflow

---

## IMPLEMENTATION NOTES

### Testing Strategy

Each feature requires:
1. Unit tests (Python)
2. UI tests (JavaScript)
3. Integration tests
4. User acceptance testing

### Vietnamese Localization

All features require:
- DocType translations
- Field label translations
- Error message translations
- Report header translations
- Email template translations

---

**END OF FEATURE SPECIFICATIONS**
