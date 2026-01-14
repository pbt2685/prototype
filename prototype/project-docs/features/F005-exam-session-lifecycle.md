# F005: Exam Session Lifecycle

**Module**: M001
**Priority**: P0
**Status**: ○ Planned
**Components**: DT005, DT006, DT007, API001, API002, API003, API004

## Purpose

Quản lý vòng đời hoàn chỉnh của phiên thi từ khi bắt đầu đến kết thúc, cho phép giám thị khởi động phiên thi, thí sinh nộp bài trong thời gian quy định, tự động kết thúc khi hết giờ, và tự động tạo báo cáo điểm sau khi hoàn thành.

## User Stories

### US-001: Start Exam Session

**As a** Giám Thị / Quản Trị Viên Thi
**I want to** khởi động phiên thi theo lịch
**So that** thí sinh có thể bắt đầu làm bài thi

**Acceptance Criteria**:
- [ ] Can start session from "Scheduled" status
- [ ] System validates current time >= scheduled start time
- [ ] Session status changes to "In Progress"
- [ ] System enables answer submission interface for participants
- [ ] Cannot start session that is already started or completed
- [ ] System logs start time and started_by user

### US-002: Submit Exam Answers

**As a** Thí Sinh
**I want to** nộp bài thi trong thời gian quy định
**So that** bài thi của tôi được chấm điểm

**Acceptance Criteria**:
- [ ] Can submit answers only when session status = "In Progress"
- [ ] System validates all required questions answered
- [ ] System records submission timestamp
- [ ] System prevents re-submission after first submit
- [ ] Can see remaining time during exam
- [ ] Cannot submit after session ends

### US-003: End Exam Session

**As a** Giám Thị / Quản Trị Viên Thi
**I want to** kết thúc phiên thi thủ công hoặc tự động
**So that** có thể chuyển sang giai đoạn chấm điểm

**Acceptance Criteria**:
- [ ] Can manually end session when time is up
- [ ] System auto-ends session when duration expires
- [ ] Session status changes to "Completed"
- [ ] System locks all answer submissions
- [ ] System triggers auto-generation of score report (F004)
- [ ] System logs end time and ended_by user

### US-004: Monitor Session Progress

**As a** Giám Thị / Quản Trị Viên Thi
**I want to** theo dõi tiến độ phiên thi theo thời gian thực
**So that** có thể quản lý và hỗ trợ thí sinh kịp thời

**Acceptance Criteria**:
- [ ] Can view session status (Scheduled/In Progress/Completed)
- [ ] Can see remaining time
- [ ] Can see submission rate (submitted/total participants)
- [ ] Can see list of participants who haven't submitted
- [ ] Dashboard updates in real-time

### US-005: View Exam Interface

**As a** Thí Sinh
**I want to** xem giao diện thi với câu hỏi và thời gian còn lại
**So that** có thể làm bài và quản lý thời gian

**Acceptance Criteria**:
- [ ] Can access exam only when session = "In Progress"
- [ ] Can see all questions from exam paper
- [ ] Can see countdown timer
- [ ] Can select answers for each question
- [ ] Can review answers before final submit
- [ ] System auto-submits when time expires

## Business Process Flow

### Process: Start Exam Session

ACTORS: Giám Thị, Quản Trị Viên Thi, Hệ Thống

FLOW:
1. User → Open Exam Session document
2. User → Click button "Bắt Đầu Thi"
3. System → Validate BR-SES-001 (scheduled time check)
4. System → Validate session.status = "Scheduled"
5. System → Update:
   - status = "In Progress"
   - actual_start_time = now()
   - started_by = current_user
6. System → Send notification to all participants
7. System → Enable answer submission interface
8. System → Start countdown timer (CR-SES-001)

### Process: Submit Exam Answers

ACTORS: Thí Sinh, Hệ Thống

FLOW:
1. Student → Access exam interface
2. System → Validate BR-SES-002 (session active)
3. Student → Answer questions
4. Student → Click "Nộp Bài"
5. System → Show confirmation dialog
6. Student → Confirm submission
7. System → Validate all required questions answered
8. System → Update Exam Session Participant:
   - status = "Submitted"
   - answers = JSON(question_id: answer)
   - submitted_at = now()
   - time_taken = submitted_at - actual_start_time
9. System → Show success message
10. System → Disable answer editing (BR-SES-005)

### Process: End Exam Session (Manual)

ACTORS: Giám Thị, Quản Trị Viên Thi, Hệ Thống

FLOW:
1. User → Open Exam Session document
2. User → Click button "Kết Thúc Thi"
3. System → Validate BR-SES-003 (minimum time elapsed)
4. System → Show confirmation with submission stats
5. User → Confirm end
6. System → Update:
   - status = "Completed"
   - actual_end_time = now()
   - ended_by = current_user
7. System → Lock all submissions
8. System → Auto-submit pending participants (mark as incomplete)
9. System → Trigger BR-SES-006 (auto-generate report)
10. System → Send notification to organizers

