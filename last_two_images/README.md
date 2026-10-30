# Làm lại 17077 và 18592 — gói v3

Bản này thay box của hai ảnh 17077, 18592. Giữ nguyên dữ liệu 7 bài từ ZIP
người dùng gửi gần nhất: 17390, 18591, 31962, 55432, 46302, 55431, 46303.
Nếu Kaggle đang có bản mới hơn của 7 bài, cell giữ bản đang có.

## Thay đổi hình học và ghép chữ

- **17077: 276 box.** Rà lại các dải chữ, chỉnh biên 110 box chạm/cắt nét;
  giữ những box đã phù hợp. Nguồn 279 ký tự; bốn 〇 trong Excluded, box 186
  là MISS ở 其 trong 以廣其傳. Còn 5 vị trí cần rà nét/phiên đọc.
- **18592: 201 box, không còn 237 ô chia theo số chữ nguồn.** Vẽ lại 138
  tọa độ trong lần này và giữ các sửa trước ở ghi chú/ngày tháng đã phù hợp.
  Hai cột 原供… kết thúc giữa bia, không kéo tới đáy. Phần ghi ruộng chuyển
  sang hai cột chữ nhỏ; các glyph 供田貮皐 nằm ở đầu chung trước khi chia cột.
- Bỏ **36 box chưa xác định được vị trí từng chữ** trong vùng mờ. Chữ tương
  ứng vẫn giữ trong Content và được liệt kê trong
  `review/18592_unlocated.json` với chỉ số nguồn (đếm từ 1, gồm tiêu đề).
  Đây là các vị trí chưa ghép được, **không phải kết luận chữ không có trên bia**.
- Box **184 mới** (213 cũ, vị trí nguồn 213) đề xuất MISS: nguồn 月, ảnh có
  dạng 日. Giữ 月 trong Content và ghi Excluded để người dùng xác nhận.
  Tổng Excluded 18592 là 37: 36 vị trí chưa định vị + một 月 đề xuất khác chữ.
- 18592 còn **95 box cần rà** và các vùng chưa định vị. Gói là bản làm lại
  để kiểm tra, **chưa phải hai bài đã chốt đúng toàn bộ**. Không sử dụng số
  lượng khớp nguồn làm bằng chứng box đúng.

Không chỉnh chữ Hán Nôm để ép khớp box. Hai Content chỉ bỏ ngoặc và đổi []
thành □; 18592 vẫn đủ 45 □ trong nguồn, trong đó 15 đã ghép vào box. JSON
`student_114/student_114.json` gốc không đổi. Content của 7 bài giữ nguyên.

## Trạng thái và định dạng

Các trạng thái trong dữ liệu đóng gói chưa phải kết quả model mới. Cell Kaggle
chạy model hỏng của app trên **box cố định**, không detect lại box. Mức hỏng
và các chữ mờ vẫn cần kiểm tra. Không tự gán Expert Prediction hoặc Suspicious.

Hai ảnh dùng Other, với nhãn đầy đủ tại `annotations/model_reviews/*.json`.
Native `source_mismatches/*.json` chỉ chứa tọa độ theo schema của app.
Excluded trong sidecar và bản rà là danh sách đối chiếu; không phải chức năng
Excluded gốc của app cho loại Extra Content. Giữ nguyên cả thư mục output
hoặc dùng `my_annotations_backup.zip` để không mất các thông tin bổ sung này.

Launcher đã sửa lỗi Other có nhãn nhưng không hiện chữ/màu ở Status & Order.
Gói có thêm bản code hỗ trợ ở thư mục gốc, để khôi phục được khi thư mục
`annotations/_support` không được đưa lên Dataset đầy đủ.

## Nạp vào Kaggle

1. Tải ZIP mới `last_two_kaggle.zip`, cập nhật Dataset và phiên bản Input của
   notebook. Chỉ gắn một Dataset có `last_two_manifest.json`; bản mới là v3.
2. Lưu bài và dừng web. Sau các cell cài app/model và đường dẫn, chạy
   `kaggle/kaggle_cell.py`. Giữ SOURCE_JSON trỏ tới student_114.json gốc.
3. Cell phục hồi 7 bài nếu output trống, giữ 7 bài nếu đã có. Model chỉ chạy
   hai ảnh bổ sung. Nếu phát hiện box do người dùng chỉnh khác bản cũ đã biết,
   cell dừng và giữ nguyên output. Có backup trước khi thay dữ liệu.
4. Mở web bằng cell dùng APP_LAUNCHER. Sau khi sửa, Save Annotation ở Review.
5. Tải `/kaggle/working/my_annotations_backup.zip` trước khi end session.
   Đây là backup cả 9 ảnh và các file phụ; không phải khẳng định 9 bài hoàn tất.

ZIP gốc người dùng của **55431** là Other chỉ có tọa độ, không có nhãn/trạng
thái. Gói không gắn nhãn cũ khác box vào đó. Sidecar đang có trên Kaggle,
nếu có, được giữ nguyên.

## Đối chiếu và kiểm tra

Mở `review.html` trong trình duyệt để chọn từng box, xem số cũ/số mới,
vị trí nguồn và danh sách chưa ghép được. Xanh = đã xem vị trí; vàng = cần rà,
không phải Intact/Damaged. Vùng tím là khu vực chưa định vị được từng chữ.

`redo_geometry.json` ghi tọa độ sửa và lý do bỏ box; `review/*.json` giữ
liên hệ với số box cũ. `validation.json` ghi số lượng và tình trạng kiểm tra.
`data/*.json` là bản đầy đủ để rà, không dùng trực tiếp như native JSON của app.

Tái tạo: chạy `build.py`, `make_review.py`, `package.py`. Cần dependency của
app; SINONOM_REPO_DIR chỉ đến clone SinoNom-Annotation. `test_apply.py` dùng
Workflow thật kiểm tra nạp, Save/reopen, đủ nhãn trong markup Status & Order,
backup, giữ 7 bài và chặn ghi đè box mới. Test dùng inference giả lập; model
thật chưa chạy trong môi trường soạn gói. Hình học không thay khi model chạy.
