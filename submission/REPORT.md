# Báo cáo nhóm 24

## 1. Số liệu luyện tập
- F1 theo seed (rule / cross_check / overall): **24007: 1.0 / 0.6 / 0.8** (`score_findings.py`, sau khi xem ảnh 8 ứng viên và chốt `errors.json`: 11 lỗi luật + 7 lỗi gán nhãn đã xác nhận). Chỉ đo một seed luyện tập, kết quả làm tròn.
- Số ứng viên trên lô sạch (`--no-faults`, 50 ảnh): **1** (2%); lỗi luật trên lô sạch: 0. Chi tiết ứng viên này xem `review_log.csv` (dòng `000000060932`, `rejected`). Hàng đợi trên seed luyện tập: **8 ảnh** (7 `confirmed`, 1 `rejected`). Hàng đợi đề ẩn: 11 ảnh (9 `confirmed`, 2 `rejected`).
- Ngưỡng đã chọn và cách chọn (không dùng `_private`): ghép box với segment bằng IoU giữa box và bbox sát của segment đo từ mask, ngưỡng ghép 0,15; `bbox_drift` khi IoU < 0,6 hoặc dưới 88% pixel của segment nằm trong box; `instance_merge` khi pixel segment được chia ra các box cùng lớp (tổng từ 0,6 đến 1,25) và không box nào chứa trọn segment; `missing_box` khi segment thing chiếm từ 1% ảnh mà không box nào còn trống che nó. Cách chọn: đo nhiễu trên lô sạch (cần ít ứng viên, đạt 1/50 ảnh) và trên phân bố IoU của 1718 cặp box–segment cùng lớp trong đề ẩn (1134 cặp có IoU xấp xỉ 1,0, chỉ khoảng 5 cặp dưới 0,7). Không dùng `_private`.

## 2. Vì sao báo hết ứng viên làm F1 giảm?
Vì F1 trừ báo thừa như bỏ sót: mỗi ứng viên không phải lỗi thật là một dương tính giả, làm precision giảm. Số của nhóm trên đề ẩn: lần ghép đầu (pixel IoU thô, chưa kiểm vật mảnh và vật che nhau) cho **461 ứng viên** trên 138 ảnh, trong khi chỉ có 9 lỗi gán nhãn thật sau khi xem ảnh. Nếu báo hết thì precision ≈ 9/461 ≈ 2%, recall 100%, F1 phần gán nhãn ≈ **0,04**. Sau khi ghép bằng IoU bbox sát của segment cùng điều kiện pixel còn **11 ứng viên**, 9 thật (precision ≈ 82%), và nhờ xem ảnh bỏ thêm 2 ca lệch tự nhiên (`img_0207` người bị che, `img_0003` ghế dài bị che) nên không báo thừa. Cũng vì vậy hàng đợi nhỏ đủ để cả nhóm xem hết từng ảnh. Báo hết ứng viên mà không xem ảnh còn không phân biệt được `class_swap` với `category_swap`.

## 3. Quyết định và lineage
<<QC v1 a/b, kết luận, vì sao R-021 phải xem lại hoặc train lại.>>

## 4. Hash chứng minh gì, không chứng minh gì?
<<>>

## 5. Truy vết
Ticket của team AI nói model bỏ sót `truck` bị che hoặc ở mép ảnh ở `scene_434` và `scene_575`; changelog nói v1.3 đổi quy tắc đúng lớp `truck` (vật bị che trên 50% hoặc cắt ở mép ảnh vẫn phải gán box). Tầng a: ảnh thuộc hai cảnh được nêu, thuộc job theo guideline v1.2 và có ít nhất một box detection lớp `truck` trong `labels/`. Tầng b: ảnh khác cùng điều kiện (job v1.2, có `truck`) mà chưa ai báo. `notify`: người gán và người kiểm của các job chứa ảnh tầng a và b. Lấy guideline theo **job** trong `jobs.csv`, không theo trường ghi ở từng ảnh, vì trường đó có thể chính là lỗi `guideline_mismatch` (seed 24007 có một ảnh như vậy), nên không dùng nó làm căn cứ truy vết. Kết quả seed luyện tập: tier_a 2 ảnh, tier_b 5 ảnh, notify A02, A04, A05, Q01 (truy vết F1 ≈ 1.0 theo `score_findings.py`).

## 6. Bug hoặc điểm chưa rõ trong lab (nếu có)
- F1 lỗi gán nhãn của seed luyện tập chỉ khoảng 0,6 dù 7 ca ta báo đều qua mắt người xem ảnh, nên chủ yếu là **recall**: còn lỗi gán nhãn mà ngưỡng ghép chưa bắt. Nhóm không dò từng ảnh bằng `score_findings.py` (RULES) nên chưa biết loại nào bị bỏ sót; giả thuyết chưa kiểm chứng là các `bbox_drift` nhỏ (lệch ít, IoU trên 0,6) vì ứng viên của seed này không có ca `bbox_drift` nào.
- Đề ẩn: `review_log.csv` hiện có thêm vài dòng `bbox_drift` `rejected` (ảnh `img_0041`, `img_0137`, `img_0154`, `img_0178`) không nằm trong `candidates.json` hiện tại, do review từ một bản ứng viên cũ; vô hại vì dòng `rejected` không vào `errors.json`.
- Phần 3 và 4 (quyết định, lineage, hash) do người phụ trách bàn giao điền sau khi dựng lô v2.
