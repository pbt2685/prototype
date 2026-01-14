# F004: Score Report Generation

**Module**: M001
**Priority**: P0
**Status**: ○ Planned
**Components**: DT007, RPT001, RPT002

## Purpose

Tự động tạo báo cáo điểm thi chi tiết sau khi kết thúc phiên thi, bao gồm điểm số cá nhân, thống kê lớp học, xếp hạng và phân tích hiệu suất từng câu hỏi để hỗ trợ giáo viên đánh giá và học sinh theo dõi kết quả.

## User Stories

### US-001: Generate Score Report After Session

**As a** Quản Trị Viên Thi / Giáo Viên
**I want to** tự động tạo báo cáo điểm sau khi phiên thi kết thúc
**So that** có thể xem kết quả tổng hợp và phân tích hiệu suất

**Acceptance Criteria**:
- [ ] Can tạo báo cáo cho phiên thi đã hoàn thành
- [ ] System validates tất cả học sinh đã nộp bài
- [ ] Cannot tạo báo cáo cho phiên thi đang diễn ra
- [ ] System calculates điểm số, xếp hạng, thống kê tự động
- [ ] Can xem báo cáo dạng bảng và xuất PDF/Excel

### US-002: View Individual Score Details

**As a** Giáo Viên
**I want to** xem chi tiết điểm và câu trả lời của từng học sinh
**So that** có thể đánh giá và phản hồi cho học sinh

**Acceptance Criteria**:
- [ ] Can xem điểm từng câu hỏi
- [ ] Can xem câu trả lời đúng/sai
- [ ] Can xem thời gian làm bài
- [ ] Can so sánh với điểm trung bình lớp
- [ ] Can xuất báo cáo cá nhân

### US-003: View Session Statistics

**As a** Giáo Viên / Quản Trị Viên
**I want to** xem thống kê tổng quan của phiên thi
**So that** có thể đánh giá độ khó và hiệu quả đề thi

**Acceptance Criteria**:
- [ ] Can xem điểm trung bình, cao nhất, thấp nhất
- [ ] Can xem tỷ lệ đậu/rớt
- [ ] Can xem phân tích từng câu hỏi (tỷ lệ đúng)
- [ ] Can xem biểu đồ phân bố điểm
- [ ] Can lọc theo lớp học

### US-004: Student View Own Score

**As a** Học Sinh
**I want to** xem điểm và câu trả lời của mình
**So that** có thể biết kết quả và học từ sai lầm

**Acceptance Criteria**:
- [ ] Can xem điểm tổng và phần trăm
- [ ] Can xem câu đúng/sai với đáp án
- [ ] Can xem xếp hạng trong lớp
- [ ] Cannot xem điểm của học sinh khác
- [ ] Can tải báo cáo PDF

## Business Process Flow

### Process: Auto Generate Report After Session

ACTORS: Hệ Thống, Giáo Viên

FLOW:
1. System → Kiểm tra phiên thi hoàn thành
   - Input: exam_session_name
   - Validation: BR-SCR-001, BR-SCR-002
2. System → Tính điểm từng học sinh
   - Calculation: CR-SCR-001, CR-SCR-002, CR-SCR-003
   - Loop through all participants
3. System → Tính thống kê lớp
   - Calculation: CR-SCR-004, CR-SCR-005
   - Generate ranking: CR-SCR-006
4. System → Tạo bản ghi Exam Score Report
   - Status: "Generated"
   - Link to exam_session
5. System → Gửi thông báo cho giáo viên
   - Notification: "Báo cáo điểm đã sẵn sàng"

### Process: Manual Generate Report

ACTORS: Giáo Viên, Quản Trị Viên

FLOW:
1. User → Mở Exam Session form đã hoàn thành
2. User → Click button "Tạo Báo Cáo Điểm"
3. System → Validate BR-SCR-001, BR-SCR-002
4. System → Execute auto generate flow
5. System → Redirect to Score Report

### Process: Export Individual Report

ACTORS: Giáo Viên, Học Sinh

FLOW:
1. User → Mở Exam Score Report
2. User → Chọn học sinh (hoặc xem của mình)
3. User → Click "Xuất PDF"
4. System → Generate PDF with:
   - Student info, score details
   - Question-by-question breakdown
   - Ranking and statistics
5. System → Download PDF file

## Business Rules

**BR-SCR-001: Session Completion Check**
- Applies to: Exam Session
- Rule: Report chỉ được tạo cho phiên thi có status = "Completed"
- Error Message: "Không thể tạo báo cáo cho phiên thi chưa hoàn thành"

**BR-SCR-002: All Participants Submitted**
- Applies to: Exam Session Participant
- Rule: Tất cả participants phải có status = "Submitted"
- Error Message: "Còn học sinh chưa nộp bài. Vui lòng chờ tất cả hoàn thành"

**BR-SCR-003: Passing Threshold Range**
- Applies to: Exam Score Report.passing_threshold
- Rule: 0 <= passing_threshold <= 100
- Error Message: "Điểm chuẩn phải từ 0 đến 100"

