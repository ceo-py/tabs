# -*- coding: utf-8 -*-
"""Look up cards by song title to inspect possible mislabels."""
import json
import os
import sys

R = os.path.dirname(os.path.abspath(__file__))
cards = json.load(open(os.path.join(R, "songs.json"), encoding="utf-8"))
needles = [n.lower() for n in sys.argv[1:]]
for s in cards:
    t = (s.get("title") or "").lower()
    if any(n in t for n in needles):
        print("  %-28s %-42s ch=%-26s %s" % (s.get("artist", ""), s.get("title", ""),
                                             s.get("channel", ""), s.get("youtube_id", "")))
