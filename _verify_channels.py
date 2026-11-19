# -*- coding: utf-8 -*-
"""INDEPENDENT verification of top YouTube tab channels for TABS 90.

Deliberately does NOT reuse the regexes from _yt_final.py / _yt_extra.py:
uses its own tab detection, its own "real rock artist" list (no generic
word 'rock') and its own word-bounded grunge list.

Writes _verify_channels.json (metrics + every tab title/url per channel).
"""
import json
import os
import re
import sys
import time
import unicodedata

import yt_dlp

OPTS = {
    "quiet": True,
    "skip_download": True,
    "extract_flat": True,
    "no_warnings": True,
    "ignoreerrors": True,
    "socket_timeout": 60,
    "extractor_args": {"youtube": {"player_client": ["web"]}},
}

# ---------------------------------------------------------------- normalise
def norm(s):
    if not s:
        return ""
    out = []
    for ch in unicodedata.normalize("NFKC", s):
        cp = ord(ch)
        if 0x1D400 <= cp <= 0x1D7FF:
            out.append(chr(cp - 0x1D400 + 65))
        elif 0x1D7CE <= cp <= 0x1D7FF:
            out.append(chr(cp - 0x1D7CE + 48))
        elif 0x1F130 <= cp <= 0x1F189:
            out.append(chr(cp - 0x1F130 + 65))
        else:
            out.append(ch)
    return unicodedata.normalize("NFKC", "".join(out)).lower()


# ---------------------------------------------------------------- tab words
# My own list of "this video shows a tab" markers.
TAB_WORDS = [
    "tab", "tabs", "tabbing", "tabbed", "tablature",
]
TAB_RE = re.compile(
    r"\btabs?\b|\btabbing\b|\btabbed\b|\btablature\b|"
    r"tabs?\s*\+|\+\s*tabs?\b|on.?screen tabs?|screen tabs?|with tabs?\b|"
    r"tabs? in (the )?video|tab in descri|\bt\s*\|\s*\w|with guitar tab"
)

COVER_RE = re.compile(
    r"(cover|playthrough|play through|lesson|tutorial|play\s?along|demonstration|"
    r"performance|song lesson|riff|how to play|session|jam)"
)

# ---------------------------------------------------------------- rock artists
# Real rock / grunge / metal / alt / punk ACTS (no generic 'rock' word).
ROCK_ACT = re.compile(
    r"nirvana|pearl jam|soundgarden|alice in chains|stone temple pilots|"
    r"led zeppelin|led zep|queen|david bowie|the doors|doors\b|red hot chili peppers|"
    r"r\.?\s?e\.?\s?m\.?\b|\bfoo fighters\b|\bgreen day\b|blink-?182|sum 41|simple plan|"
    r"offspring|slipknot|metallica|iron maiden|black sabbath|ac/?dc|"
    r"motley crue|gun n.? roses|aerosmith|bon jovi|def leppard|scorpions|"
    r"whitesnake|van halen|oasis\b|blur\b|pulp\b|travis\b|keane|coldplay|"
    r"lana del rey|the killers|arctic monkeys|kaiser chiefs|the strokes|"
    r"white stripes|royal blood|smashing pumpkins|radiohead|fleetwood mac|"
    r"eagles\b|creed\b|third eye blind|matchbox twenty|staind|incubus|"
    r"goo goo dolls|silverchair|korn\b|deftones|rage against the machine|"
    r"system of a down|audioslave|disturbed|evanescence|seether|nickelback|"
    r"theory of a deadman|smash mouth|golden earring|twisted sister|"
    r"bad religion|ramones|descendents|misfits|sex pistols|the damned|"
    r"cheap trick|husker du|the dandy Warhols|rancid|social distortion|"
    r"motörhead|motorhead|zz top|zeppelin|aerosmith|jimi hendrix|"
    r"hendrix|creedence|lynyrd skynyrd|skynyrd|deep purple|deep purple|"
    r"ruthling|alice cooper|kiss\b|van halen|scorpions|dio\b|manowar|"
    r"accept\b|pantera|sepultura|gojira|slayer|anthrax|megadeth|"
    r"motorhead|judas priest|alice in chains|dot eleven|massive attack|"
    r"rage against|tool\b|system of|korn|deftones|limp bizkit|kid rock|"
    r"earthmuzik|devin townsend|bring me the horizon|bullet for my valentine|"
    r"afi\b|as i lay dying|underoath|nickelback|bullet|architects\b|"
    r"bad wolves|halestorm|black stone cherry|mastodon\b|"
    r"godsmack|papa roach|three days grace|rob zombie|"
    r"nine inch nails|nine inch|nINe|"
    r"the offspring|bad religion|descendents|husker du|the exploited|"
    r"sex pistols|ramones|misfits|dead kennedys|t.s.o.l|rancid|"
    r"social distortion|strung out|lagwagon|guttermouth|"
    r"third eye blind|new found glory|good charlotte|"
    r"nivea\b|yellowcard|all time low|"
    r"the cranberries|duran duran|depeche mode|the cure|"
    r"joy division|new order|siouxsie|bauhaus|"
    r"the smashing pumpkins|smashing pumpkins|"
    r"pixies|sonic youth|nine inch nails|"
    r"muse\b|placebo\b|skunk anansie|garbage\b|"
    r"the offspring|korn|tool\b|a perfect circle|"
    r"the police\b|eros rothford|bon jovi|"
    r"aerosmith|van halen|reo speedwagon|"
    r"creed\b|alice in chains|stone temple pilots|soundgarden|"
    r"superfood|menswear|"
    r"the darkness|def leppard|motley crue|"
    r"pixies|the vibes|"
    r"malice n forgery|david gedge|the fray|"
    r"the cranberries|garbage|veruca salt|mary go round|"
    r"oasis|noel gallagher|"
    r"the gaslight anthem|stereophonics|"
    r"arctic monkeys|kaiser chiefs|franz ferdinand|"
    r"the verve|ocean colour scene|"
    r"supergrass|travis|keane|dodgy|"
    r"the killers|ocean colour|"
    r"the fratellis|"
    r"the darkness|motley crue|"
    r"the jimi hendrix|"
    r"superheavy|"
    r"the white stripes|the strokes|the fratellis|"
    r"queens of the stone age|"
    r"deftones|limp bizkit|"
    r"escape the fate|"
    r"nothing more|"
    r"bad religion|"
    r"blur\b|pulp\b|"
    r"the verve|"
    r"the doors|jimi hendrix|"
    r"rhcp|red hot chili|"
    r"twin peaks"
)

