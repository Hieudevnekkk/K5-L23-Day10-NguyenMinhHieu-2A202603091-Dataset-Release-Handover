# Nhóm 24

- Seed luyện tập: **24007**. Đề ẩn: **đề 20**.
- Repo: https://github.com/Hieudevnekkk/K5-L23-Day10-NguyenMinhHieu-2A202603091-Dataset-Release-Handover
- **Đại diện trả lời vấn đáp chung: Nguyễn Hoàn Thiện.** Mỗi thành viên vẫn giải thích được phần mình làm.

## Phân công

Mỗi người một phần chính và một phần hỗ trợ, để khối lượng đều nhau.

| Người | Thành viên | MSHV | Phần chính | Phần hỗ trợ | Sản phẩm |
|---|---|---|---|---|---|
| A | Nguyễn Hoàn Thiện | 2A202603123 | Pha 1: khung `validate.py`, giao diện dòng lệnh; `missing_image`, `wrong_hash`, `invalid_class`, `bbox_out_of_bounds`, `duplicate_box` | Đề ẩn: chốt `review_log.csv`, `errors.json`; Pha 5: `trace.json`; `prompts.md` | Phần đầu `validator/validate.py`; `submission/de_an/`; `trace.json` |
| B | Dương Quang Chung | (bổ sung) | Pha 1: `scene_leak`, `guideline_mismatch`, `invalid_category_id`, `thing_overlap` (đếm pixel mask qua `pngutil.py`); kiểm thử trên ≥ 2 seed và lô sạch; ghép code với A | Pha 6: `security.md` (ca USB, năm việc được/không, ca khuôn mặt) | Phần sau `validator/validate.py`; `security.md` |
| C | Phạm Tiến Dũng | 2A202603061 | Pha 2: ghép box với segment bằng pixel mask, sinh `candidates.json`; đo ứng viên trên lô sạch, chọn ngưỡng | Số liệu và câu hỏi Pha 2 trong `REPORT.md` (ứng viên lô sạch, vì sao báo hết làm F1 giảm) | `validator/crosscheck.py`; `candidates.json`; mục Pha 2 của `REPORT.md` |
| D | Nguyễn Minh Hiếu | 2A202603091 | Công cụ xem ảnh (vẽ box, viền segment); chia hàng đợi review; `merge_review.py` ra `errors.json` | Review seed luyện tập: `submission/r24007/review_log.csv` | `tools/viewer.py`; `review_log.csv`, `errors.json` của seed |
| E | Vi Thanh Đức | 2A202603051 | Pha 3–4: quyết định HOLD, `lineage.py` (HOLD v1, release v2 có parent); dựng lô v2, `pack_release.py`, `check_handover.py` | `TEAM.md`, phần bàn giao và lineage trong `REPORT.md`; `export_submission.py` | `handover/`; `lineage.jsonl`; `README.txt` của v2 |

## Phối hợp

- Cả nhóm cùng xem ảnh ở Pha 2; mỗi dòng `confirmed`/`rejected` ghi rõ người xem.
- Mỗi thành viên có ít nhất 2 commit có nội dung bằng tên và email của mình.
- Validator chỉ đọc delivery được truyền vào, dùng thư viện chuẩn; được import `scripts/pngutil.py`. Không sửa delivery v1 hoặc `scripts/` của đề.
- Không commit `data_source/`, `runs/`, file `.zip` hay `delivery/` của đề ẩn; xuất bài làm sang `submission/` ở bước nộp.

## Lệnh chuẩn bị

Chạy từ thư mục gốc repo (PowerShell, Python 3.10+):

```powershell
py -X utf8 scripts/download_public.py
py -X utf8 scripts/run_lab.py --seeds 24007
```

Seed phụ để thử validator dùng `inject_release.py`, không chạy lại `run_lab.py` để thêm seed.
