# theobuocbut-media

Ảnh, video và bài Threads công khai của Theo Bước Bụt. CI trong repo budda-social lấy file ở đây để đăng lên Threads.

| Thư mục | Chứa gì |
|---|---|
| `video/<tên short>.mp4` | video short (720p, ≤ 8 MB) đăng Threads lúc 20:00 |
| `anh/<tên bài>.jpg` | ảnh đi kèm bài đăng buổi sáng |
| `threads/<tên bài>.txt` | BẢN CŨ (09/11), không còn dùng: bài 07:00 giờ là carousel lấy chữ từ `bai-hoc/<bài>/p<i>.txt` + ảnh `p<i>-*.jpg` (dựng bằng `tools/make_carousels.py` từ bài mới nhất budda-app origin/main). Chỉ bài không chia phần (bai-01..07, đã đăng/bỏ) mới đọc file này |

Tên file trùng tên thư mục trong `budda-social/posts/` và `budda-social/shorts/`. Không để link trong bài (chờ có app Android).

## Kho trên máy là bản gọn, không giữ mp4 (CD 15/11)

Bản clone trên máy dùng `git clone --filter=blob:none` + sparse-checkout (`/*` và `!*.mp4`): mọi file chữ, json, ảnh đều có, còn video mp4 chỉ nằm trên GitHub (CI vẫn lấy đủ).
- Thêm video mới: chép mp4 vào đúng chỗ (shorts/<tên>/video.mp4, longs/<tên>/video.mp4, hoặc video/<tên>.mp4 ở theobuocbut-media), rồi chạy `py scripts/day_video.py "lời commit" <đường dẫn>` (theobuocbut-media: `py tools/day_video.py ...`). Đừng `git add`/commit video ở kho này. Script đẩy từ một bản clone tạm (không tải video), push thường, xoá bản tạm và bản mp4 trên máy, rồi `git pull` (không tải video về). Nhờ vậy .git không phình ra (17/11: commit tại chỗ làm .git lên 4,7 GB).
- Cần một video về máy: `git show HEAD:shorts/<tên>/video.mp4 > ten.mp4`. Lấy lại đủ cả kho: `git sparse-checkout disable`.
- Đừng chạy lệnh đọc kích thước từng file trên GitHub kiểu `git ls-tree -l` (nó tải hết video về). Nếu .git đã lỡ phình to: clone lại bản gọn (`git clone --filter=blob:none --no-checkout`, sparse-checkout `/*` và `!*.mp4`), so khớp file không phải mp4, rồi thay thư mục cũ.
