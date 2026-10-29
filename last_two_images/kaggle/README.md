# 17077 và 18592 — bản bổ sung sau ZIP mới nhất của người dùng

Gói này giữ nguyên 7 bài từ `input/user_seven_annotations.zip`: 17390, 18591,
31962, 55432, 46302, 55431, 46303. Đặc biệt, dùng box 55431 và 46303 mà người
dùng vừa sửa, không dùng lại bản assistant cũ. JSON gốc student_114 không đổi.

## Phần đã sửa

- **17077: 276 box.** Rà lại các ghi chú nhỏ, chỉnh biên 20 box để chứa nét chữ,
  trong đó có cụm ngày tháng 四月二十六日忌. Nguồn có 279 ký tự sau chuẩn hóa;
  bốn 〇 ở Excluded, box 186 là MISS cho 其 trong 以廣其傳. Các vị trí đã được
  xem trên ảnh phóng to; việc này không xác nhận độ đúng của mọi phiên đọc.
- **18592: 237 vị trí dự thảo, chưa hoàn tất.** Chỉnh cột ghi chú, chuyển phần
  tiếp nối 行庚□□□ và □年行更□□□ về cuối cột phải thay vì đầu cột trái.
  Vẽ lại cụm 壽八十二: 壽 là một chữ cao, 八 nhỏ ở sát trên 十.
  45 ký hiệu [] thành □. 220 vị trí vẫn mang cờ cần rà vì mờ hoặc chưa đối
  chiếu đủ; các □ ở phần mất nét chưa có ranh giới chắc chắn. Không dùng việc
  đủ số lượng để kết luận box đúng.
- Tại **18592 box 213**, nguồn ghi 月 nhưng ảnh có dạng 日. Đây là đề xuất cần
  xác nhận: giữ Content nguyên văn, dùng MISS ở box và Excluded một 月.
  Hai ảnh dùng Other và lưu đầy đủ nhãn trong `model_reviews`, tránh mất thông
  tin do định dạng Other của app chỉ xuất tọa độ.

`data/*.json` là bản rà, không phải nhãn Intact/Damaged đã chạy model.
Các trạng thái khởi tạo chỉ phục vụ nạp app; đã bỏ các cờ Expert Prediction và
Suspicious cũ do assistant suy đoán. Model thật sẽ chạy trên Kaggle, chỉ đánh
giá hỏng trên box cố định. Model không tự chọn mức hỏng hoặc xác minh chữ.

## Nạp vào Kaggle

1. Tải `last_two_kaggle.zip`, tạo/cập nhật Dataset rồi Add Input vào notebook.
   Chỉ gắn một Dataset có `last_two_manifest.json` để tránh chọn nhầm bản cũ.
2. Lưu bài đang làm và dừng ô chạy web. Chạy các ô cài app/model và khai báo
   REPO_PYTHON, REPO_DIR, IMAGE_DIR, SOURCE_JSON như trước.
3. Chạy cell trong `kaggle/kaggle_cell.py`, rồi ô mở web dùng APP_LAUNCHER.
   Source vẫn trỏ tới student_114.json gốc.
4. Cell tự phục hồi 7 bài nếu output trống; giữ các file/Content đã có của 7 bài
   nếu session còn dữ liệu. Nếu có box mới của 17077/18592 khác bản đã biết,
   cell dừng thay vì ghi đè. Chạy cell sau khi dừng web để tránh sửa đồng thời.
5. Model chỉ chạy cho 17077 và 18592, không tạo lại box. Sau đó có backup đủ
   9 ảnh tại `/kaggle/working/my_annotations_backup.zip`. Tải ZIP này về trước
   khi kết thúc session. Output không tự tồn tại qua mọi session mới.

**Giới hạn của ZIP người dùng:** 55431 được lưu dạng Other chỉ gồm tọa độ,
không có nhãn/trạng thái trong ZIP. Gói giữ nguyên tọa độ mới, không ghép
sidecar cũ khác box. Nếu output hiện tại còn sidecar 55431 thì cell giữ lại.
Không thể phục hồi nhãn/trạng thái chưa có trong file đã gửi.

## Kiểm tra và tái tạo

`review.html` cho phép chọn ảnh và số box để xem vị trí cùng lý do cần rà.
Màu xanh chỉ có nghĩa đã xem vị trí; không phải trạng thái Intact.

- `manual_box_corrections.json`: tọa độ sửa và lý do.
- `review/*.json`, `validation.json`: danh sách vị trí cần rà và số lượng.
- `input/*_seed.json`: dữ liệu đầu vào để tái tạo, có cả các ước lượng cũ.
- Chạy `build.py` bằng môi trường có các dependency của app; đặt
  SINONOM_REPO_DIR nếu clone app không ở `/tmp/sinonom-status-inspect`.
- `test_apply.py` kiểm tra bằng Workflow thật: nạp đủ 9 ảnh từ output trống,
  fallback khi Kaggle bỏ thư mục ẩn, giữ nguyên 7 bài mới nhất, không đổi
  source/box khi đánh giá hỏng, đọc nhãn/thứ tự và chặn ghi đè box mới.
  **Inference trong test là giả lập; chưa chạy model thật tại đây.**

## Sửa lỗi không hiện chữ ở Status & Order

Giao diện gốc ẩn chữ và màu trạng thái khi issue_type là Other, kể cả khi
launcher đã nạp đủ nhãn từ model_reviews. Launcher mới sửa điều kiện hiển thị
cho các ảnh đã có đủ nhãn tương ứng box. Không thay nhãn, tọa độ hoặc Content.
Với session đang chạy, dừng web và dùng `kaggle/fix_labels_cell.py`, rồi mở lại
web bằng APP_LAUNCHER; không cần chạy lại model hoặc cell nạp dữ liệu.
Test đã kiểm tra markup có đủ 276 nhãn của 17077, 237 nhãn của 18592, giữ
nguyên state và vẫn ẩn nhãn với bản Other chưa có mapping.
