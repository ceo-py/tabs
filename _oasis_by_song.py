# -*- coding: utf-8 -*-
"""Oasis: per-song breakdown across all channels."""
import collections
import csv
import os
import re

R = os.path.dirname(os.path.abspath(__file__))

STOP = re.compile(
    r"\b(guitar|bass|tab|tabs|lesson|tutorial|cover|song|chords?|strumming|play|along|"
    r"with|and|the|original|video|audio|beginners?|easy|lead|rhythm|solo|pop|punk|all|"
    r"parts|scrolling|for|to|of|version|remake|by|feat)\b", re.I)
BRACKET = re.compile(r"\(.*?\)|\[[^\]]*\]")


def song(title):
    s = BRACKET.sub(" ", title)
    s = re.sub(r"[|:\u2013\u2014-]+", " ", s)
    s = STOP.sub(" ", s)
    s = re.sub(r"\s{2,}", " ", s).strip()
    words = [w for w in s.split() if w.lower() != "oasis"]
    return " ".join(words[:4]).strip()


def main():
    rows = list(csv.DictReader(open(os.path.join(R, "_oasis_videos.csv"), encoding="utf-8")))
    per = collections.defaultdict(collections.Counter)
    tabs = collections.defaultdict(collections.Counter)
    for x in rows:
        s = song(x["title"]) or "(друго)"
        per[s][x["channel"]] += 1
        if x["has_tab"] == "да":
            tabs[s][x["channel"]] += 1

    out = ["# Oasis — разбивка по песен\n",
           "| Песен | Видеа | С tab | Канали |", "|---|---|---|---|"]
    print("%-34s %5s %5s  %s" % ("Песен", "общо", "tab", "канали"))
    print("-" * 112)
    for s in sorted(per, key=lambda k: (-sum(tabs[k].values()), -sum(per[k].values()))):
        tot, tt = sum(per[s].values()), sum(tabs[s].values())
        chs = ", ".join("%s(%d)" % (c[:16], n) for c, n in per[s].most_common(4))
        print("%-34s %5d %5d  %s" % (s[:34], tot, tt, chs))
        out.append("| %s | %d | %d | %s |" % (s, tot, tt, chs))
    with open(os.path.join(R, "_oasis_by_song.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("\nunique songs: %d" % len(per))


if __name__ == "__main__":
    main()
