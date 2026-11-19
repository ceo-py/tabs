# -*- coding: utf-8 -*-
"""Sanity check for _mark_have.py output."""
import collections
import json
import os
import random

R = os.path.dirname(os.path.abspath(__file__))
mp = json.load(open(os.path.join(R, "_have_map.json"), encoding="utf-8"))
cards = json.load(open(os.path.join(R, "songs.json"), encoding="utf-8"))

by_ct = collections.Counter((v["card_artist"], v["card_title"]) for v in mp.values())


def nk(s):
    return " ".join("".join(ch if ch.isalnum() else " " for ch in (s or "").lower()).split())


have = set((nk(a), nk(t)) for a, t in by_ct)
missing = [(s.get("artist", ""), s.get("title", "")) for s in cards
           if (nk(s.get("artist", "")), nk(s.get("title", ""))) not in have]
print("cards with no matching research video: %d" % len(missing))
for m in missing[:20]:
    print("    ", m)

print()
print("sample matches:")
random.seed(7)
for v in random.sample(list(mp.values()), 20):
    print("  %-24s %-38s -> %s - %s" % (v["channel"][:24], v["title"][:38],
                                        v["card_artist"], v["card_title"]))
