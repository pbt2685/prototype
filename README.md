### Prototype

FaceNet

1. Cài đặt lần đầu
- Di chuyển vào thư mục dự án, gõ lệnh sau:
- chmod +x install.sh
- ./install.sh
- Truy cập vào: localhost:8000 để xem giao diện

2. Thư mục dự án
Root
- (module) exam: nơi chứa các thư mục doctype, report, print format của module Exam.
- (module) prototype: tương tự
- public: nơi chứa phần css, js cho cả dự án
- hooks.py: khai báo sử dụng css, js, hooks
- package.json: nơi chứa các thư viện javascript cài riêng cho app

Disclaimer:
- Các thư mục của đối tượng Doctype, Report, Print Format sẽ được tự động thêm vào file code trong quá trình định nghĩa trên giao diện
- Vì thế, người dùng nên định nghĩa trước doctype trên giao diện thay vì generate file json, hoặc nếu generate file json trước thì bắt buộc phải migrate để db cập nhật
- Phiên bản đã Test: Frappe v15, Ubuntu v24.04, Python 3.12
- Nếu bị lỗi không truy cập được vào redis-server: vào trong frappe-bench/site/common_site_config.json, đổi lại port của redis thành port chuẩn (thường là 6379) 

3. Khởi động lại dự án:
- cd ~/frappe-bench (Truy cập vào thư mục frappe-bench)
- bench start
