# Gán nhãn toàn bộ ảnh 17077.jpg

Mở nhanh:

- [ZIP đúng cấu trúc bốn file của bài nộp — bản nháp riêng ảnh 17077](17077_submission_draft.zip)
- [Ảnh toàn bộ khung và số thứ tự](17077_overview.jpg)
- [JSON chứa toàn bộ 276 khung](source_mismatches.json)
- [Báo cáo PDF](summary.pdf)
- [Bản xem tương tác](review.html): tải về rồi mở bằng trình duyệt; GitHub hiển thị mã HTML.
- [Bộ đầy đủ gồm JSON, ảnh, báo cáo và dữ liệu phục hồi cho tool](17077_complete.zip)

Phạm vi: CHỈ ảnh 17077, theo lựa chọn của người dùng. Không xử lý 8 ảnh còn lại.
Đã xác định 276 vị trí chữ, bao gồm chữ nhỏ trong hai chú thích cuối cột.
Khung/thứ tự được xác định từ ảnh gốc; không truy cập hay điều khiển web Kaggle.
Mức hư hại là đánh giá bằng mắt ở dạng sơ bộ, cần rà lại trước khi nộp.

## Xem kết quả
- Mở review.html bằng trình duyệt: bấm từng khung hoặc chữ để phóng to.
- 17077_overview.jpg: ảnh đánh dấu nhẹ để xem nhanh.
- 17077_annotated.jpg: bản đầy đủ, giữ độ phân giải ảnh gốc.
- characters_01.jpg, characters_02.jpg, characters_03.jpg: 276 crop và nhãn.
- character_review.json: từng ID, bbox, nhãn theo nguồn, chữ quan sát/đề xuất,
  nhóm đọc và trạng thái. Đây là tệp hỗ trợ rà soát, không phải schema nộp gốc.

## Chênh lệch đã tìm được
Nguồn PDF (Tập 4, trang PDF 10 / trang in 408) viết 以廣傳云耳.
Ảnh bia có 以廣其傳云耳: thêm một chữ 其 giữa 廣 và 傳.
Đây là Missing Content, vì nhãn nguồn thiếu một ký tự xuất hiện trên ảnh.
Khung 186 tương ứng chữ 其. Theo quy trình Missing Content của tool, nhãn xuất
cho khung này là MISS, không tự sửa chính văn PDF thành nội dung khác.
Chữ quan sát được 其 vẫn được lưu trong character_review.json và review_notes.json.
Xem missing_source_qi.jpg để kiểm chứng trực tiếp.

Số đếm: JSON gốc 283 (bao gồm 4 dấu 〇 và 4 ngoặc toàn chiều rộng).
Chuỗi nguồn dùng để gán nhãn sau bỏ các dấu biên tập đó có 275 ký tự.
Có 276 khung trên ảnh = 275 nhãn nguồn + 1 MISS, nên không phải thiếu 7 khung.
Dấu biên tập bị loại vì không phải chữ thực tại các vị trí đó trên ảnh; bản gốc
được giữ trong source_17077.original.json. Cần đảm bảo quy ước này phù hợp yêu cầu
môn học trước khi dùng bản xuất làm bài nộp.

## Ba file theo schema tool
- text_annotations.json: [] — ảnh này được lưu theo nhánh source mismatch.
- inscription_content.json: nội dung của ảnh 17077 sau đối chiếu/chuẩn hóa.
- source_mismatches.json: 1 record chứa TOÀN BỘ 276 khung, nhãn, thứ tự,
  crop và thông tin Missing Content của ảnh 17077.
Không được bỏ source_mismatches.json vì nghĩ text_annotations rỗng là chưa làm.
annotations.zip chứa đúng ba file này, do chính hàm save_export_archive tạo ra.

## Các phần cần rà kỹ
Có 18 khung bật Suspicious cho khác dạng chữ giữa nguồn và ảnh, gồm các chữ số
一/壹, 百/佰, 十/拾. Nhãn theo PDF được giữ nguyên; candidate quan sát được lưu riêng.
Riêng chữ 由 trong chú thích nhỏ được đề xuất là 扣 trên ảnh: đã đánh dấu Suspicious
và cần rà kỹ. Không tự thay chữ theo suy đoán trong Source Text.
Không đánh Expert Prediction chỉ vì chữ mờ. Không dùng Unknown cho MISS.
Tất cả mức hư hại cần kiểm tra lại; xem danh sách ưu tiên trong review_notes.json.

## Thứ tự đọc
Tiêu đề phải sang trái; các cột chính trên xuống dưới, phải sang trái.
Hai nhóm chữ nhỏ được ghép vào đúng vị trí trong câu, không xếp theo cỡ chữ.
Đoạn 情願出銀...: cuối cột chính 5, nối sang đầu cột chính 6 (không tính tiêu đề).

## Đưa trở lại tool
- source_17077.normalized.json là dữ liệu đầu vào cho RIÊNG ảnh 17077, cùng schema
  student JSON. Chỉ dùng nó khi kiểm tra ảnh này; các ảnh khác không có record.
- tool_output/source_mismatches/17077.json là record từng ảnh mà tool đọc được.
- tool_output/.state/content.json chứa nội dung đã lưu cho ảnh này.
- Khi ghép vào thư mục kết quả đã có, cần gộp registry content.json theo tên image,
  giữ các ảnh khác; không ghi đè cả registry một cách máy móc.
- Bản này đã được Workflow.open_image đọc lại đúng 276 khung và MISS ở 186.
  Các dấu xác minh workflow trên web vẫn cần được thực hiện; không giả mạo thao
  tác Save Annotation hay trạng thái đã duyệt trong phiên Kaggle hiện tại.

## Kiểm tra đã chạy
Validator của source_mismatches, content và crop đều đạt.
276 ID liên tiếp; đúng 1 MISS; 275 nhãn còn lại khớp chuỗi nguồn.
Mọi khung nằm trong ảnh và vùng crop [775,760,3125,4370].
Bộ đọc và bộ xuất của tool khôi phục nguyên record; xem validation.json.
Các kiểm tra kỹ thuật không thay thế kiểm tra chính xác chữ và mức hư hại.

## Bộ tải về
17077_complete.zip có toàn bộ JSON, ảnh minh họa, HTML, dữ liệu phục hồi cho tool
và summary.pdf cho riêng ảnh này. Đây chưa phải bộ nộp đầy đủ 9 ảnh của đồ án.
