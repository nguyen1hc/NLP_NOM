# Đối chiếu student_114.json với PDF nguồn

Đã đối chiếu 6 văn bia, 9 mặt bia; 18 trường metadata (tên, địa điểm, niên đại)
và 23 mục nội dung có sẵn trong JSON. Bổ sung 4 mục nội dung bị thiếu sau kiểm tra.
Nguồn: hai PDF trích trang trong student_114. Số trang dưới đây là trang trong
file PDF đang có, không phải số trang in trên sách.

Không thay đổi student_114/student_114.json. Hai bản dưới đây là file mới có cùng
schema và đủ 6 record, 9 mã ảnh như nguồn. Đây là giai đoạn kiểm tra nội dung;
chưa xác nhận khung, nhãn theo ảnh bia hay hoàn tất bài nộp.

## Hai bản kết quả

- student_114.reviewed.json: sửa lỗi nội dung/thiếu mục có căn cứ PDF; khôi phục
  xuống dòng phần Hán Nôm theo PDF. Giữ dấu ngoặc, dấu viết đài và dấu chú thích
  nguồn để còn tra cứu. Không dùng số chữ của bản này để ép số khung.
- student_114.normalized.draft.json: thêm bước chuẩn hóa phục vụ gán nhãn:
  [] rỗng -> □, bỏ vỏ ngoặc chú thích trong phần Hán Nôm nhưng giữ chữ bên trong,
  bỏ dấu viết đài 〇 khỏi chuỗi nhãn và bỏ số chú thích 1 sau 時. Các quy ước về
  dấu thực có/không có trên bia và dấu viết đài cần được xác nhận trước khi nộp.
  Nhãn Expert Prediction/Unknown vẫn phải được đặt cho khung tương ứng về sau.

## Những lỗi đã sửa

| Mã mặt bia | JSON ban đầu | Nội dung theo PDF / cách sửa | Nguồn |
|---|---|---|---|
| 46302 | 聞：積善餘慶 | Bổ sung 蓋, thành 蓋聞：積善餘慶 | Tập 4, PDF 4 / trang in 83 |
| 17390 | 鍮，錢一百貫 | Bổ sung 捐: 鍮，捐錢一百貫 | Tập 3, PDF 12 / trang in 455 |
| 17390 | 鍮，錢六拾貫 | Bổ sung 增捐: 鍮，增捐錢六拾貫 | Tập 3, PDF 12 / trang in 455 |
| 17390 | 錢一百貫，民支辨 | Bổ sung 助: 錢一百貫，助民支辨 | Tập 3, PDF 12 / trang in 455 |
| 31962 | 足亦 | 是亦, đối chiếu hình chữ trên PDF; phiên âm là “Thị diệc” | Tập 4, PDF 13 / trang in 526 |
| 18591 | Toát yếu bắt đầu bằng <18592> | Bỏ mã mặt bia bị lọt vào nội dung | Tập 3, PDF 9 / trang in 410 |
| 18592 | Thiếu Toát yếu | Bổ sung bản Toát yếu chung, PDF ghi cả <18591><18592> | Tập 3, PDF 9 / trang in 410 |
| 55432 / 55431 | Phiên âm hai mặt dồn vào 55432 | Tách phần từ “Thuận An phủ…” sang mặt 55431 | Tập 3, PDF 3–4 / trang in 277–278 |
| 55432 / 55431 | Cả hai thiếu Toát yếu | Chép phần Toát yếu chung đúng PDF cho cả hai; không tự viết tóm tắt mới | Tập 3, PDF 4 / trang in 278 |

Tổng cộng phát hiện 5 chữ Hán bị rơi tại hai mặt 46302 và 17390, một chỗ thay
chữ tại 31962, cùng các lỗi phân bổ/thiếu mục nêu trên. Không tự sửa nội dung
PDF theo suy đoán ngôn ngữ; giữ những cách viết có trong nguồn.

## Riêng ảnh 17077 bạn đang làm

