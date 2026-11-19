# -*- coding: utf-8 -*-
"""Build the batch-21 manifest: Oasis songs that have a tab video in channels
we have NOT measured yet (found by _oasis_search.py).

    py -3.14 _b21_manifest.py    -> gz_batches/batch21.json + batch21_ids.txt

Scoring (same idea as batch 20):
  +45  the title mentions tab/tabs/rolling tab
  +20  it is a cover / tutorial / lesson of the song
  +12  chords are named in the title
  -30  "solo" / "tone" / "riff" / "play along" only
Only candidates with score >= 30 are taken, one video per song.
"""
import json
import os
import re
import subprocess
import sys

R = os.path.dirname(os.path.abspath(__file__))
import _oasis_songs as OS

TAB_RE = re.compile(r"\btab", re.I)
COVER_RE = re.compile(r"cover|tutorial|lesson|how to play|play along|playthrough", re.I)
CHORD_RE = re.compile(r"\bchords?\b", re.I)
BAD_RE = re.compile(r"\bsolo\b|tone demo|riff only|play ?along|backing track", re.I)
W = re.compile(r"[a-z0-9]+")
STOP = {"the", "a", "of", "in", "on", "and", "it", "i", "you", "my", "me", "we",
        "to", "is", "that", "for", "by", "at", "as", "or", "noel", "oasis"}

# songs that already have a card (published or in batch 20)
def already_done():
    done = set()
    cards = json.load(open(os.path.join(R, "songs.json"), encoding="utf-8"))
    for c in cards:
        if "oasis" in (c.get("artist") or "").lower():
            done.add(re.sub(r"\W+", " ", (c.get("title") or "").lower()).strip())
    for b in ("batch20",):
        p = os.path.join(R, "gz_batches", "%s.json" % b)
        if os.path.exists(p):
            for r in json.load(open(p, encoding="utf-8")):
                done.add(re.sub(r"\W+", " ", (r.get("song") or "").lower()).strip())
    return done


def norm(s):
    return re.sub(r"\W+", " ", (s or "").lower()).strip()


def slug(song):
    s = re.sub(r"[^A-Za-z0-9]+", "-", song).strip("-")
    return "Oasis-%s" % s


def score(title):
    s = 0
    if TAB_RE.search(title):
        s += 45
    if COVER_RE.search(title):
        s += 20
    if CHORD_RE.search(title):
        s += 12
    if BAD_RE.search(title):
        s -= 30
    return s


def main():
    hits = json.load(open(os.path.join(R, "_oasis_search.json"), encoding="utf-8"))
    done = already_done()
    out = []
    for song, cands in hits.items():
        ns = norm(song)
        if ns in done:
            continue
        best = None
        for c in cands:
            t = c.get("title") or ""
            sc = score(t)
            if sc < 30:
                continue
            # the song words must be in the title
            tw = [w for w in W.findall(t.lower()) if w not in STOP]
            sw = [w for w in W.findall(song.lower()) if w not in STOP]
            if not sw or not all(w in tw for w in sw):
                continue
            if best is None or sc > best[0]:
                best = (sc, c)
        if not best:
            continue
        sc, c = best
        out.append({
            "id": c["id"],
            "artist": "Oasis",
            "song": song,
            "tag": "Tabs + Chords",
            "rock": True,
            "out": "out_gz/%s.png" % slug(song),
            "url": c["url"],
            "source_channel": c.get("channel") or "Unknown",
            "score": sc,
        })

    out.sort(key=lambda r: (-r["score"], r["song"]))
    p = os.path.join(R, "gz_batches", "batch21.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(R, "gz_batches", "batch21_ids.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(r["id"] for r in out) + "\n")

    print("batch21: %d lessons" % len(out))
    for r in out:
        print("  %-24s %-34s %3d  %s" % (r["song"][:24], r["source_channel"][:34],
                                         r["score"], r["id"]))


if __name__ == "__main__":
    main()
