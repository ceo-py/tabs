# -*- coding: utf-8 -*-
"""Dump full card records whose title matches an argument."""
import json
import os
import sys

R = os.path.dirname(os.path.abspath(__file__))
cards = json.load(open(os.path.join(R, "songs.json"), encoding="utf-8"))
needles = [n.lower() for n in sys.argv[1:]]
for s in cards:
    t = (s.get("title") or "").lower()
    if any(n in t for n in needles):
        print(json.dumps(s, ensure_ascii=False, indent=1))
