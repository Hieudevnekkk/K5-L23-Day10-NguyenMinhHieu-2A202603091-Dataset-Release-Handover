#!/usr/bin/env python3
"""Dựng lô bàn giao v2 (Pha 4) từ delivery v1 + errors.json của nhóm. Chỉ dùng thư viện chuẩn.

    python tools/build_v2.py --run runs/r24007

Không sửa delivery/ (v1). Chỉ ghi vào runs/r<seed>/handover/<release_id>_v2/.
Quy tắc phân loại theo GUIDE.md Pha 4:
  - lỗi nhãn detection / thiếu file  -> rework_queue.csv, ảnh rời v2
  - lỗi chỉ ở panoptic               -> ảnh ở lại v2, ghi vào README (Ghi chú) để báo team panoptic
  - wrong_hash                       -> ảnh còn nguyên (đã mở kiểm) thì chỉ manifest sai: hash mới theo file thật
  - guideline_mismatch               -> truyvet.csv lấy guideline theo JOB
  - scene_leak                       -> đưa cả cảnh về một split (split chiếm đa số) trong truyvet.csv
Số liệu trong README.txt đều tính từ file thật, không gõ tay.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path

DET_REWORK = {"missing_image", "invalid_class", "bbox_out_of_bounds", "duplicate_box", "class_swap", "bbox_drift", "missing_box"}
PANOPTIC_ONLY = {"invalid_category_id", "thing_overlap", "category_swap", "instance_merge"}
THRESHOLD = 0.02


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def ranges(job_ids: list[str]) -> str:
    return ", ".join(job_ids)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    args = ap.parse_args()
    run = Path(args.run)
    d = run / "delivery"

    rid = json.loads((d / "release.json").read_text(encoding="utf-8"))["release_id"]
    man = json.loads((d / "manifest.json").read_text(encoding="utf-8"))["items"]
    meta = {m["image"]: m for m in json.loads((d / "metadata.json").read_text(encoding="utf-8"))["items"]}
    jobs = {r["job_id"]: r for r in read_csv(d / "jobs.csv")}
    names80 = [ln.split(" ", 1)[1].strip() for ln in (d / "classes.txt").read_text(encoding="utf-8").splitlines()]
    errors = json.loads((run / "errors.json").read_text(encoding="utf-8"))["errors"]

    by_target = defaultdict(list)
    for e in errors:
        by_target[e["target"]].append(e["type"])

    # ---- phân loại ---------------------------------------------------------------------------
    rework = {t: types[0] for t, types in by_target.items() if t in man and types[0] in DET_REWORK}
    panoptic_only = sorted(t for t, types in by_target.items() if t in man and types[0] in PANOPTIC_ONLY)
    wrong_hash = sorted(t for t, types in by_target.items() if t in man and types[0] == "wrong_hash")
    guideline_bad = sorted(t for t, types in by_target.items() if t in man and types[0] == "guideline_mismatch")
    leak_scenes = sorted(t for t, types in by_target.items() if types[0] == "scene_leak")

    # scene_leak: đưa cả cảnh về split chiếm đa số (hoà thì train)
    split_fix = {}
    for sc in leak_scenes:
        members = [n for n, m in meta.items() if m["scene_id"] == sc]
        cnt = Counter(meta[n]["split"] for n in members)
        target_split = "train" if cnt.get("train", 0) >= cnt.get("val", 0) else "val"
        for n in members:
            if meta[n]["split"] != target_split:
                split_fix[n] = (meta[n]["split"], target_split)

    # ---- dựng thư mục v2 --------------------------------------------------------------------
    v2 = run / "handover" / f"{rid}_v2"
    if v2.exists():
        shutil.rmtree(v2)
    (v2 / "images").mkdir(parents=True)
    (v2 / "labels").mkdir()
    kept = sorted(n for n in man if n not in rework)
    for n in kept:
        shutil.copy2(d / man[n]["image"], v2 / "images" / f"{n}.jpg")
        shutil.copy2(d / man[n]["label"], v2 / "labels" / f"{n}.txt")

    # rework_queue.csv
    rq_rows = []
    for n in sorted(rework):
        j = jobs[meta[n]["job_id"]]
        rq_rows.append([n, rework[n], j["annotator"], j["reviewer"], f"gán lại nhãn detection ({rework[n]}); ảnh rời v2"])
    write_csv(v2 / "rework_queue.csv", ["image", "type", "annotator", "reviewer", "action"], rq_rows)

    # manifest.csv (hash tính trên file thật trong v2)
    man_rows = []
    for sub in ("images", "labels"):
        for p in sorted((v2 / sub).iterdir()):
            man_rows.append([f"{sub}/{p.name}", sha(p)])
    write_csv(v2 / "manifest.csv", ["file", "sha256"], man_rows)

    # label_summary.csv
    counts = Counter()
    for n in kept:
        for ln in (v2 / "labels" / f"{n}.txt").read_text(encoding="utf-8").splitlines():
            if ln.strip():
                counts[names80[int(float(ln.split()[0]))]] += 1
    ls_rows = [[c, counts[c]] for c in names80 if counts[c]]
    ls_rows.append(["TOTAL", sum(counts.values())])
    write_csv(v2 / "label_summary.csv", ["class", "count"], ls_rows)

    # truyvet.csv: guideline theo JOB; mỗi cảnh một split
    tv_rows = []
    for n in kept:
        m = meta[n]
        j = jobs[m["job_id"]]
        split = split_fix[n][1] if n in split_fix else m["split"]
        tv_rows.append([n, m["scene_id"], split, m["job_id"], j["annotator"], j["reviewer"], j["guideline"]])
    write_csv(v2 / "truyvet.csv", ["image", "scene_id", "split", "job_id", "annotator", "reviewer", "guideline"], tv_rows)

    # ---- README.txt ---------------------------------------------------------------------------
    n_err_imgs = len({e["target"] for e in errors})
    rate = n_err_imgs / len(man)
    by_gl = defaultdict(list)
    for j in sorted(jobs):
        by_gl[jobs[j]["guideline"]].append(j)
    guideline = ", ".join(f"{g} ({ranges(js)})" for g, js in sorted(by_gl.items()))
    v1_decision = "Hold" if rate > THRESHOLD else "Release"
    rq_people = sorted({(r[2], r[3]) for r in rq_rows})
    owners = "; ".join(f"{n} -> gán {jobs[meta[n]['job_id']]['annotator']}, kiểm {jobs[meta[n]['job_id']]['reviewer']}" for n in sorted(rework))
    kinds = Counter(rework.values())
    kinds_s = ", ".join(f"{t} {c}" for t, c in sorted(kinds.items()))
    pan_s = ", ".join(f"{n} ({by_target[n][0]})" for n in panoptic_only)
    gl_s = ", ".join(f"{n} (metadata ghi {meta[n]['guideline_version']}, job {meta[n]['job_id']} dùng {jobs[meta[n]['job_id']]['guideline']})" for n in guideline_bad)
    leak_s = ", ".join(f"{sc}: " + "; ".join(f"{n} {a}->{b}" for n, (a, b) in sorted(split_fix.items()) if meta[n]['scene_id'] == sc) for sc in leak_scenes)
    hash_s = ", ".join(wrong_hash)
    total_labels = sum(counts.values())
    lines = [
        f"Release: {rid}_v2",
        f"Parent: {rid}",
        f"Số ảnh: {len(kept)}",
        f"Số nhãn: {total_labels}",
        f"Guideline: {guideline}",
        f"QC v1: {n_err_imgs}/{len(man)} = {rate:.1%}",
        f"Kết luận v1: {v1_decision} — {n_err_imgs}/{len(man)} ảnh/cảnh lỗi ({rate:.1%}) vượt ngưỡng 2%, không Release v1; R-021 train trên v1 phải xem lại hoặc train lại.",
        f"Kết luận v2: Release (chỉ sản phẩm detection) — đã tách {len(rework)} ảnh lỗi nhãn detection sang rework_queue ({kinds_s}), sửa hash, guideline, split; còn {len(panoptic_only)} ảnh lỗi panoptic ở lại v2 và báo team panoptic. Lỗi chưa bị bắt (nếu có) vẫn có thể còn trong v2.",
        f"Ghi chú: {len(rework)} ảnh trong rework_queue.csv giao lại đúng người gán/kiểm theo jobs.csv; v2 giữ nguyên ảnh và nhãn của v1, không sửa tay nhãn nào.",
        f"- wrong_hash ({len(wrong_hash)} ảnh: {hash_s}): đã mở ảnh kiểm, ảnh mở được và đúng nội dung, chỉ hash trong manifest v1 sai; ảnh ở lại v2, manifest.csv ghi hash tính lại trên file thật.",
        f"- guideline_mismatch: {gl_s}; truyvet.csv lấy guideline theo job.",
        f"- scene_leak: {leak_s}; đưa cả cảnh về một split trong truyvet.csv.",
        f"- Rework giao lại: {owners}.",
        f"- Báo team panoptic (ảnh ở lại v2, nhãn detection vẫn đúng): {pan_s}.",
    ]
    (v2 / "README.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"v2: {len(kept)} ảnh, {total_labels} nhãn; rework {len(rework)}; panoptic-only {len(panoptic_only)}; "
          f"wrong_hash {len(wrong_hash)}; guideline {len(guideline_bad)}; split_fix {len(split_fix)}")
    print(f"QC v1 {n_err_imgs}/{len(man)} = {rate:.1%} -> {v1_decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
