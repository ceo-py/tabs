# -*- coding: utf-8 -*-
"""Final consolidation pass for batch 20.

1. Patches the per-namespace compose copies (b20b / b20c / b20d):
   a) note_extra  : 32*(n-2) -> 32*(n-1)   (the last note line sat flush on
                                              the bottom edge and looked cut)
   b) wrap_note   : keep the "   " separators between the note fields visible.
                     The old code split on ' ' and rejoined with ' ', so the
                     three spaces between "Chords: ..." and "Strumming: ..."
                     collapsed into one and the fields ran together.
2. Rebuilds all 21 cards from the (already audited) specs.
3. Verifies every output.

    py -3.14 _b20_finalize.py
"""
import json
import os
import re
import subprocess
import sys

R = os.path.dirname(os.path.abspath(__file__))
SPECS = {
    "b20a": ["wtjoRQfmHQI", "6CVKC5LVAAs", "1F7ZncckR1o", "42GX06WDX5w", "qPTV5wkocv0",
             "BAoPHsvI1v0"],
    "b20b": ["BYLzgA94yxU", "iop2pF2hyw8", "CNNKH_oWCK0", "01gU00k6rY4", "GMq1kz1ORJs",
             "d1RxW2VIVcI", "XEyu6iQQURo", "3dARZh-lqAI"],
    "b20c": ["BN9bZdDOyZQ", "dqS2wUriKG8", "DjmB1xM7xME", "kBs2nBraZBM"],
    "b20d": ["Lbs---ONA3I", "p0Fpu1mZKOk", "B-BkCZrGp2M"],
}

OLD_EXTRA = "note_extra = 32 * max(0, len(note_lines) - 2)"
NEW_EXTRA = "note_extra = 32 * max(0, len(note_lines) - 1)"

OLD_WRAP = """def wrap_note(note, font, max_w):
    words = note.split(' ')"""
NEW_WRAP = """def wrap_note(note, font, max_w):
    # keep the multi-space separators between the note fields readable
    note = re.sub(r'\\s{2,}', ' \\u00b7 ', note)
    words = note.split(' ')"""


def patch(path):
    if not os.path.exists(path):
        return "missing"
    src = open(path, encoding="utf-8").read()
    orig = src
    if OLD_EXTRA in src:
        src = src.replace(OLD_EXTRA, NEW_EXTRA)
    if OLD_WRAP in src:
        src = src.replace(OLD_WRAP, NEW_WRAP)
    if "import re" not in src:
        # put the import next to the other imports
        m = re.search(r"^import .*$", src, re.M)
        if m:
            src = src[:m.start()] + "import re\n" + src[m.start():]
        else:
            src = "import re\n" + src
    if src != orig:
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        return "patched"
    return "unchanged"


def build(ns):
    ids = SPECS[ns]
    script = os.path.join(R, "%s_build.py" % ns)
    if not os.path.exists(script):
        print("  %s: no build script" % ns)
        return False
    r = subprocess.run([sys.executable, script] + ids, cwd=R, capture_output=True,
                       text=True, timeout=3600)
    ok = r.returncode == 0
    print("  %s: rc=%s %s" % (ns, r.returncode, "OK" if ok else "FAIL"))
    if not ok:
        print(r.stdout[-1500:])
        print(r.stderr[-1500:])
    return ok


def verify():
    man = json.load(open(os.path.join(R, "gz_batches", "batch20.json"), encoding="utf-8"))
    items = man if isinstance(man, list) else list(man.values())
    from PIL import Image
    problems = []
    for it in items:
        out = it["out"].replace("\\", "/")
        p = os.path.join(R, out)
        if not os.path.exists(p):
            problems.append("%s: card missing" % it["id"])
            continue
        for ns in SPECS:
            sp = os.path.join(R, "%s_spec" % ns, "%s.json" % it["id"])
            if os.path.exists(sp):
                spec = json.load(open(sp, encoding="utf-8"))
                break
        else:
            problems.append("%s: no spec" % it["id"])
            continue
        if spec.get("out", "").replace("\\", "/") != out:
            problems.append("%s: out mismatch" % it["id"])
        im = Image.open(p)
        if im.width < 1400:
            problems.append("%s: card too narrow" % it["id"])
        for pn in spec.get("panels", []):
            bb = pn.get("bbox")
            if not bb:
                problems.append("%s: panel without bbox" % it["id"])
                continue
            if bb[1] % 2 or bb[3] % 2:
                problems.append("%s: odd y/h in bbox %s" % (it["id"], bb))
            png = os.path.join(R, pn.get("png", "").replace("\\", "/"))
            if not os.path.exists(png):
                problems.append("%s: panel png missing %s" % (it["id"], pn.get("png")))
                continue
            pim = Image.open(png)
            if pim.size != (bb[2], bb[3]):
                problems.append("%s: panel size %s != bbox %s" % (it["id"], pim.size, bb[2:]))
    print("  verify: %d cards, %d problems" % (len(items), len(problems)))
    for p in problems:
        print("    !", p)
    return not problems


def main():
    print("patching compose copies:")
    for ns in SPECS:
        p = os.path.join(R, "%s_compose.py" % ns)
        print("  %-5s %s" % (ns, patch(p)))

    print("rebuilding:")
    allok = True
    for ns in SPECS:
        allok &= build(ns)

    print("verifying:")
    allok &= verify()
    print("\n%s" % ("ALL GOOD" if allok else "PROBLEMS FOUND"))
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
