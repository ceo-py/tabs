# -*- coding: utf-8 -*-
"""Independent DISCOVERY pass: fresh yt-dlp searches with new query wording,
then enumerate any channel that looks promising and count tabs / rock tabs.

Writes _verify_new.json. Uses the same independent classifier as
_verify_channels.py (imported from it).
"""
import json
import os
import re
import sys
import time

import yt_dlp

from _verify_channels import OPTS, classify, norm

QUERIES = [
    "grunge guitar tabs cover",
    "90s rock song tab play along",
    "acoustic rock cover tab on screen",
    "punk rock tab video cover",
    "alt rock guitar lesson tabs on screen",
    "guitar cover with tabs on screen",
    "rock song guitar tab tutorial lesson",
    "post punk alternative guitar cover tabs",
]

# channels already counted in _verify_channels.json -> skip
KNOWN_IDS = set()
if os.path.exists("_verify_channels.json"):
    with open("_verify_channels.json", encoding="utf-8") as fh:
        for v in json.load(fh).values():
            if v.get("channel_id"):
                KNOWN_IDS.add(v["channel_id"])
KNOWN_IDS |= {
    "UCSzJagetA7eVNc7ZQwXJVHg", "UCMFdBBF_dcamKYeYqHYe71g", "UCUXTxsU23H02fewbRzHXBgQ",
    "UCq5nkfMiOkek7s9j6c_Ao6g", "UCLdCUDlzx4qmwVlyVfUHxdg", "UCeWHmkuMBM760nryL8wLfLg",
    "UCqCAOEhhW6scLqcjbWKlspA", "UCLFZo57n3HpYw7o2Zkf6QJA", "UCciUBcG_bT-SOIS28FNY9-w",
    "UC_cm0YPagB8p2nXd8Z8Y_TA", "UC57CDvpwqAxHrJvVkZbaBxA", "UCN4wqAJ7UYPnVRGKshckZJQ",
    "UCrhU8Q7KgBuBme-0ggZeaUg", "UCkD0Qa33bTk-Qd9mxHc7Anw", "UCasFZzbM8JJ6dqSVEgL9VVg",
    "UCWPEi8ikVnAIu9h2XF8YrrA", "UCR8OM6seRnlh6bvZinGyyjA", "UCih2ClZ39b4JGUNclD0Gc8Q",
    "UCwsWbyUgY6c_HLmxbGj3oWw", "UCuLS9OV2fZfCnO_bEmodzHw",
}


def search_channels(query, limit=25):
    found = {}
    with yt_dlp.YoutubeDL(OPTS) as y:
        info = y.extract_info("ytsearch%d:%s" % (limit, query), download=False)
    for e in (info.get("entries") or []):
        if not e:
            continue
        cid = e.get("channel_id")
        if cid:
            found[cid] = {
                "channel": e.get("channel"),
                "channel_url": e.get("channel_url"),
                "uploader_id": e.get("uploader_id"),
            }
    return found


def enum(url):
    t0 = time.time()
    with yt_dlp.YoutubeDL(OPTS) as y:
        info = y.extract_info(url, download=False)
    entries = [e for e in (info.get("entries") or []) if e]
    recs = []
    for e in entries:
        t = e.get("title") or ""
        is_tab, rock_act, genre, grunge, cover = classify(t)
        recs.append({"t": t, "url": e.get("url"), "id": e.get("id"), "tab": is_tab,
                     "rock_act": rock_act, "genre": genre, "grunge": grunge, "cover": cover})
    tabs = [r for r in recs if r["tab"]]
    return {
        "channel": info.get("channel"), "channel_id": info.get("channel_id"),
        "uploader_id": info.get("uploader_id"), "channel_url": info.get("channel_url"),
        "subs": info.get("channel_follower_count"), "total": len(recs), "tabs": len(tabs),
        "rock_act": sum(1 for r in tabs if r["rock_act"]),
        "rock_loose": sum(1 for r in tabs if r["rock_act"] or r["genre"]),
        "grunge": sum(1 for r in tabs if r["grunge"]),
        "style": sum(1 for r in tabs if r["cover"]),
        "elapsed": round(time.time() - t0, 1), "videos": recs,
    }


def main():
    out = {}
    if os.path.exists("_verify_new.json"):
        with open("_verify_new.json", encoding="utf-8") as fh:
            out = json.load(fh)

    # 1. discovery
    cands = {}
    for q in QUERIES:
        try:
            f = search_channels(q)
        except Exception as exc:  # noqa: BLE001
            print("SEARCHFAIL %s %s" % (q, exc), file=sys.stderr, flush=True)
            continue
        new = [c for c in f if c not in KNOWN_IDS and c not in cands]
        print("QUERY %-45s channels=%-3d new=%d" % (q, len(f), len(new)), flush=True)
        for c, meta in f.items():
            cands.setdefault(c, meta)
        time.sleep(2)

    print("\n=== candidate channels (%d) ===" % len(cands), flush=True)
    for c, m in cands.items():
        print("  %-26s %-34s %s" % (c, str(m.get("channel"))[:34], m.get("uploader_id")), flush=True)

    # 2. enumerate
    for c, m in cands.items():
        if c in out or c in KNOWN_IDS:
            continue
        try:
            r = enum(m["channel_url"] if m.get("channel_url") else
                     "https://www.youtube.com/channel/%s/videos" % c)
        except Exception as exc:  # noqa: BLE001
            print("FAIL %s %s" % (m.get("channel"), exc), file=sys.stderr, flush=True)
            continue
        r["label"] = r.get("channel") or m.get("channel")
        out[c] = r
        print("%-34s total=%-5s tabs=%-5s rock_act=%-5s loose=%-5s grunge=%-4s style=%-5s subs=%-9s cid=%s handle=%s"
              % (str(r["label"])[:34], r["total"], r["tabs"], r["rock_act"], r["rock_loose"],
                 r["grunge"], r["style"], r["subs"], r["channel_id"], r["uploader_id"]), flush=True)
        with open("_verify_new.json", "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        time.sleep(2)

    print("\n=== NEW CHANNELS RANK (rock_act) ===", flush=True)
    for i, d in enumerate(sorted(out.values(), key=lambda x: -x["rock_act"]), 1):
        print("%2d. %-34s rock_act=%-4s loose=%-4s grunge=%-4s tabs=%-5s total=%-5s subs=%s"
              % (i, str(d.get("label"))[:34], d["rock_act"], d["rock_loose"], d["grunge"],
                 d["tabs"], d["total"], d["subs"]), flush=True)


if __name__ == "__main__":
    main()
