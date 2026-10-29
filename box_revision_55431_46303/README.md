# Rà lại box 55431 và 46303

Bản rà ảnh phóng to để kiểm tra, chưa chứng nhận mọi box/chữ đều chính xác.

- `review.html`: tải về, mở trong trình duyệt; bấm box để phóng to, xem chữ theo nguồn và lý do cần kiểm tra. Không cần mạng.
- `55431_comparison.png`, `46303_comparison.png`: trái là bản cũ, phải là bản sửa.
- `*_revised.png`: toàn ảnh với khung mới. Khung vàng là vị trí hoặc ranh giới còn chưa chắc.
- `data/*.json`: tọa độ, nhãn chữ, ánh xạ ID cũ/mới; chưa có kết quả model mới.
- `review/*.json`: các vị trí cần rà lại.

55431: 196 box. Đã sửa các ô cắt chữ 設 và 表, điều chỉnh theo độ nghiêng cột.
Ảnh ở đoạn này đọc 所以表; nguồn có thêm 上, nên đề xuất Excluded 上.
Chữ 祭 trong 以供丁祭之需 vẫn là MISS vì thiếu trong nguồn. Vì có cả thiếu và
thừa, bản native dùng Other và giữ nhãn đầy đủ trong `model_reviews/55431.json`.

46303: 208 box. Tách đoạn 后祖阮公… và phần ruộng 一所… thành hai cột thực tế;
phần thân có chín cột. Đầu cột thứ tư nhìn thấy 地處, chưa tìm được 墳 ở trước,
nên đề xuất Excluded 墳 cùng dấu 〇. Bỏ ô □ cuối cột 2 đang nằm ở mép trắng
không xác định được chữ; gộp nét cho 𣷷 và 泑 ở đầu cột 6/7, đề xuất đưa hai
所 dư vào Excluded. Đây là các đề xuất cần đối chiếu lại, chưa xác nhận chắc
ở vùng mờ. Có 12 ô vàng cần kiểm tra; nhất là các chữ sít nhau ở đầu cột 6/7 và
các vị trí □ cạnh mép bia/nếp gấp. Không xem số lượng box khớp là bằng chứng
mọi chữ đã đúng.

Content được giữ từ `annotations (3).zip`; không sửa nguyên văn Hán Nôm,
Hán Việt hay source `student_114.json` trong lần rà này. Năm bài còn lại,
bao gồm bản 46302 người dùng vừa sửa, được giữ trong dữ liệu Kaggle đi kèm.

## Xem trên Kaggle

Tải `kaggle_box_revision.zip`, tạo Dataset rồi Add Input. Chạy nội dung
`kaggle/kaggle_cell.py` sau các ô cài model và khai báo đường dẫn, trước ô
mở web dùng APP_LAUNCHER. Ô này thay bước nạp dữ liệu cũ trong lần này.
Nó nạp hai ảnh đã sửa và chạy lại model Intact/Damaged trên box mới. Nếu
output đã có bản sửa box khác, nó dừng để tránh ghi đè. Những ảnh khác đã
có trong output được giữ; nếu thiếu thì dùng bản trong ZIP gần nhất đã gửi.

Bản model trước dùng box khác nên không được coi là kết quả cho box mới.
Model thật chưa chạy tại môi trường soạn gói. Cell trên Kaggle sẽ chạy;
model chỉ đánh giá Intact/Damaged, các mức hỏng vẫn cần kiểm tra trên web.
File backup đầy đủ sau khi chạy là `/kaggle/working/my_annotations_backup.zip`.
