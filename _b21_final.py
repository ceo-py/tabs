# -*- coding: utf-8 -*-
"""Resolve the YouTube channel id of each batch-21 video (needed by
site_build.py CHANNEL_URLS) and write the hand-picked manifest.

    py -3.14 _b21_final.py
"""
import json
import os
import re
import subprocess
import sys

R = os.path.dirname(os.path.abspath(__file__))

# hand-picked: the best tab candidate per song, after reading all search hits
PICKS = [
    # song, artist, channel (as shown on YouTube), video id
    ("Acquiesce", "Oasis", "G.S.N. Tabs", "oE6uuH-eKHI"),
    ("Digsy's Dinner", "Oasis", "G.S.N. Tabs", "ILwkE8olT7I"),
    ("The Hindu Times", "Oasis", "Behnam Guitar Tabs", "GwSh_jC4xqY"),
    ("Who Feels Love?", "Oasis", "Wayne R Guitar", "zYP0Npys8s4"),
    ("Love Like A Bomb", "Oasis", "Fretboard Fundamentals", "7Fc5KPnarJo"),
    ("Instant Karma", "John Lennon", "Top Guitar Players", "2lc9NwgCwmA"),
]


def slug(song):
    return "Oasis-%s" % re.sub(r"[^A-Za-z0-9]+", "-", song).strip("-")


def probe(vid):
    cmd = [sys.executable, '-m', 'yt_dlp', '--no-warnings', '--skip-download',
           '--extractor-args', 'youtube:player_client=android_creator',
           '--print', '%(title)s\t%(channel)s\t%(channel_id)s\t%(uploader_id)s\t%(duration)s',
           'https://www.youtube.com/watch?v=' + vid]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                       encoding="utf-8", errors="replace")
    out = (r.stdout or "").strip().splitlines()
    if not out:
        return None
    p = out[0].split("\t")
    while len(p) < 5:
        p.append("")
    return {"title": p[0], "channel": p[1].strip(), "channel_id": p[2].strip(),
            "uploader_id": p[3].strip(), "duration": p[4]}


def main():
    rows = []
    chans = {}
    for song, artist, chan, vid in PICKS:
        info = probe(vid)
        if not info:
            print("  FAIL %s (%s)" % (song, vid))
            continue
        cid = info["channel_id"] or info["uploader_id"]
        chans[info["channel"]] = cid
        print("  %-20s %-26s %-22s %s" % (song[:20], info["channel"][:26],
                                         cid, info["title"][:44]))
        rows.append({
            "id": vid,
            "artist": artist,
            "song": song,
            "tag": "Tabs + Chords",
            "rock": True,
            "out": "out_gz/%s.png" % slug(song),
            "url": "https://www.youtube.com/watch?v=%s" % vid,
            "source_channel": info["channel"],
            "channel_id": cid,
            "score": 65,
        })

    with open(os.path.join(R, "gz_batches", "batch21.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    with open(os.path.join(R, "gz_batches", "batch21_ids.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(r["id"] for r in rows) + "\n")
    with open(os.path.join(R, "_b21_channels.json"), "w", encoding="utf-8") as f:
        json.dump(chans, f, ensure_ascii=False, indent=1)
    print("\nbatch21: %d lessons" % len(rows))
    print("channels: %s" % json.dumps(chans, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
