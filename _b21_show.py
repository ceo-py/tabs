# -*- coding: utf-8 -*-
"""Print all search candidates per song with their score, for manual picking."""
import json
import os
import sys

R = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, R)
from _b21_manifest import score  # noqa

hits = json.load(open(os.path.join(R, "_oasis_search.json"), encoding="utf-8"))
want = [a.lower() for a in sys.argv[1:]]
for song, cands in hits.items():
    if want and song.lower() not in want:
        continue
    print("\n=== %s ===" % song)
    for c in cands:
        print("  %3d  %-26s %-70s %s" % (score(c.get("title") or ""),
                                         (c.get("channel") or "")[:26],
                                         (c.get("title") or "")[:70], c.get("id")))
