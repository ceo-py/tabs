# -*- coding: utf-8 -*-
"""Pick one example video per channel that proves the on-screen-tab style,
preferring a grunge/rock artist, and dump the final ranked table.

Reads: _verify_channels.json + _verify_new2.json
Writes: _verify_final_table.json
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _verify_score import (GENRE_WORD, GRUNGE, ROCK_ACT, STYLE, TAB,  # noqa: E402
                           norm, score)


def pick(ch, s):
    """Prefer: tab + grunge act + style marker; then tab + rock act + style."""
    cands = []
    for v in ch.get("videos") or []:
        n = norm(v.get("t") or "")
        if not TAB.search(n):
            continue
        cands.append({
            "t": v.get("t"), "url": v.get("url"),
            "grunge": bool(GRUNGE.search(n)),
            "rock": bool(ROCK_ACT.search(n)),
            "style": bool(STYLE.search(n)),
        })
    best = None
    for rank, pred in enumerate([
        lambda c: c["grunge"] and c["style"],
        lambda c: c["grunge"],
        lambda c: c["rock"] and c["style"],
        lambda c: c["rock"],
        lambda c: c["style"],
    ]):
        for c in cands:
            if pred(c):
                best = dict(c, rank=rank)
                break
        if best:
            break
    return best


def main():
    raw = {}
    for f in ("_verify_channels.json", "_verify_new2.json"):
        if os.path.exists(f):
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            for k, ch in data.items():
                raw[k] = ch
    scored = []
    seen = set()
    for k, ch in raw.items():
        s = score(ch)
        cid = s["channel_id"]
        if cid in seen:
            continue
        seen.add(cid)
        s["_ch"] = ch
        scored.append(s)
    scored.sort(key=lambda d: -d["rock_loose"])
    out = []
    for s in scored:
        ex = pick(s["_ch"], s)
        out.append({
            "label": s["label"], "channel": s["channel"], "handle": s["uploader_id"],
            "url": s["channel_url"], "cid": s["channel_id"], "subs": s["subs"],
            "total": s["total"], "tabs": s["tabs"], "rock_act": s["rock_act"],
            "rock_loose": s["rock_loose"], "grunge": s["grunge"],
            "style": s["style"], "rock_style": s["rock_style"],
            "grunge_style": s["grunge_style"], "rock_prior": s["rock_prior"],
            "example": ex,
        })
    with open("_verify_final_table.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("%-3s %-30s %-26s %-8s %-6s %-5s %-6s %-5s %-5s" %
          ("#", "channel", "handle", "subs", "tabs", "rock", "grunge", "total", "style"))
    for i, d in enumerate(out, 1):
        print("%-3d %-30s %-26s %-8s %-6s %-5s %-6s %-5s %-5s" %
              (i, str(d["label"])[:30], str(d["handle"])[:26], d["subs"], d["tabs"],
               d["rock_loose"], d["grunge"], d["total"], d["style"]))
    print()
    for i, d in enumerate(out[:14], 1):
        ex = d["example"] or {}
        print("%2d %-28s | %s" % (i, str(d["label"])[:28], str(ex.get("t"))[:95]))
        print("    %s" % ex.get("url"))


if __name__ == "__main__":
    main()
