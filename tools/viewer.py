"""Cong cu xem anh de review (nguoi D). Pillow duoc phep o day, KHONG dung trong validator.

Dung:
  py -X utf8 tools/viewer.py <delivery> --candidates c.json --log review_log.csv --reviewer D   # mo cua so (Tkinter)
  py -X utf8 tools/viewer.py <delivery> --images 000000000139 --export out_png                  # xuat PNG

candidates.json: chap nhan list ten anh, list dict {image,type,...}, hoac {"candidates":[...]}.
Phim tat: C = confirmed, R = rejected, Phai/Trai = anh ke/truoc, +/- = zoom.
"""
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import pngutil  # doc mask panoptic (thu vien chuan)

PALETTE = [(230, 25, 75), (60, 180, 75), (255, 225, 25), (0, 130, 200), (245, 130, 48),
           (145, 30, 180), (70, 240, 240), (240, 50, 230), (210, 245, 60), (250, 190, 212)]


class Delivery:
    def __init__(self, root: str):
        self.root = Path(root)
        self.classes = {}
        for ln in (self.root / "classes.txt").read_text(encoding="utf-8").splitlines():
            if ln.strip():
                i, name = ln.split(" ", 1)
                self.classes[int(i)] = name
        doc = json.loads((self.root / "panoptic.json").read_text(encoding="utf-8"))
        self.cats = {c["id"]: c["name"] for c in doc["categories"]}
        self.imgs = {Path(im["file_name"]).stem: im for im in doc["images"]}
        self.anns = {a["image_id"]: a for a in doc["annotations"]}

    def boxes(self, stem, w, h):
        p = self.root / "labels" / f"{stem}.txt"
        out = []
        if p.is_file():
            for ln in p.read_text().splitlines():
                t = ln.split()
                if len(t) == 5:
                    c, x, y, bw, bh = int(float(t[0])), *map(float, t[1:])
                    out.append((c, (x - bw / 2) * w, (y - bh / 2) * h, (x + bw / 2) * w, (y + bh / 2) * h))
        return out

    def render(self, stem, zoom=3):
        im = self.imgs[stem]
        img_path = self.root / "images" / im["file_name"]
        if img_path.is_file():
            base = Image.open(img_path).convert("RGB")
        else:  # anh thieu (missing_image): ve nen xam de van xem duoc box/mask
            base = Image.new("RGB", (im.get("width", 320), im.get("height", 240)), (90, 90, 90))
            ImageDraw.Draw(base).text((5, 5), "THIEU FILE ANH", fill=(255, 80, 80))
        w, h = base.size
        left = base.resize((w * zoom, h * zoom), Image.LANCZOS)
        d = ImageDraw.Draw(left)
        for c, x0, y0, x1, y1 in self.boxes(stem, w, h):
            col = PALETTE[c % len(PALETTE)]
            d.rectangle([x0 * zoom, y0 * zoom, x1 * zoom, y1 * zoom], outline=col, width=2)
            d.text((x0 * zoom + 3, y0 * zoom + 2), self.classes.get(c, f"?{c}"), fill=col)
        right = base.resize((w * zoom, h * zoom), Image.LANCZOS)
        ann = self.anns.get(im["id"])
        if ann:
            mw, mh, buf = pngutil.read_rgb(self.root / "masks" / ann["file_name"])
            ids = {}
            for i in range(mw * mh):
                v = buf[3 * i] + buf[3 * i + 1] * 256 + buf[3 * i + 2] * 65536
                ids[i] = v
            over = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
            px = over.load()
            segs = {s["id"]: s for s in ann["segments_info"]}
            for i, v in ids.items():
                if v in segs:
                    px[i % mw, i // mw] = PALETTE[v % len(PALETTE)] + (110,)
            over = over.resize((w * zoom, h * zoom), Image.NEAREST)
            right = Image.alpha_composite(right.convert("RGBA"), over).convert("RGB")
            d = ImageDraw.Draw(right)
            for s in segs.values():
                bx, by, bw, bh = s["bbox"]
                col = PALETTE[s["id"] % len(PALETTE)]
                d.text((bx * zoom + 3, by * zoom + 2), self.cats.get(s["category_id"], f"?{s['category_id']}")
                       + (" crowd" if s.get("iscrowd") else ""), fill=(255, 255, 255))
        canvas = Image.new("RGB", (w * zoom * 2 + 10, h * zoom), (30, 30, 30))
        canvas.paste(left, (0, 0)); canvas.paste(right, (w * zoom + 10, 0))
        return canvas


def load_candidates(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("candidates", data.get("items", []))
    out = []
    for c in data:
        out.append(("", c) if isinstance(c, str) else (c.get("type", ""), c.get("image") or c.get("target")))
    return [(t, i) for t, i in out if i]


def read_log(path):
    """Doc review_log.csv cu: {image: (type, verdict, note)} (dong cuoi cung cua moi anh thang)."""
    out = {}
    if Path(path).is_file():
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                out[r["image"]] = (r["type"], r["verdict"], r["note"])
    return out


def write_log(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["image", "type", "verdict", "note"])
        for img, (t, v, n) in rows.items():
            wr.writerow([img, t, v, n])


def gui(dv, items, log, reviewer):
    import tkinter as tk
    from tkinter import messagebox, ttk
    from PIL import ImageTk
    st = {"i": 0, "zoom": 2}
    saved = read_log(log)   # da chot (image -> type, verdict, note co tien to [nguoi])
    drafts = {}             # dang go do: image -> (type, note); giu khi chuyen anh
    prefix = f"[{reviewer}] "
    root = tk.Tk(); root.title("Review - trai: detection | phai: panoptic")
    lbl = tk.Label(root); lbl.pack()
    info = tk.Label(root, font=("Segoe UI", 11)); info.pack()
    ent = tk.Entry(root, width=100); ent.pack(pady=4)
    tf = tk.Frame(root); tf.pack()
    tk.Label(tf, text="Loai loi:").pack(side="left")
    tent = ttk.Combobox(tf, width=22, state="readonly", values=["class_swap", "category_swap", "bbox_drift", "missing_box", "instance_merge"]); tent.pack(side="left", padx=4)

    def keep_draft():
        _, img = items[st["i"]]
        drafts[img] = (tent.get().strip(), ent.get().strip())

    def show():
        t, img = items[st["i"]]
        pic = dv.render(img, st["zoom"])
        sw, sh = root.winfo_screenwidth() - 40, root.winfo_screenheight() - 260  # chua cho cho o nhap + nut
        k = min(1.0, sw / pic.width, sh / pic.height)  # thu nho cho vua man hinh
        if k < 1.0:
            pic = pic.resize((int(pic.width * k), int(pic.height * k)), Image.LANCZOS)
        st["photo"] = ImageTk.PhotoImage(pic)
        lbl.config(image=st["photo"])
        if img in drafts:
            dt, dn = drafts[img]
        elif img in saved:
            dt, dn = saved[img][0], saved[img][2].removeprefix(prefix)
        else:
            dt, dn = ("" if t == "class_or_category_swap" else t), ""
        tent.set(dt); ent.delete(0, "end"); ent.insert(0, dn)
        state = f"DA CHOT: {saved[img][1]}" if img in saved else "chua review"
        info.config(text=f"[{st['i']+1}/{len(items)}] {img}  loai ung vien: {t}  |  {state}   (Ctrl+C=confirmed, Ctrl+R=rejected, ghi chu >=20 ky tu)")

    def verdict(v):
        _, img = items[st["i"]]
        note = ent.get().strip()
        t = tent.get().strip()
        if not t:
            messagebox.showwarning("Loai loi", "Chon loai: class_swap hoac category_swap (xem anh: nguon nao sai).")
            return
        if len(note) < 20:
            messagebox.showwarning("Ghi chu", "Ghi chu phai noi THAY GI trong anh (>= 20 ky tu).")
            return
        saved[img] = (t, v, prefix + note)   # ghi de neu review lai, khong trung dong
        drafts.pop(img, None)
        write_log(log, saved)
        move(1, keep=False)

    def move(d, keep=True):
        if keep:
            keep_draft()
        st["i"] = max(0, min(len(items) - 1, st["i"] + d)); show()

    def zoom(d):
        keep_draft(); st["zoom"] = max(1, min(6, st["zoom"] + d)); show()

    bar = tk.Frame(root); bar.pack()
    for text, fn in [("<", lambda: move(-1)), ("confirmed (Ctrl+C)", lambda: verdict("confirmed")),
                     ("rejected (Ctrl+R)", lambda: verdict("rejected")), (">", lambda: move(1)),
                     ("zoom +", lambda: zoom(1)), ("zoom -", lambda: zoom(-1))]:
        tk.Button(bar, text=text, command=fn).pack(side="left", padx=3)
    root.bind("<Control-c>", lambda e: verdict("confirmed")); root.bind("<Control-r>", lambda e: verdict("rejected"))
    root.bind("<Right>", lambda e: move(1) if root.focus_get() is not ent else None)
    root.bind("<Left>", lambda e: move(-1) if root.focus_get() is not ent else None)
    show(); root.mainloop()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("delivery"); ap.add_argument("--candidates"); ap.add_argument("--images", nargs="*")
    ap.add_argument("--export"); ap.add_argument("--zoom", type=int, default=3)
    ap.add_argument("--log", default="review_log.csv"); ap.add_argument("--reviewer", default="?")
    a = ap.parse_args()
    dv = Delivery(a.delivery)
    items = load_candidates(a.candidates) if a.candidates else [("", s) for s in (a.images or sorted(dv.imgs))]
    if a.export:
        Path(a.export).mkdir(parents=True, exist_ok=True)
        for t, s in items:
            dv.render(s, a.zoom).save(Path(a.export) / f"{s}.png")
        print(f"da xuat {len(items)} anh vao {a.export}")
    else:
        gui(dv, items, a.log, a.reviewer)


if __name__ == "__main__":
    main()
