# -*- coding: utf-8 -*-
"""Full video dump for every measured tab channel.

Outputs
  _channels_all_videos.md   -> human readable, one section per channel, every video
  _channels_all_videos.csv  -> same data, one row per video (filterable)

Row fields: #, title, url, TAB / ROCK / GRUNGE / BASS / genre flags
"""
import csv
import json
import os
import re

R = os.path.dirname(os.path.abspath(__file__))

GENRES = {
    "grunge": r"nirvana|pearl jam|soundgarden|alice in chains|stone temple pilots|mudhoney|"
              r"screaming trees|melvins|dinosaur jr|sebadoh|hokum|mad season|the fray|"
              r"\bhole\b|garbage|veruca salt|malice n forgery|grunge|temple of the dog|chavez",
    "punk": r"ramones|bad religion|misfits|sex pistols|descendents|rancid|green day|nofx|"
            r"dead kennedys|germs|the clash|the damned|social distortion|dropkick murphys|"
            r"offspring|lagwagon|anti-flag|minor threat|dillinger four|teenage bottlerocket|"
            r"mxpx|toxic reason|punk",
    "metal": r"metallica|iron maiden|black sabbath|slayer|megadeth|slipknot|pantera|"
             r"system of a down|korn|deftones|\btool\b|disturbed|motorhead|motörhead|rammstein|"
             r"\bghost\b|sepultura|anthrax|testament|exodus|judas priest|led zeppelin|"
             r"\bdio\b|motley crue|gun n roses|guns n roses|def leppard|scorpions|van halen|"
             r"whitesnake|aerosmith|bon jovi|avenged sevenfold|arch enemy|children of bodom|"
             r"kiss\b|accept|dokken|ratt\b|ozzy|racer x|king diamond|dream theater|"
             r"marilyn manson|lindemann|limp bizkit|rob zombie|emigrate|chevelle|hatebreed|"
             r"emily aftershock|as i lay dying|bullet for my valentine|him\b|"
             r"the warning|billy talent|korn|nine inch nails|queens of the stone age",
    "classic": r"queen|pink floyd|ac/dc|journey|foreigner|boston|deep purple|\brush\b|"
               r"\bheart\b|cheap trick|blue oyster cult|eagles\b|lynyrd skynyrd|zz top|styx|"
               r"kansas|joe satriani|steve vai|dire straits|thin lizzy|the doors|the cult|"
               r"stevie ray vaughan|jimi hendrix|gary moore|joe bonamassa|rush\b|"
               r"van halen|aerosmith|bon jovi|motley crue|creed|third eye down",
    "alt": r"radiohead|smashing pumpkins|foo fighters|oasis|\bblur\b|\bbeck\b|weezer|"
           r"blink-?182|sum 41|the cranberries|counting crows|third eye blind|gin blossoms|"
           r"sister hazel|\bbush\b|travis\b|keane|coldplay|the killers|arctic monkeys|"
           r"kaiser chiefs|the strokes|white stripes|royal blood|simple plan|silverchair|"
           r"incubus|a perfect circle|nine inch nails|\bmuse\b|linkin park|"
           r"red hot chili peppers|\brhcp\b|the smiths|depeche mode|tame impala|"
           r"pearl jam|soundgarden|alice in chains|stone temple pilots|nirvana",
    "posthc": r"\bafi\b|thrice|coheed|brand new|taking back sunday|senses fail|"
              r"\bfinch\b|underoath|chiodos|saosin|emery|carcass|the used|glass jaw|"
              r"deadstar|pj harvey|barrington mills",
    "pop": r"michael jackson|bruno mars|madonna|taylor swift|ed sheeran|adele|beyonce|"
           r"katy perry|rihanna|dua lipa|doja cat|stray kids|\bbts\b|bocchi|genshin|"
           r"zelda|nintendo|final fantasy|mario|ocarina|assassin|elden|yorushika|"
           r"specialz|zutomayo|king gnu|lilac|buwan",
}
GEN_RE = {k: re.compile(v, re.I) for k, v in GENRES.items()}
TAB_RE = re.compile(r"\btab", re.I)
BASS_RE = re.compile(r"\bbass\b", re.I)
COVER_RE = re.compile(r"cover|lesson|tutorial|play ?along|how to play|walkthrough", re.I)

