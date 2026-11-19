# -*- coding: utf-8 -*-
"""Verify the YouTube id -> song mapping for every batch-20 lesson.

    py -3.14 _b20_verify_titles.py

Fetches the real title of each video and compares it with the manifest song
name. Needs the local PO-Token server on 127.0.0.1:4416.
"""
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

R = os.path.dirname(os.path.abspath(__file__))
W = re.compile(r"[a-z0-9]+")
STOP = {"the", "a", "of", "in", "on", "and", "it", "i", "you", "my", "me", "we",
        "to", "is", "that", "don't", "dont", "for", "by", "at", "as", "or"}


def title_of(vid):
    cmd = [sys.executable, '-m', 'yt_dlp', '--no-warnings', '--skip-download',
           '--extractor-args', 'youtube:player_client=android_creator',
           '--print', '%(title)s|%(channel)s', 'https://www.youtube.com/watch?v=' + vid]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return vid, None, None
    out = (r.stdout or "").strip().splitlines()
    if not out:
        return vid, None, (r.stderr or "")[-200:]
    line = out[0]
    t, _, c = line.partition("|")
    return vid, t, c


def key(s):
    return [w for w in W.findall((s or "").lower()) if w not in STOP]


def main():
    man = json.load(open(os.path.join(R, "gz_batches", "batch20.json"), encoding="utf-8"))
    items = man if isinstance(man, list) else list(man.values())
    ids = [r["id"] for r in items]
    by = {r["id"]: r for r in items}

    res = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for vid, t, c in ex.map(title_of, ids):
            res[vid] = (t, c)

    bad = []
    print("%-14s %-26s %s" % ("id", "manifest song", "real title"))
    print("-" * 100)
    for r in sorted(items, key=lambda x: x["id"]):
        vid = r["id"]
        t, c = res.get(vid, (None, None))
        song = r["song"]
        ok = False
        if t:
            tk = set(key(t))
            sk = set(key(song))
            ok = bool(sk) and sk <= tk
        flag = "OK " if ok else "?? "
        if not ok:
            bad.append((vid, song, t, c))
        print("%s%-12s %-26s %s" % (flag, vid, song[:26], (t or "<no title>")[:56]))

    print()
    if bad:
        print("NEEDS REVIEW (%d):" % len(bad))
        for vid, song, t, c in bad:
            print("  %-12s manifest='%s'  real='%s'  channel=%s" % (vid, song, t, c))
    else:
        print("all %d ids match their manifest song" % len(items))

    with open(os.path.join(R, "_b20_real_titles.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
