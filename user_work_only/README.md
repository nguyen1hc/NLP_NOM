# Chỉ giữ bài do bạn tự làm

[Tải ZIP để đưa lên Kaggle](my_annotations_backup.zip) ·
[Xem các JSON bài đã làm](original_user_data/annotations)

Bốn ảnh: 17390, 18591, 31962, 55432. Gói ban đầu có 597 box, hai normal
và hai source mismatch. Bản 55432 lấy từ ZIP cũ bạn đã gửi, không lấy bản
nháp 55432 do trợ lý tạo. Không sửa các JSON annotation bạn cung cấp.

Upload my_annotations_backup.zip thành Dataset riêng rồi Add Input vào
notebook tool. Thay cell khôi phục bộ chín ảnh bằng kaggle_restore_cell.py.
Chạy cell đó trước cell mở web đang dùng APP_LAUNCHER. Giữ Dataset ảnh/model.
Nguồn vẫn là student_114.json gốc trong Input.

Nếu working đã có chỉnh sửa mới của bạn, bộ nạp giữ bản working; nếu nhận
ra bản nháp 55432 đã biết của trợ lý, lấy lại bản bạn gửi. Các ảnh ngoài
bốn mã đã chọn được chuyển ra annotations_previous_<timestamp>, không xóa.
History của thư mục annotations chỉ đánh dấu bài đã lưu cho bốn ảnh này.
Ảnh khác vẫn có thể chọn để bắt đầu tự làm.

Kaggle working không phải nơi sao lưu lâu dài. Sau khi làm thêm:
1. Save Annotation trên web.
2. Stop ô web, giữ session.
3. Chạy: backup_my_work(ANNOTATION_DIR)
4. Tải /kaggle/working/my_annotations_backup.zip về máy và cập nhật Dataset
   backup bằng ZIP mới. Gói mới gồm cả các ảnh bạn vừa tự hoàn thành.
5. Phiên sau, nạp Dataset backup mới và chạy cell khôi phục.

Chỉ chạy cell khôi phục ở đầu phiên. Sau khi làm thêm, dùng cell sao lưu,
không chạy lại cell khôi phục bộ bốn ảnh cũ. Không cần chạy model hoặc detect
để khôi phục các box/nhãn đã lưu. Save notebook không tự bảo đảm giữ output.
