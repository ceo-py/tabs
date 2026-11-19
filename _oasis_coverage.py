# -*- coding: utf-8 -*-
"""Oasis coverage report: what we have a card for, and what is still missing.

    py -3.14 _oasis_coverage.py    -> _oasis_coverage.md

Sources
  _oasis_songs.py      canonical list of 57 Oasis songs
  songs.json           our published cards (source of truth)
  _oasis_videos.csv    every Oasis video found in the research corpus
"""
import collections
import csv
import json
import os
import re

R = os.path.dirname(os.path.abspath(__file__))
import _oasis_songs as OS

W = re.compile(r"[a-z0-9]+")


def toks(s):
    return W.findall((s or "").lower())


def main():
    cards = json.load(open(os.path.join(R, "songs.json"), encoding="utf-8"))
    have = {}
    for c in cards:
        a = (c.get("artist") or "").lower()
        if "oasis" not in a:
            continue
        have[c.get("title", "")] = c

    # a few Oasis songs are covered by other performers (Oasis covered them
    # too) - the lesson card is credited to the original artist
    for c in cards:
        t = c.get("title", "")
        for canon, artist in OS.CROSS_ARTIST_CARDS.items():
            if (c.get("artist") or "") == artist and toks(canon) == toks(t):
                have.setdefault(t, c)

    # canonical song -> our card title
    card_by_song = {}
    for canon in OS.OASIS_SONGS:
        ct = toks(canon)
        for title, c in have.items():
            tt = toks(title)
            if ct and set(ct) <= set(tt):
                card_by_song.setdefault(canon, title)
                break

    rows = list(csv.DictReader(open(os.path.join(R, "_oasis_videos.csv"), encoding="utf-8")))
    per = collections.defaultdict(list)
    for x in rows:
        s = OS.match_song(x["title"])
        if s:
            per[s].append(x)

    out = ["# Oasis — покритие\n",
           "`Карта` = вече имаме урочна карта за тази песен ·",
           "`Видеа` = колко видеа за песента се намират в корпуса ·",
           "`Tab` = колко от тях имат tab в заглавието.\n",
           "| # | Песен | Карта | Видеа | Tab | Канали |",
           "|---|---|---|---|---|---|"]

    have_n = 0
    miss = []
    for i, canon in enumerate(OS.OASIS_SONGS, 1):
        vids = per.get(canon, [])
        tab = [v for v in vids if v.get("has_tab") == "да"]
        chs = sorted({v["channel"] for v in vids})
        card = card_by_song.get(canon)
        if card:
            have_n += 1
            mark = "✅"
        else:
            mark = "—"
            miss.append((canon, len(vids), len(tab), chs))
        out.append("| %d | %s | %s | %d | %d | %s |" % (
            i, canon, mark, len(vids), len(tab), ", ".join(ch[:18] for ch in chs[:4]) or "—"))

    out.append("")
    out.append("## Обобщение\n")
    out.append("- канонични Oasis песни: **%d**" % len(OS.OASIS_SONGS))
    out.append("- с готова карта: **%d**" % have_n)
    out.append("- остават: **%d**" % (len(OS.OASIS_SONGS) - have_n))
    out.append("- Oasis видеа в корпуса: **%d** (с tab: %d)" % (
        len(rows), sum(1 for x in rows if x.get("has_tab") == "да")))

    if miss:
        out.append("")
        out.append("## Остават без карта\n")
        out.append("| Песен | Видеа в корпуса | С tab | Канали |")
        out.append("|---|---|---|---|")
        for canon, nv, nt, chs in miss:
            out.append("| %s | %d | %d | %s |" % (
                canon, nv, nt, ", ".join(c[:18] for c in chs[:4]) or "—"))

    with open(os.path.join(R, "_oasis_coverage.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("_oasis_coverage.md written")
    print("songs: %d   with card: %d   missing: %d" % (
        len(OS.OASIS_SONGS), have_n, len(OS.OASIS_SONGS) - have_n))
    print()
    for canon, nv, nt, chs in miss:
        print("  %-32s videos=%-3d tab=%-3d %s" % (canon[:32], nv, nt,
                                                   ", ".join(c[:16] for c in chs[:3])))


if __name__ == "__main__":
    main()
