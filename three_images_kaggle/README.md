# Dữ liệu 55431, 46303, 46302 cho Kaggle

Tải `three_images_kaggle.zip`, tạo Kaggle Dataset từ ZIP rồi **Add Input** vào
notebook đang có app, model và ảnh gốc. Dataset mới này chứa dữ liệu box/nhãn
đã chuẩn bị; notebook phải đọc nó trước khi mở web.

1. Chạy các ô cài app/model và khai báo đường dẫn như trước.
2. Thay ô restore bốn bài cũ bằng nội dung `kaggle_cell.py`.
3. Chờ dòng `Dữ liệu cho web: /kaggle/working/annotations`.
4. Chạy ô mở web đang dùng `APP_LAUNCHER` để xem ba ảnh.

Nếu còn bài làm dở chưa lưu trên web, giữ phiên đó để lưu trước khi dừng ô web.
Không chạy lại ô restore cũ sau ô mới này.

## Dữ liệu trong gói

| Ảnh | Box thủ công | Đối chiếu nội dung |
| --- | ---: | --- |
| 55431.png | 197 | MISS #131: trên ảnh có 祭, nguồn không có |
| 46303.png | 212 | Excluded: 〇 |
| 46302.png | 421 | MISS #35: trên ảnh có 蓋; Excluded: 〇 và chú thích 1 |

`data/*.json` chứa tọa độ, thứ tự và nhãn chữ. Đây là đầu vào để tạo JSON
native của app, chưa phải kết quả model đã chạy. Các box đã được rà ảnh và
chỉnh thủ công; một số vùng mờ của 46303/46302 vẫn cần kiểm tra trên web.

`three_images_helper.py` chạy **model damage của app** bằng `REPO_PYTHON`, giữ
nguyên 830 box và thứ tự chữ, chỉ áp dụng kết quả Intact/Damaged theo luật
overlap của app. Không chạy lại OCR/detect box. Chữ □ được giữ Unknown/Damaged.
Model nhị phân không tự phân mức hỏng 1/2/3; các box Damaged khác cần chọn mức
trên web trước khi Save Annotation. Chưa có inference thật trong môi trường
soạn gói này; các kiểm thử tự động dùng kết quả inference giả lập.

`existing_user_annotations/` chứa bốn bài gốc gần nhất người dùng đã gửi:
17390, 18591, 31962, 55432. Chúng chỉ được chép khi output chưa có bài tương
ứng. Nội dung native bốn bài không bị sửa. Bài mới hơn trong output được giữ.

`inscription_content.json` chứa Content cho bảy ảnh. Các cặp `[]` rỗng thành
□, các dấu ngoặc được bỏ nhưng giữ chữ bên trong, □ sẵn có được giữ.
Không sửa `student_114.json` gốc. Content đã lưu trong output được ưu tiên.

46302 vừa thiếu vừa dư nội dung; schema Other của app chỉ lưu tọa độ. Vì vậy
gói tạo thêm `model_reviews/46302.json` và launcher tương thích để lưu/nạp
đủ nhãn, trạng thái và thứ tự, đồng thời cho phép xem bước Status & Order.
Khi đưa output sang phiên khác, giữ cả file kèm và `_support/`.

## Lưu để dùng lại

Ô mới tạo `/kaggle/working/my_annotations_backup.zip`; launcher cập nhật ZIP
này mỗi lần **Save Annotation** thành công. Tải ZIP này về để giữ cả bảy bài,
nhãn kèm và Content. Có thể tạo lại thủ công:

```python
backup_my_work(ANNOTATION_DIR)
```

Để phục hồi ZIP backup trong phiên mới, tạo Dataset từ ZIP và Add Input, rồi
dùng `user_work_manifest.json` và `restore_my_work.py` ở gốc Dataset:

```python
from pathlib import Path
import os, runpy

items = list(Path('/kaggle/input').rglob('user_work_manifest.json'))
if len(items) != 1:
    raise RuntimeError('Gắn đúng một Dataset backup muốn phục hồi.')
root = items[0].parent
saved = runpy.run_path(str(root / 'restore_my_work.py'))
ANNOTATION_DIR = saved['restore_my_work'](root)
APP_LAUNCHER = ANNOTATION_DIR / '_support/launch_with_original_source.py'
backup_my_work = saved['backup_my_work']
os.environ['SINONOM_REPO_DIR'] = str(Path(REPO_DIR).resolve())
```

Tiếp tục dùng `SOURCE_JSON` gốc và ô mở web dùng `APP_LAUNCHER`.
Kaggle `/working` có thể mất khi kết thúc session; cần tải ZIP hoặc lưu output
phiên đang có bài đã lưu. Save & Run All không tái hiện thao tác dán nhãn tay.

Kiểm thử bằng Workflow của upstream SinoNom-Annotation commit
`6d32727fd8bf1ba28af2107cefc6063835167e0e`.