Sau bỏ khác biệt khoảng trắng/xuống dòng, phần Hán Nôm trong JSON phù hợp phần
văn bản PDF; chưa thấy trường hợp rơi chữ tương tự 17390.
Số 283 mà tool đếm có cả 4 dấu 〇 và 4 dấu （）. Bản chuẩn hóa nháp còn 275.
Với 276 khung trong ảnh chụp màn hình CŨ, chênh lệch khi ấy sẽ là +1, không phải
mặc định thiếu 7. Không có file Detect hiện tại để xác nhận số khung hay vị trí.
Không thêm/xóa khung chỉ nhằm đạt 275; kiểm tra hình và quy ước chuẩn hóa trước.

## Phân biệt sai nội dung với khác mã/font

- Giữ 户 của mặt 55432 theo dữ liệu/glyph nguồn, chưa đủ căn cứ đổi thành 戶
  chỉ vì nhìn một ảnh nhỏ. Việc đổi này trong bản demo trước chưa đủ bằng chứng.
- Mặt 55431 có ⿈ (U+2FC8, Kangxi Radical Yellow), trong ngữ cảnh “Hoàng”. Glyph
  tham chiếu có cùng hình với một mã chữ khác. Giữ nguyên và đánh dấu cần xác
  nhận Unicode; không tự coi nhận diện hình đúng là chứng minh mã đúng.
- Giữ các chữ hiếm 𥸷, 𣷷, 𨕭, 𦝧, 𡧲 từ nguồn. Cần kiểm tra cách hiển thị font;
  không mặc định đổi tất cả chữ hiếm thành @.
- Các chữ trong [ ] có nội dung là chữ được bổ sung/đoán theo quy định nguồn;
  [] rỗng biểu thị chữ mất. Bỏ ngoặc không được làm mất thông tin cần đánh dấu
  Expert Prediction ở bước Status & Order.
- Chú thích 1 sau 時 ở mặt 46302 nói chữ trên bia nguyên là 辰 do kiêng húy.
  Đây là ghi chú cần giữ cho bước đối chiếu ảnh; không thay chính văn PDF bằng
  辰 tại bước kiểm tra nội dung.

## Kiểm tra và giới hạn

Các metadata và nội dung tiếng Việt có sẵn không có khác biệt nội dung mới rõ
ràng sau khi đối chiếu, ngoài lỗi phân bổ mục đã nêu. Không tự hiệu đính các
cách viết hoặc dấu câu vốn có trong PDF. So sánh bỏ qua khoảng trắng dùng để
phát hiện rơi chữ; sau đó khôi phục xuống dòng Hán Nôm theo dòng PDF.

Việc trích chữ PDF dùng so khớp font để hỗ trợ tìm chỗ cần soi, không phải bằng
chứng độc lập về Unicode. Các đề xuất được kiểm tra trên trang PDF hiển thị;
những glyph không xác định được chắc chắn được để lại trong needs_review.json.

Đã kiểm tra cả hai JSON bằng adapter nội dung gốc: 6 record, 9 mặt bia duy nhất,
đủ ba mục nội dung ở mỗi mặt, không thay mã ảnh, không thay metadata nguồn.
counts.json là số đếm bằng đúng hàm characters của tool; không phải số khung
đã được kiểm chứng trên ảnh.

## Sử dụng trên web

Để sửa riêng ảnh đang làm, mở Content và đối chiếu nội dung trong bản mới,
Save Content rồi kiểm tra số đếm lại. Không cần chạy Detect lại chỉ vì sửa chữ.
Đổi file SOURCE_JSON của notebook chỉ áp dụng khi app đọc lại nguồn; không tự
chuyển các sửa tay chưa lưu trong phiên web. Lưu/sao lưu phần đã làm trước khi
khởi động lại app. Bản normalized.draft cần được rà quy ước trước khi dùng nộp.

## Số ký tự theo hàm đếm của tool

| Mã ảnh | Gốc | Sửa theo PDF, giữ ký hiệu | Chuẩn hóa nháp |
|---|---:|---:|---:|
| 46302 | 446 | 447 | 421 |
| 46303 | 219 | 219 | 212 |
| 17390 | 248 | 252 | 238 |
| 17077 | 283 | 283 | 275 |
| 55432 | 55 | 55 | 55 |
| 55431 | 196 | 196 | 196 |
| 31962 | 134 | 134 | 132 |
| 18591 | 172 | 172 | 172 |
| 18592 | 282 | 282 | 237 |
