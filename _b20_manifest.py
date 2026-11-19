# -*- coding: utf-8 -*-
"""Build the Oasis batch manifest: one source video per Oasis song.

Skips songs we already have a card for (songs.json = source of truth).
Writes gz_batches/batch20.json + batch20_ids.txt
"""
import json
import os
import re

R = os.path.dirname(os.path.abspath(__file__))
import _channels_all_dump as D
from _oasis_songs import match_song
import _have

# channels whose videos show tab/chord/strumming graphics over a performance
ONSCREEN = {
    "Lex Guitar Tabs": 60, "guitar cover with tabs & chords": 55, "Sparky Guitar": 50,
    "ike": 45, "CWZ Guitar": 40, "Play Along Guitar": 38, "CoverSolutions": 30,
    "GuitarZero2Hero Express": 35, "GuitarZero2Hero": 33, "Marc Sanz Guitar": 28,
    "Dotti Brothers": 25, "Mike Atsushi": 22, "Easy Guitar Tabs Tutorial": 20,
    "Super Easy Bass": 12, "Guitar Tab Lab": 15, "Marty Music": 18,
    "Let's Play All": 16, "SAW": 6, "Yoni Schlesinger": 8, "christianvib": 8,
    "Cameron Ford Music": 10, "Chevans Music": 10, "Gareth Evans": 10,
    "Rock Factory": 8, "Romain CNC": 8, "Guitar Push": 8, "Easy Guitar Tabs": 12,
    "Mr. Tabs (real)": 20, "Lex Guitar Tabs ": 60,
}
BANNED = ("Mr. Tabs (impostor?)",)


def score(channel, title):
    s = ONSCREEN.get(channel, 0)
    if D.TAB_RE.search(title):
        s += 45
    if D.COVER_RE.search(title):
        s += 20
    if re.search(r"\bchords?\b", title, re.I):
        s += 12
    if re.search(r"strumming", title, re.I):
        s += 12
    if re.search(r"on.?screen|screen tab|play along", title, re.I):
        s += 10
    if re.search(r"\bsolo\b", title, re.I):
        s -= 8
    if re.search(r"riff|tone|amp|gear|pedal|interview|reaction|setup", title, re.I):
        s -= 15
    if re.search(r"fingerstyle|acoustic version", title, re.I):
        s -= 6
    return s


def main():
    data = D.load()
    h = _have.Have()
    best = {}
    for label, vids in data.items():
        if label in BANNED:
            continue
        for v in vids:
            t = v.get("t", "")
            song = match_song(t)
            if not song:
                continue
            sc = score(label, t)
            if sc <= 0:
                continue
            cur = best.get(song)
            if cur is None or sc > cur["score"]:
                best[song] = {"song": song, "channel": label, "title": t,
                              "url": v.get("url", ""), "score": sc}

    rows = []
    for song, r in sorted(best.items(), key=lambda kv: (-kv[1]["score"], kv[0])):
        already = h.match("Oasis", song)
        rows.append({**r, "have": already or ""})

    new = [r for r in rows if not r["have"]]
    print("Oasis песни общо: %d   вече ги имаме: %d   нови: %d" % (
        len(rows), len(rows) - len(new), len(new)))
    print()
    for r in rows:
        print("%-30s %-32s %4d  %s" % (r["song"][:30], r["channel"][:32], r["score"],
                                        ("ИМАМЕ: " + r["have"]) if r["have"] else "ново"))

    manifest = []
    for r in new:
        manifest.append({
            "id": r["url"].split("v=")[-1].split("&")[0],
            "artist": "Oasis",
            "song": r["song"],
            "tag": "Tabs + Chords",
            "rock": True,
            "out": "out_gz/Oasis-%s.png" % re.sub(r"[^A-Za-z0-9]+", "-", r["song"]).strip("-"),
            "url": r["url"],
            "source_channel": r["channel"],
        })
    with open(os.path.join(R, "gz_batches", "batch20.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    with open(os.path.join(R, "gz_batches", "batch20_ids.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(m["id"] for m in manifest))
    print("\nbatch20.json: %d урока" % len(manifest))
    for m in manifest:
        print("  %-14s %-30s %s" % (m["id"], m["song"][:30], m["source_channel"]))


if __name__ == "__main__":
    main()
