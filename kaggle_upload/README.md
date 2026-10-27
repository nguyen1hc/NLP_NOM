# Dữ liệu để khôi phục trên Kaggle

Gói có đủ **9 ảnh / 1.940 box**, gồm ba bài bạn cung cấp (17390, 18591, 31962) và bản nháp cho sáu ảnh còn lại. Box, nhãn, trạng thái và crop của ba bài bạn cung cấp được giữ nguyên.

## File cần dùng

- **[student_114_kaggle_restore.zip](student_114_kaggle_restore.zip)**: tải file này, upload thành Kaggle Dataset rồi Add Input vào notebook tool. Gói chứa các JSON từng ảnh, Content đã lưu, nguồn để mở lại và ghi chú kiểm tra.
- **[restore_in_kaggle.ipynb](restore_in_kaggle.ipynb)**: chứa cell khôi phục. Sao chép cell vào chính notebook đang chạy tool, trước cell mở web.
- [annotations.zip](annotations.zip): ba JSON theo dạng Download All, để lưu trữ/đối chiếu. Dùng gói khôi phục ở trên để nạp lại tool.

Các ảnh gốc vẫn ở [student_114](../student_114). Notebook Kaggle cần có Dataset ảnh và model như trước; gói khôi phục không chứa model hay ảnh gốc.

## Cách chạy

1. Tải `student_114_kaggle_restore.zip`, tạo Dataset riêng trên Kaggle và Add Input vào notebook tool.
2. Sao chép cell trong notebook khôi phục vào **cùng notebook tool**, sau các cell chuẩn bị dữ liệu và trước cell mở web. Chạy cell đó. Cell hỗ trợ cả ZIP còn nguyên hoặc Dataset đã được Kaggle giải nén.
3. Cell tạo hai biến cần giữ cho lệnh mở web:

```python
ANNOTATION_DIR = Path('/kaggle/working/annotations')
SOURCE_JSON = ANNOTATION_DIR / '_review/student_114_for_review.json'
```

4. Lệnh mở `gradio/app.py` phải dùng `--output-dir` và `--source-json` tương ứng với hai biến trên. Không gán lại SOURCE_JSON về JSON cũ sau cell khôi phục. IMAGE_DIR vẫn trỏ tới thư mục chín ảnh.
5. Mở web, chọn ảnh trong History và kiểm tra. Không bấm Run Detection để khôi phục box.

Nếu output đã có dữ liệu khác, cell sẽ dừng để không ghi đè. Chọn một thư mục output mới trong lời gọi khôi phục và dùng cùng đường dẫn cho app.

## Các giới hạn cần kiểm tra

Đây là **bản nháp để kiểm tra**, chưa xác nhận sẵn sàng nộp:

- **17077 và 46302** có cả nhãn dư lẫn thiếu. Tool gốc không hỗ trợ đồng thời hai loại nên gói native dùng Other. Other chỉ nạp box; toàn bộ nhãn, trạng thái, crop được giữ riêng trong `_review/review_details` và `_review/character_review`.
- **18592** có 145 box ghi chú nhỏ/vùng hỏng cần soi kỹ. Theo yêu cầu chỉ bỏ ngoặc ở Hán Nôm, 45 `[]` rỗng không được tự đổi thành `□` tại mục này, nên xuất thành 45 vị trí MISS. Đây là hệ quả của quy tắc chuẩn hóa đã chọn.
- Sáu ảnh mới cần kiểm tra lại trạng thái hư hại. Ghi chú đầy đủ và báo cáo kiểm tra nằm trong `_review/README.md`, `_review/summary.pdf`, `_review/validation.json` sau khi khôi phục.

Nguyên văn Hán Nôm chỉ bỏ ngoặc. Phiên âm Hán Việt đổi `[]` thành `□` rồi bỏ ngoặc, không tự thay chữ. Phần thuần Việt được sửa theo PDF. Các quy tắc và thay đổi được ghi trong gói.

Đã kiểm tra checksum gói, schema JSON, nạp lại cả chín ảnh bằng Workflow của tool gốc và giữ nguyên annotation người dùng. Cell khôi phục cũng đã thử với Dataset ZIP, Dataset đã giải nén và tình huống có dữ liệu mới hơn.

Sau khi làm thêm trên Kaggle, bấm **Save Annotation → Download All** và giữ ZIP mới bên ngoài session. Gói trong GitHub không tự cập nhật theo thao tác của bạn trên web.