### Process: Auto-End Session (Scheduled)

ACTORS: Hệ Thống

FLOW:
1. System → Check CR-SES-001 (remaining_time = 0)
2. System → Trigger BR-SES-004 (auto-end)
3. System → Execute end session flow (same as manual)
4. System → Force submit all active participants
5. System → Log "Auto-ended due to time expiry"

### Process: Monitor Session Progress

ACTORS: Giám Thị, Quản Trị Viên Thi, Hệ Thống

FLOW:
1. User → Open Session Dashboard
2. System → Display:
   - Session status indicator
   - Remaining time (CR-SES-001)
   - Progress bar (CR-SES-002)
   - Submission rate (CR-SES-003)
   - Participant list with status
3. System → Auto-refresh every 30 seconds
4. User → Can view individual participant progress
5. User → Can send reminders to non-submitted participants

## Business Rules

**BR-SES-001: Session Start Time Validation**
- Applies to: Exam Session.start_exam_session()
- Rule: current_time >= scheduled_start_time - 15 minutes (grace period)
- Error Message: "Chưa đến giờ thi. Vui lòng chờ đến {scheduled_start_time}"

**BR-SES-002: Answer Submission Validation**
- Applies to: Exam Session Participant.submit_answers()
- Rule: session.status = "In Progress" AND current_time <= actual_end_time
- Error Message: "Phiên thi chưa bắt đầu hoặc đã kết thúc. Không thể nộp bài"

**BR-SES-003: Minimum Duration Check**
- Applies to: Exam Session.end_exam_session()
- Rule: (current_time - actual_start_time) >= (duration * 0.5)
- Error Message: "Phiên thi chưa đạt thời gian tối thiểu. Vui lòng chờ thêm {remaining} phút"

**BR-SES-004: Auto-End on Time Expiry**
- Applies to: Exam Session (scheduled job)
- Rule: current_time >= (actual_start_time + duration)
- Action: Auto-execute end_exam_session()

**BR-SES-005: Prevent Answer Modification**
- Applies to: Exam Session Participant
- Rule: Once status = "Submitted", answers field is read-only
- Error Message: "Không thể sửa bài thi đã nộp"

**BR-SES-006: Auto-Generate Score Report**
- Applies to: Exam Session.on_update (when status = "Completed")
- Rule: If status changes to "Completed", trigger generate_report_for_session()
- Action: Create Exam Score Report (F004)

**CR-SES-001: Calculate Remaining Time**
- Formula: `remaining_time = (actual_start_time + duration * 60) - current_time`
- Inputs: actual_start_time, duration (minutes), current_time
- Output: remaining_seconds (integer)
- Display: Format as MM:SS

**CR-SES-002: Calculate Session Progress**
- Formula: `progress = ((current_time - actual_start_time) / (duration * 60)) * 100`
- Inputs: actual_start_time, duration, current_time
- Output: progress_percentage (0-100)
- Display: Progress bar

**CR-SES-003: Calculate Submission Rate**
- Formula: `submission_rate = (submitted_count / total_participants) * 100`
- Inputs: submitted_count, total_participants
- Output: submission_rate_percentage
- Display: "X/Y đã nộp bài (Z%)"

## Data Model

**Updated Entity**: Exam Session (DT005)

**New Fields**:
```yaml
actual_start_time:
  type: Datetime
  label: "Thời Gian Bắt Đầu Thực Tế"
  read_only: 1

started_by:
  type: Link
  options: User
  label: "Người Bắt Đầu"
  read_only: 1

actual_end_time:
  type: Datetime
  label: "Thời Gian Kết Thúc Thực Tế"
  read_only: 1

ended_by:
  type: Link
  options: User
  label: "Người Kết Thúc"
  read_only: 1

status:
  type: Select
  options: "Scheduled\nIn Progress\nCompleted\nCancelled"
  default: "Scheduled"
  label: "Trạng Thái"
```

**Updated Entity**: Exam Session Participant (DT006)

**Updated Fields**:
```yaml
answers:
  type: JSON
  label: "Câu Trả Lời"
  description: "JSON: {question_id: answer_value}"

submitted_at:
  type: Datetime
  label: "Thời Gian Nộp Bài"
  read_only: 1

time_taken:
  type: Duration
  label: "Thời Gian Làm Bài"
  read_only: 1

status:
  type: Select
  options: "Registered\nIn Progress\nSubmitted\nIncomplete"
  default: "Registered"
  label: "Trạng Thái"
```

**See**: shared/data-model.yml

## UI Requirements

### Exam Session Form

**New Buttons**:
- "Bắt Đầu Thi" (visible when status = "Scheduled")
- "Kết Thúc Thi" (visible when status = "In Progress")
- "Xem Dashboard" (always visible)

**New Sections**:
- Session Status Section (collapsed=0)
  - Status indicator (color-coded)
  - Remaining time (live countdown)
  - Submission rate progress bar
  - Participant summary table

