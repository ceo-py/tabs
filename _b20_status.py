# -*- coding: utf-8 -*-
"""Where batch 20 stands right now: manifest vs spec vs built card."""
import json
import os

R = os.path.dirname(os.path.abspath(__file__))
man = json.load(open(os.path.join(R, "gz_batches", "batch20.json"), encoding="utf-8"))
if isinstance(man, dict):
    items = list(man.values())
elif isinstance(man, list):
    items = man
else:
    items = []
items = [i for i in items if isinstance(i, dict) and i.get("id")]

print("%-14s %-32s %-30s %-9s %s" % ("id", "song", "channel", "spec", "card"))
print("-" * 110)
nspec = ncard = 0
for it in sorted(items, key=lambda x: x.get("source_channel", "")):
    vid = it["id"]
    ch = it.get("source_channel", "?")
    spec = None
    for d in ("b20a_spec", "b20b_spec", "b20c_spec", "b20d_spec"):
        p = os.path.join(R, d, vid + ".json")
        if os.path.exists(p):
            spec = d
            break
    out = (it.get("out") or "").replace("\\", "/")
    card = "✅" if out and os.path.exists(os.path.join(R, out)) else "—"
    if spec:
        nspec += 1
    if card == "✅":
        ncard += 1
    print("%-14s %-32s %-30s %-9s %s" % (vid, (it.get("song") or "")[:32], ch[:30],
                                         spec or "—", card))
print("-" * 110)
print("manifest: %d   specs: %d   built cards: %d" % (len(items), nspec, ncard))
