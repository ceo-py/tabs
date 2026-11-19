# -*- coding: utf-8 -*-
"""Swap the Who Feels Love? lesson in batch 21 to a video that actually shows
the notation.

The first pick (Wayne R Guitar, zYP0Npys8s4) turns out to contain no notation
whatsoever - no TAB, no chord names, no diagrams, no text overlay - so the card
would have been empty. The Fretboard Fundamentals version (WPupZKbRTvo) has the
same layout as the already-built Love Like A Bomb card (chord box + navy
chords/lyrics banner + labelled fret diagrams).

    py -3.14 _b21_swap.py
"""
import json
import os

R = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(R, "gz_batches", "batch21.json")

OLD_ID = "zYP0Npys8s4"
NEW = {
    "id": "WPupZKbRTvo",
    "artist": "Oasis",
    "song": "Who Feels Love?",
    "tag": "Tabs + Chords",
    "rock": True,
    "out": "out_gz/Oasis-Who-Feels-Love.png",
    "url": "https://www.youtube.com/watch?v=WPupZKbRTvo",
    "source_channel": "Fretboard Fundamentals",
    "score": 65,
}

rows = json.load(open(P, encoding="utf-8"))
out = []
for r in rows:
    if r["id"] == OLD_ID:
        out.append(NEW)
    else:
        out.append(r)
with open(P, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

ip = os.path.join(R, "gz_batches", "batch21_ids.txt")
ids = [NEW["id"] if i == OLD_ID else i for i in
       [l.strip() for l in open(ip, encoding="utf-8") if l.strip()]]
with open(ip, "w", encoding="utf-8") as f:
    f.write("\n".join(ids) + "\n")

print("batch21 now:")
for r in out:
    print("  %-12s %-20s %-26s %s" % (r["id"], r["song"][:20], r["source_channel"][:26], r["out"]))
