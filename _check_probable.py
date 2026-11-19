# -*- coding: utf-8 -*-
"""Inspect the 'probable' matches (song matched, artist not named in the title)."""
import json
import os
import random

R = os.path.dirname(os.path.abspath(__file__))
mp = json.load(open(os.path.join(R, "_have_map.json"), encoding="utf-8"))
prob = [v for v in mp.values() if v["match"] == "probable"]
print("probable: %d" % len(prob))
random.seed(11)
for v in random.sample(prob, 30):
    print("  %-24s %-44s -> %s - %s" % (v["channel"][:24], v["title"][:44],
                                        v["card_artist"], v["card_title"]))
