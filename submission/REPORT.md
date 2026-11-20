# Báo cáo nhóm 24

## 1. Số liệu luyện tập
- F1 theo seed (rule / cross_check / overall): **24007: 1.0 / 0.6 / 0.8** (`score_findings.py`, sau khi xem ảnh 8 ứng viên và chốt `errors.json`: 11 lỗi luật + 7 lỗi gán nhãn đã xác nhận). Chỉ đo một seed luyện tập, kết quả làm tròn.
- Số ứng viên trên lô sạch (`--no-faults`, 50 ảnh): **1** (2%); lỗi luật trên lô sạch: 0. Chi tiết ứng viên này xem `review_log.csv` (dòng `000000060932`, `rejected`). Hàng đợi trên seed luyện tập: **8 ảnh** (7 `confirmed`, 1 `rejected`). Hàng đợi đề ẩn: 11 ảnh (9 `confirmed`, 2 `rejected`).
- Ngưỡng đã chọn và cách chọn (không dùng `_private`): ghép box với segment bằng IoU giữa box và bbox sát của segment đo từ mask, ngưỡng ghép 0,15; `bbox_drift` khi IoU < 0,6 hoặc dưới 88% pixel của segment nằm trong box; `instance_merge` khi pixel segment được chia ra các box cùng lớp (tổng từ 0,6 đến 1,25) và không box nào chứa trọn segment; `missing_box` khi segment thing chiếm từ 1% ảnh mà không box nào còn trống che nó. Cách chọn: đo nhiễu trên lô sạch (cần ít ứng viên, đạt 1/50 ảnh) và trên phân bố IoU của 1718 cặp box–segment cùng lớp trong đề ẩn (1134 cặp có IoU xấp xỉ 1,0, chỉ khoảng 5 cặp dưới 0,7). Không dùng `_private`.

## 2. Vì sao báo hết ứng viên làm F1 giảm?
Vì F1 trừ báo thừa như bỏ sót: mỗi ứng viên không phải lỗi thật là một dương tính giả, làm precision giảm. Số của nhóm trên đề ẩn: lần ghép đầu (pixel IoU thô, chưa kiểm vật mảnh và vật che nhau) cho **461 ứng viên** trên 138 ảnh, trong khi chỉ có 9 lỗi gán nhãn thật sau khi xem ảnh. Nếu báo hết thì precision ≈ 9/461 ≈ 2%, recall 100%, F1 phần gán nhãn ≈ **0,04**. Sau khi ghép bằng IoU bbox sát của segment cùng điều kiện pixel còn **11 ứng viên**, 9 thật (precision ≈ 82%), và nhờ xem ảnh bỏ thêm 2 ca lệch tự nhiên (`img_0207` người bị che, `img_0003` ghế dài bị che) nên không báo thừa. Cũng vì vậy hàng đợi nhỏ đủ để cả nhóm xem hết từng ảnh. Báo hết ứng viên mà không xem ảnh còn không phân biệt được `class_swap` với `category_swap`.

## 3. Quyết định và lineage
**QC v1 = 18/250 = 7,2%** (số mục trong `errors.json` chia tổng ảnh; mỗi ảnh mang nhiều nhất một lỗi, `scene_leak` của `scene_423` tính một mục). Vượt ngưỡng 2% của Day 7 nên **không Release v1**: lineage ghi `decision HOLD` cho `lab250_c5c3f115cc1b`.

Ngưỡng tính theo **tỉ lệ ảnh lỗi** chứ không theo số lỗi, vì 18 lỗi nghĩa khác nhau trên lô 250 ảnh và trên lô 25.000 ảnh; tỉ lệ so sánh được giữa các lô.

`lineage.py impact` cho **`R-021: affected=True action=review_or_retrain`**. Run R-021 đã train trực tiếp trên v1. Đổi dataset (phát hành v2) không sửa được trọng số của model đã học: model vẫn mang những gì nó học từ 18 ảnh lỗi của v1, và có thể cả lỗi chưa ai bắt. Vì vậy R-021 phải được xem lại kết quả (đặc biệt ở các lớp bị ảnh hưởng, ví dụ `truck` theo ticket) hoặc train lại trên v2 sau khi rework xong.

**Lô v2** (`lab250_c5c3f115cc1b_v2`, parent là v1, lineage có sự kiện `release` kèm `parent`): 240 ảnh, 1663 nhãn. v1 giữ nguyên (H1 PASS). Phân loại 18 lỗi theo GUIDE Pha 4:
- **Sửa ngay trong v2** (4 ảnh/cảnh): `wrong_hash` 2 ảnh (đã mở ảnh kiểm, còn nguyên, ghi hash mới), `guideline_mismatch` 1 ảnh (`000000023126`, truyvet.csv lấy theo job J09 là v1.3), `scene_leak` 1 cảnh (`scene_423`: `000000017207` từ val về train).
- **Vào `rework_queue.csv`, rời v2** (10 ảnh): `missing_box` 3, `invalid_class` 2, `bbox_out_of_bounds` 2, `class_swap` 2, `duplicate_box` 1. Giao lại đúng người theo `jobs.csv`: A04 (5 ảnh, kiểm Q01), A02 (4 ảnh, kiểm Q01/Q02/Q03), A05 (1 ảnh, kiểm Q03).
- **Ở lại v2, báo team panoptic** (4 ảnh): `invalid_category_id`, `thing_overlap`, `category_swap`, `instance_merge`. Nhãn detection của các ảnh này vẫn đúng, vì v2 là sản phẩm detection.