# Generic style words (used only for the LOOSE metric, to compare with prior work)
GENRE_WORD_RE = re.compile(
    r"\brock\b|\bmetal\b|\bpunk\b|\bgrunge\b|alternative rock|alt rock|"
    r"indie rock|hard rock|classic rock|\brock'n'?roll\b|\brock and roll\b"
)

# 90s grunge acts, word-bounded to avoid matching 'hole' inside 'whole'
GRUNGE_ACT = re.compile(
    r"\bnirvana\b|\bpearl jam\b|\bsoundgarden\b|\balice in chains\b|"
    r"\bstone temple pilots\b|\bstp\b|\bmudhoney\b|\bscreaming trees\b|"
    r"\bmelvins\b|\bdinosaur jr\b|\bhokum\b|\bmad season\b|\bthe fray\b|"
    r"\bgrunge\b|\bthe hole\b|\bhole\b(?!\s*\w)|\(?hole\)?\b|\bgarbage\b|"
    r"\bveruca salt\b|\bmary go round\b|\bmalice n forgery\b|\bdavid gedge\b|"
    r"\bsmashing pumpkins\b|\b911\b|\btadpole\b|\b7 year bitch\b|"
    r"\bbush\b(?!\s*a)| Candlebox|\bcandlebox\b|\bcandle\b|"
    r"\bsponge\b|\bflotsam\b|\bno doubt\b|\bthird eye blind\b|"
    r"\bspin Doctors\b|\bharvey danger\b|\bcherry poppin\b|\bjawbreaker\b"
)

CHANNELS = [
    ("CWZ Guitar", "https://www.youtube.com/channel/UCSzJagetA7eVNc7ZQwXJVHg/videos"),
    ("Schmuck's Punk Tabs", "https://www.youtube.com/channel/UCMFdBBF_dcamKYeYqHYe71g/videos"),
    ("CoverSolutions", "https://www.youtube.com/channel/UCUXTxsU23H02fewbRzHXBgQ/videos"),
    ("Dotti Brothers", "https://www.youtube.com/channel/UCq5nkfMiOkek7s9j6c_Ao6g/videos"),
    ("Nikola Gugoski", "https://www.youtube.com/channel/UCLdCUDlzx4qmwVlyVfUHxdg/videos"),
    ("guitar cover with tabs & chords", "https://www.youtube.com/channel/UCeWHmkuMBM760nryL8wLfLg/videos"),
    ("Steven Perrone", "https://www.youtube.com/channel/UCqCAOEhhW6scLqcjbWKlspA/videos"),
    ("Godderdy Tabs", "https://www.youtube.com/channel/UCLFZo57n3HpYw7o2Zkf6QJA/videos"),
    ("Matt Ten", "https://www.youtube.com/channel/UCciUBcG_bT-SOIS28FNY9-w/videos"),
    ("Mr. Tabs (real)", "https://www.youtube.com/@Mr.Tabs.Guitar.Lessons/videos"),
    ("GuitarZero2Hero Express", "https://www.youtube.com/channel/UC57CDvpwqAxHrJvVkZbaBxA/videos"),
    ("Lex Guitar Tabs", "https://www.youtube.com/channel/UCN4wqAJ7UYPnVRGKshckZJQ/videos"),
    ("TAB 'EM ALL", "https://www.youtube.com/channel/UCrhU8Q7KgBuBme-0ggZeaUg/videos"),
    ("Sightline Guitar", "https://www.youtube.com/channel/UCkD0Qa33bTk-Qd9mxHc7Anw/videos"),
    ("GuitarZero2Hero", "https://www.youtube.com/channel/UCasFZzbM8JJ6dqSVEgL9VVg/videos"),
    ("Rockin Tabs", "https://www.youtube.com/channel/UCWPEi8ikVnAIu9h2XF8YrrA/videos"),
    ("Sparky Guitar", "https://www.youtube.com/channel/UCR8OM6seRnlh6bvZinGyyjA/videos"),
    ("De Gaspari Guitar", "https://www.youtube.com/channel/UCih2ClZ39b4JGUNclD0Gc8Q/videos"),
    ("East Village Guitar Method", "https://www.youtube.com/channel/UCwsWbyUgY6C_HLmxbGj3oWw/videos"),
    ("Mr. Tabs (impostor?)", "https://www.youtube.com/channel/UCuLS9OV2fZfCnO_bEmodzHw/videos"),
]