**BR-SCR-004: Duplicate Report Prevention**
- Applies to: Exam Score Report
- Rule: Mỗi exam_session chỉ có 1 active report
- Error Message: "Báo cáo cho phiên thi này đã tồn tại"

**BR-SCR-005: Student Access Control**
- Applies to: Report viewing
- Rule: Học sinh chỉ xem được điểm của mình
- Error Message: "Bạn không có quyền xem điểm của học sinh khác"

**CR-SCR-001: Calculate Total Score**
- Formula: `total_score = SUM(points_earned for correct answers)`
- Inputs: exam_session_participant.answers, exam_paper_question.points
- Output: participant_score.total_score

**CR-SCR-002: Calculate Percentage**
- Formula: `percentage = (total_score / max_possible_score) * 100`
- Inputs: total_score, exam_paper.total_points
- Output: participant_score.percentage

**CR-SCR-003: Determine Pass/Fail**
- Formula: `pass_status = "Pass" if percentage >= passing_threshold else "Fail"`
- Inputs: percentage, passing_threshold
- Output: participant_score.pass_status

**CR-SCR-004: Calculate Average Score**
- Formula: `average_score = SUM(all_participant_scores) / participant_count`
- Inputs: all participant scores
- Output: exam_score_report.average_score

**CR-SCR-005: Calculate Standard Deviation**
- Formula: `std_dev = SQRT(SUM((score - average)^2) / count)`
- Inputs: all scores, average_score
- Output: exam_score_report.std_deviation

**CR-SCR-006: Calculate Ranking**
- Formula: `rank = ORDER BY total_score DESC`
- Inputs: all participant scores
- Output: participant_score.rank

**CR-SCR-007: Calculate Question Statistics**
- Formula: `correct_rate = (correct_count / total_attempts) * 100`
- Inputs: participant answers per question
- Output: question_analysis.correct_percentage

## Data Model

**Primary Entity**: Exam Score Report (E007)

**Relationships**:

```
E007 (Exam Score Report)
├── BELONGS_TO: E005 (Exam Session) [N:1]
├── HAS_MANY: E008 (Participant Score) [1:N]
├── HAS_MANY: E009 (Question Analysis) [1:N]

E008 (Participant Score) [Child Table]
├── BELONGS_TO: E007 (Exam Score Report) [N:1]
├── LINKS_TO: E006 (Exam Session Participant) [1:1]

E009 (Question Analysis) [Child Table]
├── BELONGS_TO: E007 (Exam Score Report) [N:1]
├── LINKS_TO: E001 (Exam Question) [N:1]
```

**See**: shared/data-model.yml

## UI Requirements

**List View**: 
- Filters: exam_session, generated_on, status
- Columns: exam_session_name, total_participants, average_score, pass_rate, generated_on
- Default sort: generated_on DESC

**Form**: 
- Required: exam_session, passing_threshold
- Read-only: all statistics fields, generated_on, generated_by
- Child tables: participant_scores, question_analysis
- Sections: Session Info, Overall Statistics, Participant Scores, Question Analysis

**Note**: Form layout auto-generated at code generation.

## Integration Points

- Depends on: Exam Session (DT005), Exam Session Participant (DT006), Exam Paper (DT003)
- Triggers: 
  - On Exam Session.on_submit → Auto-generate report
  - On button click → Manual generate report
- Links to: Student reports, Teacher dashboard
- Notifications: Email teachers when report ready

## Testing Scenarios

**Scenario**: Generate report for completed session
```
Given exam session "SESS-2024-001" is completed
  And all 30 participants have submitted
When admin clicks "Tạo Báo Cáo Điểm"
Then system creates Exam Score Report
  And calculates all scores correctly
  And ranks participants 1 to 30
  And sends notification to teacher
```

**Scenario**: Prevent report for incomplete session
```
Given exam session "SESS-2024-002" has status "In Progress"
When admin clicks "Tạo Báo Cáo Điểm"
Then system shows error "Không thể tạo báo cáo cho phiên thi chưa hoàn thành"
  And no report is created
```

**Scenario**: Prevent duplicate reports
```
Given exam session "SESS-2024-001" already has score report
When admin tries to create another report
Then system shows error "Báo cáo cho phiên thi này đã tồn tại"
```

**Scenario**: Student views own score
```
Given student "John Doe" has completed exam
  And score report is generated
When student opens report
Then system shows only John's score and details
  And system hides other students' scores
```

**Scenario**: Export individual PDF
```
Given teacher opens score report
When teacher selects student "Jane Smith"
  And clicks "Xuất PDF"
Then system generates PDF with:
  - Student info and photo
  - Score breakdown by question
  - Correct/incorrect answers
  - Rank and statistics
```

## Technical Implementation

**See**: 
- components/DT007-exam-score-report.md
- components/RPT001-individual-score-report.md
- components/RPT002-session-statistics-report.md

## References

- Business Rules: BR-SCR-001 to BR-SCR-005
- Calculations: CR-SCR-001 to CR-SCR-007
- Data Model: E007, E008, E009
- Related Components: DT005, DT006, DT003