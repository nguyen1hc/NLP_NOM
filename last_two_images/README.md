# 17077 và 18592 — bản bổ sung để rà, chưa phải 2 bài đã chốt

17077: 276 box; nguồn có 279 ký tự sau chuẩn hóa. Bốn 〇 đưa vào Excluded;
box 186 là MISS tại 其 trong 以廣其傳. Các cột chữ lớn đã được xem trên dải ảnh
phóng to; 27 ô ghi chú/ngày tháng vẫn cần rà. Những chữ khác dạng giữa ảnh và
nguồn được giữ theo nguồn; không tự thay chữ trong Content.

18592: 237 vị trí dự thảo; đã sửa cột tên 梅氏…, các box tên 阮氏號妙科 và
phần đầu cột cúng tiến bên trái. 45 [] được đổi thành □, không còn gán MISS
cho các dấu này. Ảnh mất nét nhiều; toàn bộ 18592 vẫn mang cờ cần rà, đặc biệt
các ghi chú nhỏ và vị trí trống. Không thể xác nhận từng chữ hoặc ranh giới
các ô chỉ từ các vùng mờ hiện có; số lượng khớp nguồn không chứng minh box đúng.

`data/*.json` và `review/*.json` là dữ liệu rà. `*_review.png` cho thấy vị trí:
xanh = đã xem vị trí trên dải ảnh; vàng = còn cần kiểm tra. Những box không có
□ chưa có kết quả Intact/Damaged mới. Không lấy trạng thái khởi tạo làm nhãn
chuyên gia hoặc kết quả model.

## Nạp vào Kaggle

1. Giữ 7 bài hiện có trong `/kaggle/working/annotations`. Nếu là session mới,
   phục hồi backup 7 bài trước. Cell mới sẽ dừng nếu còn thiếu bài.
2. Tạo Dataset từ `last_two_kaggle.zip`, Add Input.
3. Chạy `kaggle/kaggle_cell.py` sau khi cài app/model, trước ô mở web.
4. Dùng ô mở web đang gọi APP_LAUNCHER. Model của app sẽ chạy cho 17077,18592
   trên các box này; không chạy lại detect box. Mức hỏng cần kiểm tra trên web.
5. Backup sau khi chạy: `/kaggle/working/my_annotations_backup.zip`, chứa
   dữ liệu của cả 9 ảnh. Đây là 9 ảnh có dữ liệu, không phải 9 bài đã xác minh.

Cell giữ các file bài làm và Content đã có của 7 ảnh trước, bao gồm 46302.
18592 xuất dạng annotation thường; 17077 dùng Other và `model_reviews` để giữ
nhãn đầy đủ cho trường hợp vừa dư vừa thiếu. Source student_114.json gốc giữ nguyên.
Chưa chạy model thật trong môi trường soạn gói. Kiểm tra bằng Workflow thật
với inference giả lập đã xác nhận nạp 2 ảnh, giữ nhãn/thứ tự và giữ 7 bài cũ.
