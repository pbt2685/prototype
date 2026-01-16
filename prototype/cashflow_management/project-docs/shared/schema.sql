-- ============================================
-- CASHFLOW MANAGEMENT SYSTEM - DATABASE SCHEMA
-- ============================================
-- Project: ERPNext Cashflow & Profitability Management
-- Company: Software Development Company (Vietnam)
-- ERPNext Version: v14/v15
-- Character Set: utf8mb4 (Vietnamese support)
-- Scope: Phase 1 (M001-M007)
-- ============================================

-- ============================================
-- M001: CORE SETUP
-- ============================================

-- Department (Level 1) - Customized ERPNext
-- Note: Uses existing tabDepartment, fields added via custom fields
-- Custom Fields to add:
-- - department_code VARCHAR(20)
-- - cost_center_allocation VARCHAR(140)

CREATE TABLE `tabTeam` (
  `name` VARCHAR(140) PRIMARY KEY,
  `team_code` VARCHAR(20) NOT NULL UNIQUE,
  `team_name` VARCHAR(100) NOT NULL,
  `department` VARCHAR(140) NOT NULL,
  `department_name` VARCHAR(100),              -- fetch_from: department.department_name
  `team_lead` VARCHAR(140),                    -- Link to Employee
  `team_lead_name` VARCHAR(100),               -- fetch_from: team_lead.employee_name
  `is_revenue_generating` INT DEFAULT 1,       -- 0=R&D/Internal, 1=Contract-based
  `active` INT DEFAULT 1,
  
  `creation` DATETIME(6),
  `modified` DATETIME(6),
  `modified_by` VARCHAR(140),
  `owner` VARCHAR(140),
  `docstatus` INT DEFAULT 0,
  `idx` INT DEFAULT 0,
  
  FOREIGN KEY (`department`) REFERENCES `tabDepartment` (`name`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (`team_lead`) REFERENCES `tabEmployee` (`name`)
    ON DELETE SET NULL ON UPDATE CASCADE,
    
  INDEX `idx_team_code` (`team_code`),
  INDEX `idx_department` (`department`),
  INDEX `idx_active` (`active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- M002: EMPLOYEE MANAGEMENT
-- ============================================

-- Employee - Customized ERPNext tabEmployee
-- Custom Fields to add:
-- - employee_type VARCHAR(20) [Regular|Intern|Freelancer]
-- - payment_method VARCHAR(20) [Bank|Cash]
-- - daily_rate DECIMAL(15,2)
-- - primary_team VARCHAR(140) Link to Team
-- - bank_account_number VARCHAR(50)
-- - bank_name VARCHAR(100)

CREATE TABLE `tabPerformance Rating` (
  `name` VARCHAR(140) PRIMARY KEY,
  `naming_series` VARCHAR(140) DEFAULT 'PERF-.YYYY.-',
  `employee` VARCHAR(140) NOT NULL,
  `employee_name` VARCHAR(100),                 -- fetch_from: employee.employee_name
  `employee_type` VARCHAR(20),                  -- fetch_from: employee.employee_type
  `team` VARCHAR(140),                          -- fetch_from: employee.primary_team
  `rating_period` DATE NOT NULL,
  `rating_date` DATE NOT NULL,
  `rating_score` INT NOT NULL,                  -- 1-5 scale
  `rated_by` VARCHAR(140) NOT NULL,             -- Link to Employee (Manager)
  `rated_by_name` VARCHAR(100),                 -- fetch_from: rated_by.employee_name
  `overridden_by_bod` INT DEFAULT 0,            -- 1 if BOD override
  `bod_override_user` VARCHAR(140),             -- User who did override
  `bod_override_date` DATETIME(6),
  `original_rating` INT,                        -- Before BOD override
  `comments` TEXT,
  `status` VARCHAR(20) DEFAULT 'Draft',         -- Draft|Submitted|Cancelled
  
  `creation` DATETIME(6),
  `modified` DATETIME(6),
  `modified_by` VARCHAR(140),
  `owner` VARCHAR(140),
  `docstatus` INT DEFAULT 0,
  `idx` INT DEFAULT 0,
  
  FOREIGN KEY (`employee`) REFERENCES `tabEmployee` (`name`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`rated_by`) REFERENCES `tabEmployee` (`name`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
    
  INDEX `idx_employee_period` (`employee`, `rating_period`),
  INDEX `idx_rating_date` (`rating_date`),
  INDEX `idx_status` (`status`),
  UNIQUE KEY `unique_employee_period` (`employee`, `rating_period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Attendance - Customized ERPNext tabAttendance
-- Custom Fields to add:
-- - late_minutes INT
-- - is_half_day INT

-- Leave Application - Use existing tabLeave Application (no customization needed)

-- ============================================
-- M003: CONTRACT & PROJECT MANAGEMENT
-- ============================================

-- Contract - Customized ERPNext tabContract
-- Custom Fields to add:
-- - payment_type VARCHAR(20) [Long-term|Monthly|One-time]
-- - total_contract_value DECIMAL(15,2)

CREATE TABLE `tabPayment Schedule` (
  `name` VARCHAR(140) PRIMARY KEY,
  `parent` VARCHAR(140) NOT NULL,              -- Link to Contract
  `parentfield` VARCHAR(140) DEFAULT 'payment_schedule',
  `parenttype` VARCHAR(140) DEFAULT 'Contract',
  `milestone_name` VARCHAR(100) NOT NULL,
  `milestone_description` TEXT,
  `milestone_amount` DECIMAL(15,2) NOT NULL,
  `expected_date` DATE NOT NULL,
  `actual_date` DATE,
  `payment_status` VARCHAR(20) DEFAULT 'Pending', -- Pending|Received|Overdue
  `delay_days` INT DEFAULT 0,                  -- computed: CR-DELAY-001
  `payment_reference` VARCHAR(140),            -- Link to Payment Entry
  
  `creation` DATETIME(6),
  `modified` DATETIME(6),
  `modified_by` VARCHAR(140),
  `owner` VARCHAR(140),
  `docstatus` INT DEFAULT 0,
  `idx` INT DEFAULT 0,
  
  FOREIGN KEY (`parent`) REFERENCES `tabContract` (`name`)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  INDEX `idx_parent` (`parent`),
  INDEX `idx_expected_date` (`expected_date`),
  INDEX `idx_status` (`payment_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Project - Customized ERPNext tabProject
-- Custom Fields to add:
-- - project_type VARCHAR(20) [Contract-based|Internal R&D]
-- - contract VARCHAR(140) Link to Contract
-- - rd_budget DECIMAL(15,2)
-- - bonus_policy_percent DECIMAL(5,2)
-- - assigned_team VARCHAR(140) Link to Team
-- - project_status VARCHAR(20) [On-time|Delayed]

-- ============================================
-- M004: EXPENSE MANAGEMENT
-- ============================================

CREATE TABLE `tabExpense` (
  `name` VARCHAR(140) PRIMARY KEY,
  `naming_series` VARCHAR(140) DEFAULT 'EXP-.YYYY.-',
  `expense_date` DATE NOT NULL,
  `category` VARCHAR(50) NOT NULL,             -- Office|Travel|Equipment|Marketing|R&D
  `expense_type` VARCHAR(20) NOT NULL,         -- Individual|Grouped
  `amount` DECIMAL(15,2) NOT NULL,
  `description` TEXT NOT NULL,
  `allocated_team` VARCHAR(140),               -- Link to Team (optional)
  `allocated_project` VARCHAR(140),            -- Link to Project (optional, for R&D)
  `initiated_by` VARCHAR(140) NOT NULL,        -- User (Finance)
  `approval_status` VARCHAR(20) DEFAULT 'Draft', -- Draft|Pending BOD|Approved|Rejected
  `approved_by` VARCHAR(140),                  -- User (BOD)
  `approval_date` DATE,
  `approval_comments` TEXT,
  `supporting_documents` TEXT,                 -- JSON array of file paths
  `journal_entry` VARCHAR(140),                -- Link to Journal Entry
  
  `creation` DATETIME(6),
  `modified` DATETIME(6),
  `modified_by` VARCHAR(140),
  `owner` VARCHAR(140),
  `docstatus` INT DEFAULT 0,
  `idx` INT DEFAULT 0,
  
  FOREIGN KEY (`allocated_team`) REFERENCES `tabTeam` (`name`)
    ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (`allocated_project`) REFERENCES `tabProject` (`name`)
    ON DELETE SET NULL ON UPDATE CASCADE,
    
  INDEX `idx_expense_date` (`expense_date`),
  INDEX `idx_category` (`category`),
  INDEX `idx_approval_status` (`approval_status`),
  INDEX `idx_team` (`allocated_team`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tabGrouped Expense Item` (
  `name` VARCHAR(140) PRIMARY KEY,
  `parent` VARCHAR(140) NOT NULL,              -- Link to Expense
  `parentfield` VARCHAR(140) DEFAULT 'expense_items',
  `parenttype` VARCHAR(140) DEFAULT 'Expense',
  `item_date` DATE NOT NULL,
  `item_description` VARCHAR(200) NOT NULL,
  `item_amount` DECIMAL(15,2) NOT NULL,
  `receipt_number` VARCHAR(50),
  
  `creation` DATETIME(6),
  `modified` DATETIME(6),
  `modified_by` VARCHAR(140),
  `owner` VARCHAR(140),
  `docstatus` INT DEFAULT 0,
  `idx` INT DEFAULT 0,
  
  FOREIGN KEY (`parent`) REFERENCES `tabExpense` (`name`)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  INDEX `idx_parent` (`parent`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- M005: SALARY & PAYROLL
-- ============================================

-- Salary Structure - Use existing tabSalary Structure (separate for each employee type)
-- Salary Slip - Use existing tabSalary Slip
-- Custom Fields to add to tabSalary Slip:
-- - payment_method VARCHAR(20) [Bank|Cash]
-- - payment_note VARCHAR(200)
-- - is_cash_payment INT DEFAULT 0

CREATE TABLE `tabSalary Table` (
  `name` VARCHAR(140) PRIMARY KEY,
  `naming_series` VARCHAR(140) DEFAULT 'SAL-TBL-.YYYY.-.MM.-',
  `month` VARCHAR(7) NOT NULL,                 -- Format: YYYY-MM
  `from_date` DATE NOT NULL,
  `to_date` DATE NOT NULL,
  `total_employees` INT DEFAULT 0,
  `total_amount` DECIMAL(15,2) DEFAULT 0,
  `bank_payment_amount` DECIMAL(15,2) DEFAULT 0,
  `cash_payment_amount` DECIMAL(15,2) DEFAULT 0,
  `export_status` VARCHAR(20) DEFAULT 'Draft', -- Draft|Approved|Exported
  `approved_by` VARCHAR(140),                  -- User (BOD)
  `approval_date` DATE,
  `export_date` DATETIME(6),
  `export_file` VARCHAR(200),                  -- Path to Excel file
  `export_by` VARCHAR(140),                    -- User
  
  `creation` DATETIME(6),
  `modified` DATETIME(6),
  `modified_by` VARCHAR(140),
  `owner` VARCHAR(140),
  `docstatus` INT DEFAULT 0,
  `idx` INT DEFAULT 0,
  
  INDEX `idx_month` (`month`),
  INDEX `idx_export_status` (`export_status`),
  UNIQUE KEY `unique_month` (`month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tabSalary Table Item` (
  `name` VARCHAR(140) PRIMARY KEY,
  `parent` VARCHAR(140) NOT NULL,              -- Link to Salary Table
  `parentfield` VARCHAR(140) DEFAULT 'salary_items',
  `parenttype` VARCHAR(140) DEFAULT 'Salary Table',
  `employee` VARCHAR(140) NOT NULL,
  `employee_name` VARCHAR(100),
  `employee_type` VARCHAR(20),
  `team` VARCHAR(140),
  `payment_method` VARCHAR(20),
  `bank_account_number` VARCHAR(50),
  `bank_name` VARCHAR(100),
  `base_amount` DECIMAL(15,2) DEFAULT 0,
  `allowances` DECIMAL(15,2) DEFAULT 0,
  `deductions` DECIMAL(15,2) DEFAULT 0,
  `bonus` DECIMAL(15,2) DEFAULT 0,
  `net_amount` DECIMAL(15,2) NOT NULL,
  `payment_note` VARCHAR(200),
  `salary_slip` VARCHAR(140),                  -- Link to Salary Slip
  
  `creation` DATETIME(6),
  `modified` DATETIME(6),
  `modified_by` VARCHAR(140),
  `owner` VARCHAR(140),
  `docstatus` INT DEFAULT 0,
  `idx` INT DEFAULT 0,
  
  FOREIGN KEY (`parent`) REFERENCES `tabSalary Table` (`name`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`employee`) REFERENCES `tabEmployee` (`name`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
    
  INDEX `idx_parent` (`parent`),
  INDEX `idx_employee` (`employee`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- M006: DEBT MANAGEMENT & CRM
-- ============================================

CREATE TABLE `tabCustomer Contact Hierarchy` (
  `name` VARCHAR(140) PRIMARY KEY,
  `customer` VARCHAR(140) NOT NULL,
  `contact` VARCHAR(140) NOT NULL,             -- Link to Contact
  `contact_name` VARCHAR(100),
  `contact_level` INT NOT NULL,                -- 1=Account Mgr, 2=Finance Mgr, 3=CFO
  `contact_role` VARCHAR(100),                 -- Job title
  `email` VARCHAR(140),
  `phone` VARCHAR(50),
  `is_active` INT DEFAULT 1,
  
  `creation` DATETIME(6),
  `modified` DATETIME(6),
  `modified_by` VARCHAR(140),
  `owner` VARCHAR(140),
  `docstatus` INT DEFAULT 0,
  `idx` INT DEFAULT 0,
  
  FOREIGN KEY (`customer`) REFERENCES `tabCustomer` (`name`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`contact`) REFERENCES `tabContact` (`name`)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  INDEX `idx_customer` (`customer`),
  INDEX `idx_contact_level` (`contact_level`),
  UNIQUE KEY `unique_customer_contact` (`customer`, `contact`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tabDebt Management` (
  `name` VARCHAR(140) PRIMARY KEY,
  `naming_series` VARCHAR(140) DEFAULT 'DEBT-.YYYY.-',
  `customer` VARCHAR(140) NOT NULL,
  `customer_name` VARCHAR(100),
  `contract` VARCHAR(140),                     -- Link to Contract
  `payment_schedule` VARCHAR(140),             -- Link to Payment Schedule
  `invoice_reference` VARCHAR(140),            -- Link to Sales Invoice
  `outstanding_amount` DECIMAL(15,2) NOT NULL,
  `due_date` DATE NOT NULL,
  `days_overdue` INT DEFAULT 0,                -- computed: CR-DEBT-OVERDUE-001
  `escalation_level` INT DEFAULT 0,            -- 0=monitoring, 1-3=escalated
  `current_status` VARCHAR(20) DEFAULT 'Pending', -- Pending|In Progress|Resolved|Written Off
  `assigned_to` VARCHAR(140),                  -- User
  `last_action_date` DATE,
  `next_followup_date` DATE,
  `resolution_date` DATE,
  `resolution_notes` TEXT,
  
  `creation` DATETIME(6),
  `modified` DATETIME(6),
  `modified_by` VARCHAR(140),
  `owner` VARCHAR(140),
  `docstatus` INT DEFAULT 0,
  `idx` INT DEFAULT 0,
  
  FOREIGN KEY (`customer`) REFERENCES `tabCustomer` (`name`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (`contract`) REFERENCES `tabContract` (`name`)
    ON DELETE SET NULL ON UPDATE CASCADE,
    
  INDEX `idx_customer` (`customer`),
  INDEX `idx_due_date` (`due_date`),
  INDEX `idx_escalation_level` (`escalation_level`),
  INDEX `idx_status` (`current_status`),
  INDEX `idx_assigned` (`assigned_to`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tabCollection Action` (
  `name` VARCHAR(140) PRIMARY KEY,
  `naming_series` VARCHAR(140) DEFAULT 'COLL-.YYYY.-',
  `debt_management` VARCHAR(140) NOT NULL,
  `action_type` VARCHAR(50) NOT NULL,          -- Call|Email|Meeting|Legal Notice
  `action_date` DATE NOT NULL,
  `performed_by` VARCHAR(140) NOT NULL,        -- User
  `customer_contact` VARCHAR(140),             -- Link to Contact
  `customer_contact_name` VARCHAR(100),
  `action_status` VARCHAR(20) DEFAULT 'Planned', -- Planned|Completed|Failed
  `action_details` TEXT NOT NULL,
  `outcome` TEXT,
  `followup_date` DATE,
  `payment_commitment` DECIMAL(15,2),          -- If customer commits
  `payment_commitment_date` DATE,
  
  `creation` DATETIME(6),
  `modified` DATETIME(6),
  `modified_by` VARCHAR(140),
  `owner` VARCHAR(140),
  `docstatus` INT DEFAULT 0,
  `idx` INT DEFAULT 0,
  
  FOREIGN KEY (`debt_management`) REFERENCES `tabDebt Management` (`name`)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  INDEX `idx_debt` (`debt_management`),
  INDEX `idx_action_date` (`action_date`),
  INDEX `idx_status` (`action_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tabEscalation Rule` (
  `name` VARCHAR(140) PRIMARY KEY,
  `rule_name` VARCHAR(100) NOT NULL UNIQUE,
  `days_overdue_threshold` INT NOT NULL,
  `escalation_level` INT NOT NULL,             -- 1, 2, 3
  `contact_level` INT NOT NULL,                -- 1=Account Mgr, 2=Finance Mgr, 3=CFO
  `required_action` VARCHAR(50) NOT NULL,      -- Call|Email|Meeting|Legal Notice
  `notification_template` TEXT,
  `is_active` INT DEFAULT 1,
  
  `creation` DATETIME(6),
  `modified` DATETIME(6),
  `modified_by` VARCHAR(140),
  `owner` VARCHAR(140),
  `docstatus` INT DEFAULT 0,
  `idx` INT DEFAULT 0,
  
  INDEX `idx_threshold` (`days_overdue_threshold`),
  UNIQUE KEY `unique_level` (`escalation_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- RELATIONSHIPS SUMMARY
-- ============================================
-- Department (1) ←─── (N) Team
-- Team (1) ←─── (N) Employee (primary_team)
-- Team (1) ←─── (N) Project (assigned_team)
-- Employee (1) ←─── (N) Performance Rating
-- Employee (1) ←─── (N) Attendance
-- Employee (1) ←─── (N) Leave Application
-- Contract (1) ←─── (N) Payment Schedule
-- Contract (1) ←─── (N) Project
-- Project (N) ←─── (1) Team
-- Expense (N) ←─── (1) Team (optional)
-- Expense (N) ←─── (1) Project (optional)
-- Salary Table (1) ←─── (N) Salary Table Item
-- Salary Table Item (N) ←─── (1) Employee
-- Customer (1) ←─── (N) Customer Contact Hierarchy
-- Customer (1) ←─── (N) Debt Management
-- Debt Management (1) ←─── (N) Collection Action

-- ============================================
-- NAMING SERIES
-- ============================================
-- Team: Auto-generated name field
-- Performance Rating: PERF-.YYYY.-
-- Payment Schedule: Auto (child table)
-- Expense: EXP-.YYYY.-
-- Salary Table: SAL-TBL-.YYYY.-.MM.-
-- Debt Management: DEBT-.YYYY.-
-- Collection Action: COLL-.YYYY.-

-- ============================================
-- INDEXES SUMMARY
-- ============================================
-- Performance indexes added for:
-- - Foreign key relationships
-- - Frequently filtered fields (status, date, team)
-- - Unique constraints (codes, email, period combinations)
-- - Search fields (name, ID)

-- ============================================
-- DATA TYPES
-- ============================================
-- VARCHAR(140): Standard Frappe name field
-- VARCHAR(20-100): Short text (codes, types, status)
-- TEXT: Long descriptions
-- DECIMAL(15,2): Currency (VND supports large amounts)
-- INT: Numbers, flags, counts
-- DATE: Dates without time
-- DATETIME(6): Timestamps with microseconds (Frappe standard)

-- ============================================
-- END OF SCHEMA
-- ============================================