Kết luận v2 là Release cho nhãn detection, kèm cảnh báo: PASS của `check_handover.py` chỉ nói lô đúng định dạng và nhất quán, không nói nhãn đúng; lỗi mà validator chưa bắt (F1 lỗi gán nhãn của nhóm khoảng 0,6) vẫn có thể còn trong v2.

## 4. Hash chứng minh gì, không chứng minh gì?
**Chứng minh được:**
- Nội dung (từng byte) của file lúc này đúng bằng nội dung lúc ghi hash. `check_handover.py` H1 tính lại sha256 nhãn và mask của v1 so với `manifest.json`, và `release_id` của v1 được tính từ `manifest.json` cộng `metadata.json`, nên sửa v1 thì `release_id` đổi: v1 không bị ghi đè.
- Trong v2, `manifest.csv` có 480 file (images và labels) với sha256 tính trên file thật (H8); nhãn của v2 trùng hash với nhãn v1 (H7), tức không ai sửa tay nhãn.
- Gói v2 tái lập được: đóng gói lại ra đúng `ed8092632792b8c886781976e101b130392f9e1cd2382511fd8f1de235ebc8f9` ghi trong `lab250_c5c3f115cc1b_v2.sha256` (H15).

**Không chứng minh được:**
- **Nhãn đúng hay sai.** Một nhãn sai vẫn có hash hợp lệ. 7 lỗi gán nhãn của seed 24007 đều có hash khớp; chỉ mắt người xem ảnh mới bắt được.
- **Hash lệch không có nghĩa là ảnh hỏng.** Hai ảnh `wrong_hash` (`000000002685`, `000000009769`) mở được và đúng nội dung; lỗi nằm ở hash ghi trong manifest. Vì vậy phải mở ảnh kiểm trước khi quyết định đưa vào rework hay chỉ ghi hash mới.
- **Ai đổi và vì sao.** Nếu cả file lẫn dòng hash cùng bị sửa thì hash vẫn khớp; hash chỉ có giá trị khi bản ghi hash được giữ ở nơi khác (ở đây là lineage và `.sha256`).
- **Ảnh có phải bản gốc hay không**, và v2 có đủ ảnh cần thiết không: hash chỉ nói về những file đã có trong danh sách.

## 5. Truy vết
Ticket của team AI nói model bỏ sót `truck` bị che hoặc ở mép ảnh ở `scene_434` và `scene_575`; changelog nói v1.3 đổi quy tắc đúng lớp `truck` (vật bị che trên 50% hoặc cắt ở mép ảnh vẫn phải gán box). Tầng a: ảnh thuộc hai cảnh được nêu, thuộc job theo guideline v1.2 và có ít nhất một box detection lớp `truck` trong `labels/`. Tầng b: ảnh khác cùng điều kiện (job v1.2, có `truck`) mà chưa ai báo. `notify`: người gán và người kiểm của các job chứa ảnh tầng a và b. Lấy guideline theo **job** trong `jobs.csv`, không theo trường ghi ở từng ảnh, vì trường đó có thể chính là lỗi `guideline_mismatch` (seed 24007 có một ảnh như vậy), nên không dùng nó làm căn cứ truy vết. Kết quả seed luyện tập: tier_a 2 ảnh, tier_b 5 ảnh, notify A02, A04, A05, Q01 (truy vết F1 ≈ 1.0 theo `score_findings.py`).

## 6. Bug hoặc điểm chưa rõ trong lab (nếu có)
- F1 lỗi gán nhãn của seed luyện tập chỉ khoảng 0,6 dù 7 ca ta báo đều qua mắt người xem ảnh, nên chủ yếu là **recall**: còn lỗi gán nhãn mà ngưỡng ghép chưa bắt. Nhóm không dò từng ảnh bằng `score_findings.py` (RULES) nên chưa biết loại nào bị bỏ sót; giả thuyết chưa kiểm chứng là các `bbox_drift` nhỏ (lệch ít, IoU trên 0,6) vì ứng viên của seed này không có ca `bbox_drift` nào.
- Đề ẩn: `review_log.csv` hiện có thêm vài dòng `bbox_drift` `rejected` (ảnh `img_0041`, `img_0137`, `img_0154`, `img_0178`) không nằm trong `candidates.json` hiện tại, do review từ một bản ứng viên cũ; vô hại vì dòng `rejected` không vào `errors.json`.
- `scripts/pack_release.py` không tái lập được giữa các hệ điều hành dù docstring nói "trên mọi máy": nó sắp xếp file bằng `sorted()` trên đối tượng `Path`, nên trên Linux `README.txt` (chữ hoa) đứng trước `label_summary.csv`, còn trên Windows (so sánh không phân biệt hoa thường) đứng sau `manifest.csv`. Cùng 485 file nhưng thứ tự trong zip khác nên sha256 khác: mã tạo trên Linux (`d04803ac…`) làm `check_handover.py` H15 FAIL trên Windows. Nhóm không sửa script (RULES); đóng gói lại trên Windows ra `ed809263…` thì H15 PASS. Mã `.sha256` nộp vì vậy gắn với Windows; nếu người chấm chạy trên Linux hoặc macOS thì H15 có thể lệch. Cần báo giảng viên theo RULES (chưa báo).
- `check_handover.py` đọc `errors.json`, `review_log.csv`, `trace.json`, `security.md` từ `runs/r<seed>/`, trong khi bài nộp nằm ở `submission/`; `export_submission.py --run` chép theo chiều `runs/` sang `submission/` và ghi đè. Sửa file ở `submission/` mà quên chép ngược về `runs/` thì bộ kiểm vẫn chạy trên bản cũ, và chạy export sau đó sẽ làm mất bản sửa.
