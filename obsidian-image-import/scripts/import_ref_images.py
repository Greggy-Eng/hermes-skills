#!/usr/bin/env python3
"""obsidian-image-import — plan/apply image imports from Documents/Reference into the Obsidian vault.

Implements skill steps 1,3-10,12: scan, convert (HEIC->JPG via sips, SVG->JPG via rsvg + trim),
sanitize filenames (U+202F/NNBSP -> space), dated folders with _a/_b per-batch suffixes,
Master+{count}.md embeds (bare-filename when vault-unique, full vault path otherwise),
source batch move, and step-12 visibility verification (exit 1 on any failure).

Usage:
  import_ref_images.py                 # print plan, change nothing (default)
  import_ref_images.py --apply       # execute the plan
  import_ref_images.py --source DIR --vault DIR --apply   # override paths (tests/backlog)
"""
import argparse, datetime, os, re, shutil, subprocess, sys

IMG = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
CONV = {".heic", ".svg"}

def sanitize(name):
    return name.replace("\u202f", " ").replace("\u00a0", " ")

def free_path(path):
    """First available path: base, base_a, base_b, ..."""
    if not os.path.exists(path):
        return path
    i = 0
    while True:
        cand = f"{path}_{'abcdefghijklmnopqrstuvwxyz'[i // 26]}{i % 26}" if i >= 26 else f"{path}_{chr(97 + i)}"
        if not os.path.exists(cand):
            return cand
        i += 1

def which(cmd):
    from shutil import which as w
    return w(cmd) is not None

def scan(src):
    files = [f for f in sorted(os.listdir(src))
             if os.path.isfile(os.path.join(src, f)) and not f.startswith(".")
             and os.path.splitext(f)[1].lower() in IMG | CONV]
    return files

def build_plan(src, vault, date):
    ref = os.path.join(vault, "Reference")
    files = scan(src)
    if not files:
        return None
    heic = [f for f in files if f.lower().endswith(".heic")]
    svg = [f for f in files if f.lower().endswith(".svg")]
    direct = [f for f in files if f not in heic + svg]
    count = len(files)
    parent = free_path(os.path.join(ref, date))
    nested = os.path.join(parent, f"{date}+{count}")
    srcmove = free_path(os.path.join(src, f"{date}-source"))
    missing_tools = [t for t, need in (("sips", heic), ("rsvg-convert", svg)) if need and not which(t)]
    return dict(src=src, vault=vault, date=date, files=files, heic=heic, svg=svg,
                direct=direct, parent=parent, nested=nested, srcmove=srcmove,
                master=os.path.join(parent, f"Master+{count}.md"), missing_tools=missing_tools)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0

def apply(plan):
    if plan["missing_tools"]:
        print(f"ABORT: missing tools {plan['missing_tools']}"); return 1
    os.makedirs(plan["nested"], exist_ok=True)
    placed = []
    failures = []
    for f in plan["heic"]:
        out = os.path.join(plan["nested"], sanitize(re.sub(r"\.heic$", ".jpg", f, flags=re.I)))
        if run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "best", "--out", out,
               os.path.join(plan["src"], f)]):
            placed.append(os.path.basename(out))
        else:
            failures.append(f"HEIC->JPG: {f}"); print("FAIL HEIC->JPG:", f)
    for f in plan["svg"]:
        raw = os.path.join(plan["nested"], sanitize(re.sub(r"\.svg$", ".jpg", f, flags=re.I)))
        ok = run(["rsvg-convert", "-w", "1920", "-h", "1080", "-o", raw, os.path.join(plan["src"], f)])
        if ok:
            run(["magick", raw, "-trim", "+repage", raw])  # trim SVG-derived only
            placed.append(os.path.basename(raw))
        else:
            failures.append(f"SVG->JPG: {f}"); print("FAIL SVG->JPG:", f)
    for f in plan["direct"]:
        dest = os.path.join(plan["nested"], sanitize(f))
        shutil.copy2(os.path.join(plan["src"], f), dest)
        placed.append(os.path.basename(dest))

    # rename nested + master to actual count
    count = len(placed)
    nested_final = os.path.join(plan["parent"], f"{plan['date']}+{count}")
    if nested_final != plan["nested"]:
        os.rename(plan["nested"], nested_final)
    master = os.path.join(plan["parent"], f"Master+{count}.md")
    # embeds: bare name iff unique across vault (excluding this batch's own copies)
    lines = []
    for n in sorted(placed):
        hits = sum(1 for root, _, fs in os.walk(plan["vault"])
                   if ".git" not in root and n in fs)
        rel = os.path.join(plan["date"], os.path.basename(nested_final), n)
        lines.append(f"![[{n}]]" if hits <= 1 else f"![[Reference/{rel}]]")
    open(master, "w").write(f"# Master+{count} — {plan['date']}\n\n" + "\n".join(lines) + "\n")

    # move source batch (never merge)
    os.makedirs(plan["srcmove"], exist_ok=True)
    for f in plan["files"]:
        shutil.move(os.path.join(plan["src"], f), os.path.join(plan["srcmove"], f))

    vrc = verify(plan["vault"], master, nested_final)
    if failures:
        print("CONVERSION FAILURES:", failures)
        return 1
    return vrc

def verify(vault, master, nested):
    ok = True
    embeds = [l[3:-2] for l in open(master).read().splitlines() if l.startswith("![[")]
    for e in embeds:
        p = e if e.startswith("Reference/") else None
        target = os.path.join(vault, e) if p else os.path.join(nested, e)
        if not os.path.exists(target):
            print("MISSING:", e); ok = False; continue
        head = open(target, "rb").read(8)
        magic = head == b"\x89PNG\r\n\x1a\n" or head[:3] == b"\xff\xd8\xff"
        if not magic:
            print("BAD MAGIC:", e); ok = False
        if not all(ord(c) < 128 for c in os.path.basename(e)):
            print("NON-ASCII:", e); ok = False
        if e.lower().endswith(".heic"):
            print("HEIC IN MASTER:", e); ok = False
    n = len(os.listdir(nested))
    if n != len(embeds):
        print(f"COUNT MISMATCH: folder {n} vs embeds {len(embeds)}"); ok = False
    print("VISIBILITY:", "PASS" if ok else "FAIL", f"({len(embeds)} embeds)")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=os.path.expanduser("~/Documents/Reference"))
    ap.add_argument("--vault", default=os.path.expanduser("~/Greggy-AI"))
    ap.add_argument("--date", default=datetime.date.today().strftime("%Y-%m-%d"))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    plan = build_plan(a.source, a.vault, a.date)
    if not plan:
        print(f"No image files found in {a.source}. Import cancelled."); return 0
    print(f"PLAN: {len(plan['files'])} files (direct={len(plan['direct'])} heic={len(plan['heic'])} svg={len(plan['svg'])})")
    print("  vault parent :", plan["parent"])
    print("  nested       :", plan["nested"])
    print("  master       :", plan["master"])
    print("  source move  :", plan["srcmove"])
    if plan["missing_tools"]:
        print("  MISSING TOOLS:", plan["missing_tools"])
    if not a.apply:
        print("DRY RUN — nothing changed. Re-run with --apply.")
        return 0
    return apply(plan)

if __name__ == "__main__":
    sys.exit(main())
