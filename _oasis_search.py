# -*- coding: utf-8 -*-
"""Search YouTube for tab videos of the Oasis songs that have NO source in the
measured corpus.

    py -3.14 _oasis_search.py    -> _oasis_search.md

Metadata only (no download). Uses yt-dlp ytsearch through the local PO-Token
server on 127.0.0.1:4416.
"""
import json
import os
import subprocess
import sys
import time

R = os.path.dirname(os.path.abspath(__file__))
import _oasis_songs as OS

OUT_MD = os.path.join(R, "_oasis_search.md")
OUT_JSON = os.path.join(R, "_oasis_search.json")
PER_SONG = 6


def have_sources():
    """songs that already have at least one candidate video in the corpus"""
    import csv
    import re
    W = re.compile(r"[a-z0-9]+")
    rows = list(csv.DictReader(open(os.path.join(R, "_channels_all_videos.csv"),
                                    encoding="utf-8")))
    covered = set()
    for canon in OS.OASIS_SONGS:
        key = [w for w in W.findall(canon.lower()) if len(w) > 2]
        if not key:
            continue
        for x in rows:
            t = W.findall(x["title"].lower())
            if "oasis" in t:
                if OS.match_song(x["title"]) == canon:
                    covered.add(canon)
                    break
                continue
            if all(w in t for w in key):
                covered.add(canon)
                break
    return covered


def search(song, n=PER_SONG):
    q = "Oasis %s guitar tab" % song
    cmd = [sys.executable, '-m', 'yt_dlp', '--no-warnings', '--flat-playlist',
           '--extractor-args', 'youtube:player_client=android_creator',
           '--dump-json', 'ytsearch%d:%s' % (n, q)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return []
    out = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            j = json.loads(line)
        except Exception:
            continue
        out.append({
            "id": j.get("id"),
            "title": j.get("title"),
            "channel": j.get("channel") or j.get("uploader"),
            "duration": j.get("duration"),
            "url": "https://www.youtube.com/watch?v=%s" % j.get("id"),
        })
    return out


def main():
    covered = have_sources()
    missing = [s for s in OS.OASIS_SONGS if s not in covered]
    print("songs with no corpus source: %d" % len(missing))
    results = {}
    for i, song in enumerate(missing, 1):
        hits = search(song)
        results[song] = hits
        print("[%2d/%2d] %-32s %d hits" % (i, len(missing), song[:32], len(hits)), flush=True)
        for h in hits[:3]:
            print("        %-26s %s" % ((h["channel"] or "")[:26], (h["title"] or "")[:62]))

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    out = ["# Oasis — търсене на tab видеа за песни без източник в корпуса\n",
           "Търсене през YouTube (`Oasis <песен> guitar tab`), само метаданни.\n",
           "| # | Песен | Кандидати | Канали |", "|---|---|---|---|"]
    for i, song in enumerate(missing, 1):
        hits = results.get(song) or []
        chs = sorted({h["channel"] for h in hits if h.get("channel")})
        out.append("| %d | %s | %d | %s |" % (i, song, len(hits),
                                             ", ".join(c[:20] for c in chs[:4]) or "—"))
    out.append("")
    out.append("## Кандидати\n")
    for song in missing:
        hits = results.get(song) or []
        out.append("### %s" % song)
        out.append("")
        if hits:
            out.append("| Канал | Видео | Време |")
            out.append("|---|---|---|")
            for h in hits:
                dur = h.get("duration")
                out.append("| %s | [%s](%s) | %s |" % (
                    (h.get("channel") or "")[:30], (h.get("title") or "")[:70],
                    h.get("url"), ("%ds" % dur) if dur else "—"))
        else:
            out.append("_няма резултат_")
        out.append("")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("\nwritten %s and %s" % (OUT_MD, OUT_JSON))


if __name__ == "__main__":
    main()