**Dashboard Widget**:
```
┌────────────────────────────────────────┐
│ PHIÊN THI: {session_name}             │
├────────────────────────────────────────┤
│ ⏱️  Thời gian còn lại: 45:23          │
│ 📊 Tiến độ: ████████░░ 80%            │
│ ✅ Đã nộp: 24/30 (80%)                │
├────────────────────────────────────────┤
│ Thí Sinh Chưa Nộp:                     │
│ • Nguyễn Văn A                         │
│ • Trần Thị B                           │
│ • Lê Văn C                             │
└────────────────────────────────────────┘
```

### Student Exam Interface (New Page)

**URL**: `/exam/{session_id}/take`

**Layout**:
```
┌────────────────────────────────────────────────┐
│ ⏱️  Thời gian còn lại: 45:23                  │
│ 📝 Câu hỏi: 5/20                              │
├────────────────────────────────────────────────┤
│ Câu 5: What is 2 + 2?                         │
│                                                │
│ ○ A. 3                                        │
│ ○ B. 4  [Selected]                            │
│ ○ C. 5                                        │
│ ○ D. 6                                        │
├────────────────────────────────────────────────┤
│ [◀ Câu Trước]  [Câu Tiếp ▶]  [📋 Xem Tổng]  │
│                              [✓ Nộp Bài]      │
└────────────────────────────────────────────────┘
```

**Note**: Full UI implementation in components/API001-start-exam-session.md

## Integration Points

- **Depends on**: 
  - Exam Session (DT005)
  - Exam Session Participant (DT006)
  - Exam Paper (DT003)
  - Exam Score Report (DT007, F004)
  
- **Triggers**: 
  - On start → Enable participant access, start timer
  - On submit → Update participant status, check completion
  - On end → Lock submissions, generate report (F004)
  - On time expiry → Auto-end session
  
- **API Methods**:
  - `start_exam_session(session_id)` → API001
  - `submit_exam_answers(session_id, answers)` → API002
  - `end_exam_session(session_id)` → API003
  - `get_session_status(session_id)` → API004
  
- **Scheduled Jobs**:
  - `check_session_expiry()` - Every 1 minute
  - `auto_end_expired_sessions()` - Every 1 minute

## Testing Scenarios

**Scenario**: Start exam session successfully
```
Given exam session "EXAM-2026-01-14-00001" with status "Scheduled"
  And current time is >= scheduled start time
When admin clicks "Bắt Đầu Thi"
Then system updates status to "In Progress"
  And system records actual_start_time
  And system sends notification to 30 participants
  And participants can access exam interface
```

**Scenario**: Cannot start session too early
```
Given exam session scheduled for 14:00
  And current time is 13:30
When admin clicks "Bắt Đầu Thi"
Then system shows error "Chưa đến giờ thi. Vui lòng chờ đến 14:00"
  And status remains "Scheduled"
```

**Scenario**: Student submits answers during exam
```
Given exam session is "In Progress"
  And student has answered all 20 questions
When student clicks "Nộp Bài"
  And confirms submission
Then system saves answers as JSON
  And system updates participant status to "Submitted"
  And system records submitted_at timestamp
  And system calculates time_taken
  And student cannot edit answers anymore
```

**Scenario**: Cannot submit after session ends
```
Given exam session status is "Completed"
When student tries to submit answers
Then system shows error "Phiên thi đã kết thúc. Không thể nộp bài"
  And answers are not saved
```

**Scenario**: Auto-end session on time expiry
```
Given exam session started at 14:00 with duration 90 minutes
  And current time is 15:30 (90 minutes elapsed)
When scheduled job runs
Then system auto-ends session
  And system updates status to "Completed"
  And system force-submits 5 pending participants with status "Incomplete"
  And system generates score report
```

**Scenario**: Manual end session before time
```
Given exam session started at 14:00 with duration 90 minutes
  And current time is 14:50 (50 minutes elapsed)
When admin clicks "Kết Thúc Thi"
Then system shows error "Phiên thi chưa đạt thời gian tối thiểu. Vui lòng chờ thêm 5 phút"
  And session continues
```

**Scenario**: End session with all submitted
```
Given exam session is "In Progress"
  And all 30 participants have submitted
  And minimum time has elapsed
When admin clicks "Kết Thúc Thi"
Then system updates status to "Completed"
  And system triggers auto-generate report
  And system shows success "Đã kết thúc phiên thi và tạo báo cáo điểm"
```

## Technical Implementation

**See**: 
- components/API001-start-exam-session.md
- components/API002-submit-exam-answers.md
- components/API003-end-exam-session.md
- components/API004-get-session-status.md
- components/DT005-exam-session.md (updates)
- components/DT006-exam-session-participant.md (updates)

## References

- Business Rules: BR-SES-001 to BR-SES-006
- Calculations: CR-SES-001 to CR-SES-003
- Data Model: E005 (updated), E006 (updated)
- Related Features: F004 (Score Report Generation)
- Module: M001 (Exam Management)