def classify(title):
    n = norm(title)
    is_tab = bool(TAB_RE.search(n))
    rock_act = bool(ROCK_ACT.search(n))
    genre = bool(GENRE_WORD_RE.search(n))
    grunge = bool(GRUNGE_ACT.search(n))
    cover = bool(COVER_RE.search(n))
    return is_tab, rock_act, genre, grunge, cover


def enum(url):
    t0 = time.time()
    with yt_dlp.YoutubeDL(OPTS) as y:
        info = y.extract_info(url, download=False)
    entries = [e for e in (info.get("entries") or []) if e]
    recs = []
    for e in entries:
        t = e.get("title") or ""
        is_tab, rock_act, genre, grunge, cover = classify(t)
        recs.append({
            "t": t,
            "url": e.get("url"),
            "id": e.get("id"),
            "tab": is_tab,
            "rock_act": rock_act,
            "genre": genre,
            "grunge": grunge,
            "cover": cover,
        })
    tabs = [r for r in recs if r["tab"]]
    return {
        "channel": info.get("channel"),
        "channel_id": info.get("channel_id"),
        "uploader_id": info.get("uploader_id"),
        "channel_url": info.get("channel_url"),
        "subs": info.get("channel_follower_count"),
        "total": len(recs),
        "tabs": len(tabs),
        "rock_act": sum(1 for r in tabs if r["rock_act"]),
        "rock_loose": sum(1 for r in tabs if r["rock_act"] or r["genre"]),
        "grunge": sum(1 for r in tabs if r["grunge"]),
        "style": sum(1 for r in tabs if r["cover"]),
        "elapsed": round(time.time() - t0, 1),
        "videos": recs,
    }


def main():
    only = sys.argv[1:] or None
    out = {}
    if os.path.exists("_verify_channels.json"):
        with open("_verify_channels.json", encoding="utf-8") as fh:
            out = json.load(fh)
    for label, url in CHANNELS:
        if only and label not in only:
            continue
        if label in out:
            print("SKIP %s" % label, flush=True)
            continue
        try:
            r = enum(url)
        except Exception as exc:  # noqa: BLE001
            print("FAIL %s %s" % (label, exc), file=sys.stderr, flush=True)
            continue
        r["label"] = label
        out[label] = r
        print("%-30s name=%-28s cid=%-26s handle=%-30s subs=%-9s total=%-5s tabs=%-5s rock_act=%-5s rock_loose=%-5s grunge=%-4s style=%-5s %ss"
              % (label[:30], str(r["channel"])[:28], str(r["channel_id"]), str(r["uploader_id"]),
                 r["subs"], r["total"], r["tabs"], r["rock_act"], r["rock_loose"], r["grunge"],
                 r["style"], r["elapsed"]), flush=True)
        with open("_verify_channels.json", "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        time.sleep(2)
    print("\n=== VERIFIED RANK (rock_act) ===", flush=True)
    rows = sorted(out.values(), key=lambda d: -d["rock_act"])
    for i, d in enumerate(rows, 1):
        print("%2d. %-30s rock_act=%-4s loose=%-4s grunge=%-4s tabs=%-5s style=%-5s total=%-5s subs=%s"
              % (i, d["label"][:30], d["rock_act"], d["rock_loose"], d["grunge"],
                 d["tabs"], d["style"], d["total"], d["subs"]), flush=True)


if __name__ == "__main__":
    main()
