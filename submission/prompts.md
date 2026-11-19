# Dùng AI

| # | Ai dùng | Công cụ | Prompt (tóm tắt) | AI sai ở đâu | Nhóm kiểm lại thế nào |
|---|---|---|---|---|---|
| 1 | Người B (chờ bổ sung họ tên) | Codex | Đọc tài liệu trong folder và ảnh phân công, giải thích nhiệm vụ người B. | Chưa ghi nhận sai sót; phần dưới ảnh bị cắt nên chưa xác định được nhiệm vụ hỗ trợ thêm của B. | Đối chiếu GUIDE.md, RULES.md, docs/DELIVERY.md, CHECKPOINTS.md, RUBRIC.md và SUBMISSION.md với ảnh phân công. |
| 2 | Người B (chờ bổ sung họ tên) | Codex | Chạy download Pha 0; seed nhóm 24007; làm toàn bộ Pha 0; đánh dấu thông tin thành viên còn thiếu để nhóm bổ sung sau. | Chưa ghi nhận sai sót của AI; không tự điền danh tính hoặc MSHV còn thiếu. Tải dữ liệu bị timeout, nên Pha 0 chưa hoàn tất. | Xác nhận Python 3.13.9; kiểm log timeout, file tải dở và thay đổi Git. Chưa tạo delivery hoặc lineage cho seed 24007; cần kiểm hai phần này khi download thành công. |
