# -*- coding: utf-8 -*-
"""Oasis: unique songs + the best source video for each (prefer on-screen tab
channels over lesson-only channels, then prefer more views/clearer title)."""
import csv
import json
import os
import re

R = os.path.dirname(os.path.abspath(__file__))
import _channels_all_dump as D

STOP = re.compile(
    r"\b(guitar|bass|tab|tabs|lesson|tutorial|cover|song|chords?|strumming|play|along|"
    r"with|and|the|original|video|audio|beginners?|easy|lead|rhythm|solo|pop|punk|all|"
    r"parts|scrolling|for|to|of|version|remake|by|feat|official|channel|watch|me|how|"
    r"play|on|screen|timings?|comment|subscribe|get|is|this|what|that|my|your|we|i)\b", re.I)
BRACKET = re.compile(r"\(.*?\)|\[[^\]]*\]")

CANON = {
    "dont look back in anger": "Don't Look Back In Anger",
    "don t look back in anger": "Don't Look Back In Anger",
    "live forever": "Live Forever",
    "slide away": "Slide Away",
    "supersonic": "Supersonic",
    "wonderwall": "Wonderwall",
    "champagne supernova": "Champagne Supernova",
    "rock n roll star": "Rock 'n' Roll Star",
    "rock n roll star": "Rock 'n' Roll Star",
    "some might say": "Some Might Say",
    "whatever": "Whatever",
    "cigarettes alcohol": "Cigarettes & Alcohol",
    "half the world away": "Half The World Away",
    "she s electric": "She's Electric",
    "stand by me": "Stand By Me",
    "morning glory": "Morning Glory",
    "i hope i think i know": "I Hope, I Think, I Know",
    "d you know what i mean": "D'you Know What I Mean?",
    "lyla": "Lyla",
    "stay young": "Stay Young",
    "roll with it": "Roll With It",
    "songbird": "Songbird",
    "shakermaker": "Shakermaker",
    "masterplan": "Masterplan",
    "importance of being idle": "Importance Of Being Idle",
    "the importance of being idle": "Importance Of Being Idle",
    "dont believe the truth": "Don't Believe The Truth",
    "go let it out": "Go Let It Out",
    "the boy with the blues": "The Boy With The Blues",
    "fade away": "Fade Away",
    "let it all hang out": "Let It All Hang Out",
    "stop crying your heart out": "Stop Crying Your Heart Out",
    "my big mouth": "My Big Mouth",
    "mucky fingers": "Mucky Fingers",
    "d'You Know What I Mean": "D'you Know What I Mean?",
}

# channels whose on-screen layout carries tab/chord/strumming graphics
ONSCREEN = [
    "Lex Guitar Tabs", "guitar cover with tabs & chords", "ike", "Sparky Guitar",
    "Play Along Guitar", "CWZ Guitar", "CoverSolutions", "GuitarZero2Hero Express",
    "Marc Sanz Guitar", "Dotti Brothers", "GuitarZero2Hero", "Mike Atsushi",
    "Super Easy Bass", "Easy Guitar Tabs Tutorial", "Guitar Tab Lab",
    "Marty Music", "Let's Play All", "SAW", "Yoni Schlesinger", "christianvib",
    "Cameron Ford Music", "Chevans Music", "Gareth Evans", "Rock Factory",
    "Romain CNC", "Guitar Push", "Easy Guitar Tabs",
]


def clean_song(title):
    s = BRACKET.sub(" ", title)
    s = re.sub(r"[|:\u2013\u2014]+", " ", s)
    s = re.sub(r"'", "'", s)
    s = STOP.sub(" ", s)
    s = re.sub(r"[^A-Za-z0-9' ]+", " ", s)
    s = re.sub(r"\s{2,}", " ", s).strip().lower()
    s = re.sub(r"^\s*oasis\s+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    for k, v in CANON.items():
        if s.startswith(k):
            return v
    if "top" in s and "riff" in s:
        return "(Top 10 riffs)"
    words = s.split()
    return " ".join(words[:3]).title()


def score(channel, title, has_tab):
    s = 0
    if has_tab:
        s += 100
    if channel in ONSCREEN:
        s += 50
    for pref, w in [("Lex Guitar Tabs", 20), ("guitar cover with tabs", 18),
                    ("Sparky Guitar", 16), ("ike", 14), ("CWZ Guitar", 12),
                    ("Play Along Guitar", 10), ("CoverSolutions", 8),
                    ("GuitarZero2Hero Express", 30), ("GuitarZero2Hero", 28)]:
        if channel.startswith(pref):
            s += w
    if re.search(r"\bchords?\b", title, re.I):
        s += 6
    if re.search(r"strumming", title, re.I):
        s += 6
    if re.search(r"solo", title, re.I):
        s -= 3
    return s


def main():
    data = D.load()
    have = set()
    import _have
    h = _have.Have()

    best = {}
    rows = []
    for label, vids in data.items():
        for v in vids:
            t = v.get("t", "")
            if not re.search(r"\boasis\b", t, re.I):
                continue
            if not D.TAB_RE.search(t):
                continue
            song = clean_song(t)
            sc = score(label, t, True)
            already = h.match("Oasis", song)
            rec = {"channel": label, "title": t, "url": v.get("url", ""),
                   "song": song, "score": sc, "have": already or ""}
            rows.append(rec)
            if song not in best or sc > best[song]["score"]:
                best[song] = rec

    order = sorted(best.values(), key=lambda r: -r["score"])
    with open(os.path.join(R, "_oasis_unique.json"), "w", encoding="utf-8") as f:
        json.dump(order, f, ensure_ascii=False, indent=1)

    print("Oasis tab видеа: %d   уникални песни: %d   вече ги имаме: %d" % (
        len(rows), len(order), sum(1 for r in order if r["have"])))
    print()
    print("%-28s %-30s %5s %s" % ("Песен", "Канал", "score", "вече имаме"))
    for r in order:
        print("%-28s %-30s %5d %s" % (r["song"][:28], r["channel"][:30], r["score"],
                                      r["have"] or "—"))


if __name__ == "__main__":
    main()
