# theobuocbut-media

Ảnh, video và bài Threads công khai của Theo Bước Bụt. CI trong repo budda-social lấy file ở đây để đăng lên Threads.

| Thư mục | Chứa gì |
|---|---|
| `video/<tên short>.mp4` | video short (720p, ≤ 8 MB) đăng Threads lúc 20:00 |
| `anh/<tên bài>.jpg` | ảnh đi kèm bài đăng buổi sáng |
| `threads/<tên bài>.txt` | chữ của bài Threads 07:00 (chuyện mở đầu + câu hỏi). Sửa file này là bài đăng đổi theo |

Tên file trùng tên thư mục trong `budda-social/posts/` và `budda-social/shorts/`. Không để link trong bài (chờ có app Android).

## Kho trên máy là bản gọn, không giữ mp4 (CD 15/11)

Bản clone trên máy dùng `git clone --filter=blob:none` + sparse-checkout (`/*` và `!*.mp4`): mọi file chữ, json, ảnh đều có, còn video mp4 chỉ nằm trên GitHub (CI vẫn lấy đủ).
- Thêm video mới: chép mp4 vào đúng chỗ (shorts/<tên>/video.mp4, longs/<tên>/video.mp4, hoặc video/<tên>.mp4 ở theobuocbut-media), rồi chạy `py scripts/day_video.py "lời commit" <đường dẫn>` (theobuocbut-media: `py tools/day_video.py ...`). Script dùng `git add --sparse`, commit, push thường, rồi `git sparse-checkout reapply` để mp4 rời khỏi ổ đĩa.
- Cần một video về máy: `git show HEAD:shorts/<tên>/video.mp4 > ten.mp4`. Lấy lại đủ cả kho: `git sparse-checkout disable`.
- Mỗi tháng chạy `git repack -a -d --filter=blob:none` để bỏ blob video đã tải về khỏi .git.
