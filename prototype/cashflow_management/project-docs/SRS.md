PURPOSE
--------------------------------------------------------------------------------
Build a comprehensive management system to help the company:
- Track cash flow accurately (income, expenses, forecasting)
- Evaluate profit by group/project
- Manage 3 types of personnel: Full-time, Interns, Freelancers
- Control customer debts and payment collection
- Automate payroll process and export bank files
- Approve expense requests

SCOPE
--------------------------------------------------------------------------------
7 Main Modules:

M001 - Basic Setup
   • 2-level structure: Department → Team
   • Revenue-generating teams (e.g., FotoFinder, DGX, VTT, ...)
   • Non-revenue teams (e.g., R&D, Support, Sales, Marketing, ...)

M002 - HR Management
   • 3 types of employees with different salary calculations
   • Attendance, leave, performance evaluation

M003 - Contract & Project Management
   • Track contracts, payment milestones
   • Project classification: Contracted vs Internal R&D

M004 - Expense Management
   • Expense approval workflow
   • Group small office expenses together

M005 - Payroll Processing & Payroll Sheet
   • Auto-calculate salary by employee type
   • Export Excel file for bank transfer

M006 - Accounts Receivable & CRM Management
   • Auto-escalate based on overdue days
   • Record all collection actions

M007 - Reports & Analytics
   • Team performance (revenue, expenses, profit)
   • Cash flow forecast 3-12 months


14 MAIN FUNCTIONS DETAIL
--------------------------------------------------------------------------------

1. ORGANIZATIONAL STRUCTURE
   - Create departments and work teams
   - Classify revenue-generating teams (e.g., FotoFinder, DGX, VTT)
   - Classify non-revenue teams (e.g., R&D, Support, Sales, Marketing)
   - Assign team leaders

2. 3-TYPE EMPLOYEE MANAGEMENT
   
   Type A - Full-time Employees:
   • Have labor contracts
   • Bank transfer payment
   • Calculate social insurance
   • Calculate personal income tax
   • Tax-deductible expenses
   
   Type B - Interns:
   • No contract
   • Cash payment
   • Unit price × Days × Performance coefficient (0.6-1.5)
   • Expenses NOT tax-deductible
   
   Type C - Freelancers:
   • Have cooperation agreement
   • Bank transfer payment
   • 10% tax withholding
   • Tax-deductible expenses

3. CONTRACT MANAGEMENT
   - Multiple payment methods (e.g., Periodic, One-time)
   - Track each payment milestone
   - Auto-calculate days overdue
   - Alert overdue payments

4. 2-TYPE PROJECT MANAGEMENT
   
   Type 1 - Revenue-generating Projects, Type 2 - Non-revenue Projects:
   • Link revenue to contracts or R&D budget
   • Calculate profit = Revenue - Expenses
   • Have bonus policy (% of profit)
   • Track expenses

5. ATTENDANCE & LEAVE
   - Daily check-in, auto-calculate tardiness
   - Alert manager for attendance issues
   - Alert for abnormal leave patterns
   - Check leave balance before approval

6. PERFORMANCE EVALUATION
   - Scale 1-5
   - Manager evaluates employees
   - Leadership can adjust evaluations
   - Directly affects intern salary:
     Score 1 = ×0.6 | Score 2 = ×0.8 | Score 3 = ×1.0
     Score 4 = ×1.2 | Score 5 = ×1.5

7. EXPENSE MANAGEMENT
   - Expense approval workflow per company policy
   - Multiple expense categories (e.g., Office, Travel, Equipment, Marketing, R&D...)
   - Group small office expenses in same month, keep itemized list
   - R&D expenses linked to specific projects

8. AUTO SALARY CALCULATION
   
   Full-time Employees:
   • Net salary = Base + Allowances - Deductions
   • Social insurance
   
   Interns:
   • Base = Unit price × Days worked
   • Adjusted = Base × Performance coefficient
   • Net = Adjusted + Bonus
   
   Freelancers:
   • Total = Project fee or Hourly rate × Hours
   • Withholding = 10% × Total
   • Net = Total - Withholding

9. PAYROLL SHEET & BANK EXPORT
   - Consolidate all salaries in month
   - Export Excel file formatted for bank
   - File includes: Employee ID, Name, Account, Amount, Notes
   - Note example: "Salary 01/2026: Base 15M, Allow 2M, Ded -3.5M, Bonus 5M"

10. CUSTOMER CONTACT HIERARCHY
    - Set up multiple contact levels per customer
    - Example 3 levels:
      • Level 1: Account Manager (regular contact)
      • Level 2: Finance Manager (escalation)
      • Level 3: CFO/Director (highest escalation)

11. ACCOUNTS RECEIVABLE & AUTO-ESCALATION
    - Auto-detect overdue payments
    - Auto-escalate based on overdue days (customizable thresholds)
    - Auto-notify responsible person, BOD
    - Calculate collection probability by overdue level

12. COLLECTION ACTION RECORDING
    - Record all debt collection actions
    - Multiple action types (e.g., Phone call, Email, Meeting, Legal notice)
    - Track status of each action
    - Record customer payment commitments
    - Remind when next action needed

13. TEAM PERFORMANCE REPORT
    
    Revenue-generating Teams:
    • Revenue from contracts
    • Expenses = Personnel + Allocated expenses
    • Profit = Revenue - Expenses
    • Profit margin %
    
    Non-revenue Teams (R&D, Support, Sales):
    • Expenses = Personnel + Operating expenses
    • Display: "Operating expenses" or "R&D investment"
    • Don't calculate profit margin

14. CASH FLOW FORECAST
    
    Cash Inflow Forecast:
    • Based on contract payment schedule
    • Adjust for customer's historical delays
    • Calculate collection probability by debt status
    
    Cash Outflow Forecast:
    • Classify by Cash outflow source (e.g., Salary, Social Insurance, Project Bonus, Project Promotion, R&D Budget...)
    • Classify by Tax-deductible or not
    • Classify by Internally explainable or not
    
    Risk Assessment:
    • Analyze cash balance trending vs operating expenses
    • Visual charts for easy understanding

================================================================================