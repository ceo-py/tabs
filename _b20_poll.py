# -*- coding: utf-8 -*-
"""Poll until every batch-20 spec dir has one JSON per expected video."""
import json
import os
import time

R = os.path.dirname(os.path.abspath(__file__))
EXPECT = {"b20a_spec": 5, "b20b_spec": 8, "b20c_spec": 4, "b20d_spec": 4}
# b20d has 3 lessons in the manifest
EXPECT["b20d_spec"] = 3


def counts():
    out = {}
    for d, n in EXPECT.items():
        p = os.path.join(R, d)
        c = 0
        if os.path.isdir(p):
            c = len([f for f in os.listdir(p) if f.endswith(".json")])
        out[d] = (c, n)
    return out


deadline = time.time() + 1800
while time.time() < deadline:
    c = counts()
    done = all(v[0] >= v[1] for v in c.values())
    print("%s  %s" % (time.strftime("%H:%M:%S"),
                      "  ".join("%s=%d/%d" % (k, v[0], v[1]) for k, v in c.items())), flush=True)
    if done:
        print("ALL SPECS PRESENT", flush=True)
        break
    time.sleep(45)
else:
    print("TIMEOUT", flush=True)