# order used in the report
PRIMARY = [
    "DadRock TABS", "Schmuck's Punk Tabs", "CWZ Guitar", "CoverSolutions",
    "Dotti Brothers", "Nikola Gugoski", "Steven Perrone", "GuitarForce.Com",
    "Godderdy Tabs", "guitar cover with tabs & chords",
]


def load():
    data = {}
    for f in ("_verify_channels.json", "_verify_new2.json"):
        p = os.path.join(R, f)
        if not os.path.exists(p):
            continue
        for val in json.load(open(p, encoding="utf-8")).values():
            lbl = val.get("label")
            vids = val.get("videos") or []
            if lbl and vids:
                data.setdefault(lbl, vids)
    return data


def flags(title):
    t = title or ""
    fl = []
    if TAB_RE.search(t):
        fl.append("TAB")
    for g, rx in GEN_RE.items():
        if rx.search(t):
            fl.append(g.upper())
    if BASS_RE.search(t):
        fl.append("BASS")
    if COVER_RE.search(t):
        fl.append("COVER")
    return fl


def main():
    data = load()
    rows = []
    md = ["# TABS 90 research — full video lists per channel", "",
          "All videos from the `/videos` tab of each channel, as measured on 2026-11-18.",
          "Flags: TAB = title mentions tab(s) · COVER = cover/lesson/tutorial/play-along ·",
          "GRUNGE / PUNK / METAL / CLASSIC / ALT / POSTHC / POP = genre detected from the artist ·",
          "BASS = title mentions bass.", ""]

    order = PRIMARY + [k for k in sorted(data, key=lambda x: -len(data[x])) if k not in PRIMARY]
    for label in order:
        vids = data.get(label) or []
        if not vids:
            continue
        tabc = sum(1 for v in vids if TAB_RE.search(v.get("t", "")))
        md.append("## %s — %d видеа (%d с tab)" % (label, len(vids), tabc))
        md.append("")
        md.append("| # | Видео | Флагове |")
        md.append("|---|---|---|")
        for i, v in enumerate(vids, 1):
            t = re.sub(r"\s+", " ", v.get("t", "")).strip()
            fl = flags(t)
            md.append("| %d | [%s](%s) | %s |" % (i, t.replace("|", "\\|"), v.get("url", ""), " ".join(fl)))
            rows.append([label, i, t, v.get("url", ""), " ".join(fl)])
        md.append("")

    with open(os.path.join(R, "_channels_all_videos.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(os.path.join(R, "_channels_all_videos.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["channel", "n", "title", "url", "flags"])
        w.writerows(rows)

    print("channels: %d   videos: %d" % (len(order), len(rows)))
    print()
    print("%-34s %7s %7s %7s %7s %8s" % ("channel", "total", "TAB", "COVER", "BASS", "genres"))
    for label in order:
        vids = data.get(label) or []
        tab = sum(1 for v in vids if TAB_RE.search(v.get("t", "")))
        cov = sum(1 for v in vids if COVER_RE.search(v.get("t", "")))
        bas = sum(1 for v in vids if BASS_RE.search(v.get("t", "")))
        gr = collections_counter(vids)
        print("%-34s %7d %7d %7d %7d %8s" % (label[:34], len(vids), tab, cov, bas, gr))
    print()
    print("written: _channels_all_videos.md  /  _channels_all_videos.csv")


def collections_counter(vids):
    import collections
    c = collections.Counter()
    for v in vids:
        for g in GENRES:
            if GEN_RE[g].search(v.get("t", "")):
                c[g] += 1
    return ",".join("%s:%d" % (k[:4], c[k]) for k in ("grunge", "punk", "metal", "classic", "alt"))


if __name__ == "__main__":
    main()
