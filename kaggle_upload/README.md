# Dữ liệu để khôi phục trên Kaggle

Gói có đủ **9 ảnh / 1.940 box**, gồm ba bài bạn cung cấp (17390, 18591, 31962) và bản nháp cho sáu ảnh còn lại. Giữ nguyên box, trạng thái và crop bạn cung cấp; nhãn **31962 #91** được sửa theo PDF như mô tả dưới đây.

## Bản cập nhật sau khi rà lỗi font

- **31962, ô #91:** JSON trước ghi `足`, nhưng PDF Tập 4 trang 13 (trang in 526) và ảnh bia đều là `是` trong `是亦酬德報功`. Đã sửa đồng bộ Content, nhãn box, source_text, text_sequence và bản nguồn dùng để khôi phục.
- Không thay bằng `@` ở vị trí này vì đã xác định được Unicode đúng.
- Đã kiểm tra đủ bốn font CJK mà tool dùng: NomNaTong, DengXian, PMingLiU, PMingLiU-ExtB. Những chữ hiếm như `𦝧` có font dự phòng hỗ trợ nên giữ nguyên.
- Bảy trang phiên chép chứa chín mặt bia không có glyph dán bằng ảnh raster. Không tìm thấy vị trí cần bắt buộc đổi sang `@` trong PDF và font đã kiểm tra.
- Xem [báo cáo font](font_audit.json) và [ảnh đối chiếu](font_audit_evidence.png). Đây là kiểm tra PDF/font đi kèm tool, không phải kiểm tra việc tải font trong trình duyệt Kaggle của bạn.

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

### Nếu Kaggle báo thiếu `annotations/annotations.zip`

Kaggle có thể tự giải nén cả ZIP con thành thư mục `annotations/annotations`.
ZIP này chỉ là bản xuất để tải về; History đọc JSON từng ảnh. Bản đóng gói mới
không chứa ZIP con và bộ khôi phục mới cũng hỗ trợ Dataset cũ bị giải nén theo cách này.
Các JSON bắt buộc vẫn được kiểm tra đầy đủ bằng checksum; không bỏ qua file nhãn bị thiếu.

Nếu đã upload Dataset cũ, không cần upload lại. Chạy cell sau trước cell mở web
(đổi INPUT_DIR nếu Dataset của bạn nằm ở đường dẫn khác):

```python
from pathlib import Path
import json
import runpy
import shutil
import tempfile

INPUT_DIR = Path('/kaggle/input/datasets/nhn12312312412/backup')
restore = runpy.run_path(str(INPUT_DIR / 'restore_in_kaggle.py'))['restore_student_114']

with tempfile.TemporaryDirectory() as temporary:
    staged = Path(temporary) / 'backup'
    shutil.copytree(INPUT_DIR, staged)
    manifest_path = staged / 'student_114_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    # Chỉ bỏ yêu cầu về ZIP phụ trong bản sao tạm; giữ kiểm tra các JSON.
    manifest['files'].pop('annotations.zip', None)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding='utf-8')
    ANNOTATION_DIR = restore(
        input_root=staged,
        output='/kaggle/working/annotations_font_review',
    )

SOURCE_JSON = ANNOTATION_DIR / '_review/student_114_for_review.json'
```

Trong cell mở web, dùng cùng `ANNOTATION_DIR` và `SOURCE_JSON` ở trên.

Nếu đã khôi phục gói cũ, hãy dùng Dataset chứa ZIP mới và khôi phục sang thư mục mới, ví dụ:

```python
ANNOTATION_DIR = restore_student_114(output='/kaggle/working/annotations_font_review')
SOURCE_JSON = ANNOTATION_DIR / '_review/student_114_for_review.json'
```

Lệnh mở web phải giữ đúng ANNOTATION_DIR mới; bỏ lệnh gán lại về đường dẫn cũ nếu có. Không gắn đồng thời nhiều Dataset chứa các bản `student_114_kaggle_restore*.zip` vì cell sẽ không tự chọn thay bạn.

## Các giới hạn cần kiểm tra

Đây là **bản nháp để kiểm tra**, chưa xác nhận sẵn sàng nộp:

- **17077 và 46302** có cả nhãn dư lẫn thiếu. Tool gốc không hỗ trợ đồng thời hai loại nên gói native dùng Other. Other chỉ nạp box; toàn bộ nhãn, trạng thái, crop được giữ riêng trong `_review/review_details` và `_review/character_review`.
- **18592** có 145 box ghi chú nhỏ/vùng hỏng cần soi kỹ. Theo yêu cầu chỉ bỏ ngoặc ở Hán Nôm, 45 `[]` rỗng không được tự đổi thành `□` tại mục này, nên xuất thành 45 vị trí MISS. Đây là hệ quả của quy tắc chuẩn hóa đã chọn.
- Sáu ảnh mới cần kiểm tra lại trạng thái hư hại. Ghi chú đầy đủ và báo cáo kiểm tra nằm trong `_review/README.md`, `_review/summary.pdf`, `_review/validation.json` sau khi khôi phục.

Nguyên văn Hán Nôm chỉ bỏ ngoặc, ngoại trừ lỗi font/Unicode được xác minh theo yêu cầu rà soát mới nhất. Phiên âm Hán Việt đổi `[]` thành `□` rồi bỏ ngoặc, không tự thay chữ. Phần thuần Việt được sửa theo PDF. Các quy tắc và thay đổi được ghi trong gói.

Đã kiểm tra checksum gói, schema JSON, nạp lại cả chín ảnh bằng Workflow của tool gốc, giữ nguyên hình học/trạng thái/crop và chỉ sửa nhãn Unicode nêu trên. Cell khôi phục cũng đã thử với Dataset ZIP, Dataset đã giải nén và tình huống có dữ liệu mới hơn.

Sau khi làm thêm trên Kaggle, bấm **Save Annotation → Download All** và giữ ZIP mới bên ngoài session. Gói trong GitHub không tự cập nhật theo thao tác của bạn trên web.
