# Khôi phục nhãn với nguồn student_114.json gốc

Gói có **9 ảnh / 1.940 box**, gồm ba bài bạn cung cấp và bản nháp cho sáu ảnh còn lại.
`SOURCE_JSON` luôn trỏ tới **student_114.json gốc trong Input**. Không sửa hoặc tạo
bản thay thế của file nguồn. Các chỉnh sửa Content, kể cả Toát yếu bổ sung và
chữ đã xác minh ở 31962, được lưu trong `annotations/.state/content.json`.

## Dataset backup đã upload vẫn dùng được

Không cần upload lại nhãn. Dừng ô chạy web, rồi:

1. Mở [restore_in_kaggle.ipynb](restore_in_kaggle.ipynb), sao chép **hai cell code**
   để thay cell khôi phục và cell mở web cũ trong chính notebook đang chạy tool.
2. Chạy cell đó. Nó tự tìm `student_114.json` gốc trong Input và backup đã gắn,
   khôi phục vào `/kaggle/working/annotations`, rồi tạo `APP_LAUNCHER`.
   Hỗ trợ cả Dataset còn ZIP hoặc đã được Kaggle giải nén, kể cả ZIP con đã bung.
3. Cell mở web mới đã dùng APP_LAUNCHER. Nếu sửa thủ công cell cũ, thay:

   ```python
   str(REPO_PYTHON), '-u', str(REPO_DIR / 'gradio/app.py'),
   ```

   bằng:

   ```python
   str(REPO_PYTHON), '-u', str(APP_LAUNCHER),
   ```

4. Giữ các tham số sau trong command:

   ```python
   '--source-json', str(SOURCE_JSON.resolve()),
   '--output-dir', str(ANNOTATION_DIR.resolve()),
   ```

   SOURCE_JSON là đường dẫn tới `student_114.json` gốc trong Input; bỏ dòng gán
   nó sang bản nguồn phụ nếu còn trong notebook cũ. IMAGE_DIR vẫn trỏ tới ảnh gốc.
   Nếu REPO_DIR khác `/kaggle/working/SinoNom-Annotation`, đặt
   `environment['SINONOM_REPO_DIR'] = str(REPO_DIR.resolve())` trước subprocess.run.
5. Chạy riêng ô mở web, mở History và chọn ảnh. Không chạy detection để khôi phục.

[annotation-sinonom.ipynb](../annotation-sinonom.ipynb) đã hỗ trợ APP_LAUNCHER.
Nếu có nhiều bản student_114.json trong Input, truyền đường dẫn gốc rõ ràng vào
`find_original_source(source_json=...)`. Nếu output có nhãn khác hoặc chỉnh sửa
mới, bộ khôi phục dừng để giữ dữ liệu đó; không tự xóa/ghi đè.

## Content được lưu và đọc thế nào

- File nguồn: `student_114.json` gốc, dùng để khởi tạo dữ liệu.
- Content đã sửa: `/kaggle/working/annotations/.state/content.json`.
- JSON từng ảnh: trực tiếp trong annotations hoặc annotations/source_mismatches.
- Download All: xuất Content thành inscription_content.json trong ZIP tải về.

Tool gốc bỏ qua mục Content chưa có trong nguồn. Bộ nạp mới lấy các mục đã lưu,
như Toát yếu của 55431, 55432, 18592, vào **bản ghi trong bộ nhớ** khi mở ảnh.
Sau đó giao diện cho sửa và Save Annotation như các mục khác. Không ghi nguồn,
không sửa checkout của tool, không tạo hay chuyển nội dung Hán Nôm/Hán Việt mới.
Mục có giá trị null vẫn giữ nguyên null; không tự tạo văn bản cho mục đó.

File nguồn phụ từ gói cũ, nếu đã nằm trong output cũ, không được dùng làm nguồn.
Bản gói mới không chứa `student_114_for_review.json`.

## File tải lên khi bắt đầu lại

- [student_114_kaggle_restore.zip](student_114_kaggle_restore.zip): tạo Kaggle
  Dataset rồi Add Input vào notebook tool. Không chứa ảnh hoặc model.
- [restore_in_kaggle.ipynb](restore_in_kaggle.ipynb): cell mới tự chứa đầy đủ code.
- [restore_in_kaggle.py](restore_in_kaggle.py): cùng code, dùng nếu chạy bằng Python.
- [launch_with_original_source.py](launch_with_original_source.py): bộ nạp tương thích.
- [annotations.zip](annotations.zip): ba JSON theo dạng Download All, để sao lưu.

## Giới hạn và kiểm tra nội dung

Đây vẫn là **bản nháp để kiểm tra**, chưa xác nhận sẵn sàng nộp:

- **17077 và 46302:** có cả nhãn dư lẫn thiếu; tool chỉ cho một loại nên dùng Other.
  Native Other chỉ nạp box. Nhãn/trạng thái/crop đầy đủ ở `_review/review_details`.
- **18592:** 145 box nhỏ/vùng hỏng cần soi kỹ; 45 MISS là hệ quả của quy tắc chỉ bỏ
  ngoặc rỗng trong nguyên văn Hán Nôm đã thống nhất.
- Sáu ảnh mới cần kiểm tra lại trạng thái hư hại.

Nguyên văn Hán Nôm chỉ bỏ ngoặc, ngoại trừ lỗi Unicode đã xác minh ở **31962 #91:
足 → 是**. Phiên âm Hán Việt đổi `[]` thành `□` rồi bỏ ngoặc. Phần thuần Việt sửa
theo PDF. Không tìm thấy vị trí cần đổi sang `@` trong PDF và font đã kiểm tra;
xem [báo cáo](font_audit.json) và [ảnh đối chiếu](font_audit_evidence.png).

Sau khi sửa trên web: **Save Annotation → Download All**, giữ ZIP ngoài session.
Gói trên GitHub không tự cập nhật theo thao tác trên Kaggle.

Kiểm tra khôi phục ZIP/Dataset và giữ nhãn mới: `python kaggle_upload/test_restore.py`.
Kiểm tra nạp Content với nguồn gốc: chạy test_original_source.py bằng môi trường
đã cài requirements của tool, truyền SINONOM_REPO_DIR trỏ tới checkout tool.
