# Bản người dùng gửi: annotations (4).zip

Giữ nguyên dữ liệu xuất của cả 9 ảnh. 18592 có 233 box; tám ảnh còn lại
giống bản trước. Không chạy detection, không sửa Content, không đổi source gốc.

Các bản Other (17077, 18592, 55431) trong ZIP chỉ chứa tọa độ, không chứa nhãn
chữ hoặc Intact/Damaged. Không tự suy ra các trường còn thiếu. Nếu working còn
file model_reviews tương ứng đúng geometry thì giữ lại; bản phụ sai geometry
không dùng lại. Toàn bộ thư mục trước khi nhập được giữ bên cạnh annotations.

1. Đưa user_work_latest_kaggle.zip lên Kaggle Dataset, rồi Add Input.
2. Dừng cell mở web. Chạy nội dung kaggle_cell.py.
3. Chạy cell mở web cũ, giữ SOURCE_JSON trỏ student_114.json gốc.

Lần đầu nhập, ZIP người dùng gửi là bản chuẩn cho chín ảnh trong ZIP.
Các ảnh khác ngoài ZIP vẫn giữ nguyên. Chạy lại cùng gói sẽ giữ chỉnh sửa mới
trong working; không nhập đè lần nữa.
Sau nhập có /kaggle/working/latest_work_full_backup.zip; tải về để giữ qua session.
Chạy lại importer không thay nhãn mới bằng nhãn cũ.
