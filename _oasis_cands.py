# -*- coding: utf-8 -*-
"""Print the candidate tab videos for given Oasis songs from _oasis_gap.md logic."""
import csv
import json
import os
import re
import sys

R = os.path.dirname(os.path.abspath(__file__))
import _oasis_songs as OS

W = re.compile(r"[a-z0-9]+")
STOP = {"the", "a", "of", "in", "on", "and", "it", "i", "you", "my", "me",
        "we", "to", "is", "that", "don't", "dont"}

rows = list(csv.DictReader(open(os.path.join(R, "_channels_all_videos.csv"), encoding="utf-8")))
want = [a.lower() for a in sys.argv[1:]]

for canon in OS.OASIS_SONGS:
    if canon.lower() not in want:
        continue
    key = [w for w in W.findall(canon.lower()) if w not in STOP]
    print("\n=== %s ===" % canon)
    for x in rows:
        t = W.findall(x["title"].lower())
        if "oasis" in t:
            if OS.match_song(x["title"]) != canon:
                continue
        else:
            pos = 0
            ok = True
            for w in key:
                while pos < len(t) and t[pos] != w:
                    pos += 1
                if pos >= len(t):
                    ok = False
                    break
                pos += 1
            if not ok:
                continue
        if "tab" not in x["flags"].lower():
            continue
        print("  [%-22s] %s" % (x["channel"][:22], x["title"][:78]))
        print("      %s" % x["url"])
