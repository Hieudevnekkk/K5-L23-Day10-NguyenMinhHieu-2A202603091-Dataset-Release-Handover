Release: lab250_c5c3f115cc1b_v2
Parent: lab250_c5c3f115cc1b
Số ảnh: 240
Số nhãn: 1663
Guideline: v1.2 (J01, J02, J03, J04), v1.3 (J05, J06, J07, J08, J09, J10)
QC v1: 18/250 = 7.2%
Kết luận v1: Hold — 18/250 ảnh/cảnh lỗi (7.2%) vượt ngưỡng 2%, không Release v1; R-021 train trên v1 phải xem lại hoặc train lại.
Kết luận v2: Release (chỉ sản phẩm detection) — đã tách 10 ảnh lỗi nhãn detection sang rework_queue (bbox_out_of_bounds 2, class_swap 2, duplicate_box 1, invalid_class 2, missing_box 3), sửa hash, guideline, split; còn 4 ảnh lỗi panoptic ở lại v2 và báo team panoptic. Lỗi chưa bị bắt (nếu có) vẫn có thể còn trong v2.
Ghi chú: 10 ảnh trong rework_queue.csv giao lại đúng người gán/kiểm theo jobs.csv; v2 giữ nguyên ảnh và nhãn của v1, không sửa tay nhãn nào.
- wrong_hash (2 ảnh: 000000002685, 000000009769): đã mở ảnh kiểm, ảnh mở được và đúng nội dung, chỉ hash trong manifest v1 sai; ảnh ở lại v2, manifest.csv ghi hash tính lại trên file thật.
- guideline_mismatch: 000000023126 (metadata ghi v1.2, job J09 dùng v1.3); truyvet.csv lấy guideline theo job.
- scene_leak: scene_423: 000000017207 val->train; đưa cả cảnh về một split trong truyvet.csv.
- Rework giao lại: 000000000872 -> gán A04, kiểm Q01; 000000001761 -> gán A04, kiểm Q01; 000000001818 -> gán A04, kiểm Q01; 000000008762 -> gán A02, kiểm Q01; 000000011760 -> gán A04, kiểm Q01; 000000012748 -> gán A04, kiểm Q01; 000000013348 -> gán A05, kiểm Q03; 000000017959 -> gán A02, kiểm Q03; 000000022192 -> gán A02, kiểm Q02; 000000023034 -> gán A02, kiểm Q02.
- Báo team panoptic (ảnh ở lại v2, nhãn detection vẫn đúng): 000000014038 (invalid_category_id), 000000016249 (thing_overlap), 000000017178 (instance_merge), 000000017379 (category_swap).
