# -*- coding: utf-8 -*-
"""Mechanical check of the batch-21 cards: spec vs manifest, geometry, files."""
import glob
import json
import os

R = os.path.dirname(os.path.abspath(__file__))
from PIL import Image

man = json.load(open(os.path.join(R, "gz_batches", "batch21.json"), encoding="utf-8"))
by_id = {r["id"]: r for r in man}

problems = []
checked = 0
for f in sorted(glob.glob(os.path.join(R, "b21*_spec", "*.json"))):
    spec = json.load(open(f, encoding="utf-8"))
    vid = os.path.basename(f)[:-5]
    m = by_id.get(vid)
    if not m:
        problems.append("%s: not in manifest" % vid)
        continue
    checked += 1
    out = spec.get("out", "").replace("\\", "/")
    if out != m["out"].replace("\\", "/"):
        problems.append("%s: out mismatch: %s vs %s" % (vid, out, m["out"]))
    if spec.get("diagram") not in ("LETTERS", "DIAGRAM", "NONE"):
        problems.append("%s: diagram=%r" % (vid, spec.get("diagram")))
    chan = m["source_channel"]
    if chan not in (spec.get("subtitle") or ""):
        problems.append("%s: subtitle lacks channel %r" % (vid, chan))
    card = os.path.join(R, out)
    if not os.path.exists(card):
        problems.append("%s: card missing %s" % (vid, out))
    else:
        im = Image.open(card)
        if im.width < 1200:
            problems.append("%s: card too narrow %s" % (vid, im.size))
    for pn in spec.get("panels", []):
        bb = pn.get("bbox")
        if not bb:
            problems.append("%s: panel without bbox" % vid)
            continue
        if bb[1] % 2 or bb[3] % 2:
            problems.append("%s: odd y/h %s" % (vid, bb))
        png = os.path.join(R, pn.get("png", "").replace("\\", "/"))
        if not os.path.exists(png):
            problems.append("%s: panel png missing %s" % (vid, pn.get("png")))
            continue
        pim = Image.open(png)
        if pim.size != (bb[2], bb[3]):
            problems.append("%s: panel size %s != bbox %s" % (vid, pim.size, bb[2:]))
        if pn.get("t", 0) > 10 ** 6:
            problems.append("%s: bad t" % vid)

print("batch21 specs checked: %d" % checked)
print("problems: %d" % len(problems))
for p in problems:
    print("  !", p)
if not problems:
    for f in sorted(glob.glob(os.path.join(R, "b21*_spec", "*.json"))):
        spec = json.load(open(f, encoding="utf-8"))
        print("  %-12s %-22s %-8s %s" % (os.path.basename(f)[:-5], spec.get("title", "")[:22],
                                          spec.get("diagram"), len(spec.get("panels", []))))
