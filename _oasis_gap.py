# -*- coding: utf-8 -*-
"""Find videos for the Oasis songs that have no card yet - full corpus scan.

    py -3.14 _oasis_gap.py    -> _oasis_gap.md

The earlier coverage report (_oasis_coverage.md) only looked at videos whose
title contains "Oasis" (via _oasis_songs.match_song). This script scans the
whole measured corpus (112 channels / 50 490 videos) for every canonical Oasis
song name, so songs covered by channels that do not name Oasis are not missed.
"""
import collections
import csv
import json
import os
import re

R = os.path.dirname(os.path.abspath(__file__))
import _oasis_songs as OS

W = re.compile(r"[a-z0-9]+")
STOP = {"the", "a", "of", "in", "on", "and", "it", "i", "you", "my", "me",
        "we", "to", "is", "that", "don't", "dont"}


def toks(s):
    return [w for w in W.findall((s or "").lower())]


def loose(song):
    """tokens of the song name without stopwords, for a loose containment test"""
    return [w for w in toks(song) if w not in STOP]


def main():
    cards = json.load(open(os.path.join(R, "songs.json"), encoding="utf-8"))
    have = set()
    for c in cards:
        a = (c.get("artist") or "").lower()
        if "oasis" in a:
            have.add(frozenset(toks(c.get("title", ""))))

    rows = list(csv.DictReader(open(os.path.join(R, "_channels_all_videos.csv"), encoding="utf-8")))
    print("corpus videos: %d" % len(rows))

    # songs already assigned to batch 20
    b20 = set()
    man = json.load(open(os.path.join(R, "gz_batches", "batch20.json"), encoding="utf-8"))
    items = man.values() if isinstance(man, dict) else man
    for it in items:
        if isinstance(it, dict) and it.get("song"):
            b20.add(it["song"].lower())

    # one pass: tokenize every title once
    titles = []
    for x in rows:
        t = toks(x["title"])
        titles.append((t, set(t)))

    out = ["# Oasis — видеа за песните без карта (пълен корпус)\n",
           "Търси се в **целия корпус** (112 канала / %d видеа), не само в видеата с „Oasis“ в заглавието.\n" % len(rows),
           "`Tab` = в заглавието пише tab/tabs · `Карта` = вече имаме урочна карта за тази песен.\n",
           "| # | Песен | Видеа | С tab | Канали | Карта |",
           "|---|---|---|---|---|---|"]

    gaps = []
    for i, canon in enumerate(OS.OASIS_SONGS, 1):
        key = loose(canon)
        if not key:
            continue
        hits = []
        for x, (t, ts) in zip(rows, titles):
            if "oasis" in ts:
                # video names Oasis -> use the canonical matcher
                if OS.match_song(x["title"]) == canon:
                    hits.append(x)
                continue
            # every word of the song name must be present, in order
            pos = 0
            ok = True
            for w in key:
                while pos < len(t) and t[pos] != w:
                    pos += 1
                if pos >= len(t):
                    ok = False
                    break
                pos += 1
            if ok:
                hits.append(x)
        # drop the ones we already have a card for
        done = any(set(key) <= h for h in have)
        in20 = canon.lower() in b20
        tab = [h for h in hits if "tab" in h["flags"].lower()]
        chs = sorted({h["channel"] for h in hits})
        out.append("| %d | %s | %d | %d | %s | %s |" % (
            i, canon, len(hits), len(tab),
            ", ".join(c[:18] for c in chs[:4]) or "—",
            "✅" if done else ("🎯 b20" if in20 else "—")))
        if not done and not in20:
            gaps.append((canon, len(hits), len(tab), chs,
                         [(h["channel"], h["title"], h["url"], h["flags"]) for h in tab]))

    out.append("")
    out.append("## Песни без карта — намерени видеа с tab\n")
    total = 0
    for canon, nh, nt, chs, tabs in gaps:
        out.append("### %s — %d видеа (%d с tab)" % (canon, nh, nt))
        out.append("")
        if tabs:
            out.append("| Канал | Видео | Флагове |")
            out.append("|---|---|---|")
            for ch, ti, url, fl in tabs[:12]:
                out.append("| %s | [%s](%s) | %s |" % (ch, ti.replace("|", "\\|"), url, fl))
            total += len(tabs)
            out.append("")
        else:
            out.append("_Няма видео с tab в корпуса._")
            out.append("")
    out.append("Общо намерени видеа с tab за песни без карта: **%d**" % total)

    with open(os.path.join(R, "_oasis_gap.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    print("\nПесни без карта и намерени видеа с tab:")
    for canon, nh, nt, chs, tabs in gaps:
        flag = "%2d" % nt
        print("  %-34s videos=%-3d tab=%s  %s" % (canon[:34], nh, flag,
                                                 ", ".join(c[:14] for c in chs[:3])))
    print("\nобщо tab-видеа за песни без карта: %d" % total)


if __name__ == "__main__":
    main()
