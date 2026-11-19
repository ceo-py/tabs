# -*- coding: utf-8 -*-
"""For each of the top-10 channels: pick 10 representative on-screen-tab cover
videos and lay them out 5 per row. Output: _top10_samples.md
"""
import json
import os
import re

R = os.path.dirname(os.path.abspath(__file__))

TOP = [
    ("DadRock TABS", "@DadRockYTOfficial", "Metal / hard rock + classic rock, 89% with bass too"),
    ("Schmuck's Punk Tabs", "@PunkRockGuitarTabs", "Punk / hardcore pure play"),
    ("CWZ Guitar", "@CWZGuitar", "Broad rock catalogue, most grunge among the big ones"),
    ("CoverSolutions", "@CoverSolutions", "Bass play-along, heavy 90s rock"),
    ("Dotti Brothers", "@dottibrothers", "Japanese-format rock covers"),
    ("Nikola Gugoski", "@nikolagugoski", "Alt / grunge / metal lessons"),
    ("Steven Perrone", "@StevenPerrone", "Nu-metal / alt metal covers"),
    ("GuitarForce.Com", "@GuitarForceCom", "Blues-rock + metal, Hendrix school"),
    ("Godderdy Tabs", "@GodderdyTabs", "Metal / metalcore + 51% bass"),
    ("guitar cover with tabs & chords", "@guitarcoverwithtab", "Japanese rock/pop covers"),
]

ROCK = re.compile(
    r"nirvana|pearl jam|soundgarden|alice in chains|stone temple pilots|mudhoney|"
    r"screaming trees|melvins|dinosaur jr|sebadoh|mad season|the fray|hole|garbage|"
    r"veruca salt|grunge|temple of the dog|chavez|"
    r"ramones|bad religion|misfits|sex pistols|descendents|rancid|green day|nofx|"
    r"dead kennedys|germs|the clash|the damned|social distortion|dropkick murphys|offspring|"
    r"metallica|iron maiden|black sabbath|slayer|megadeth|slipknot|pantera|"
    r"system of a down|korn|deftones|tool\b|disturbed|motorhead|rammstein|ghost\b|"
    r"sepultura|anthrax|testament|exodus|judas priest|led zeppelin|dio\b|motley crue|"
    r"gun n roses|guns n roses|def leppard|scorpions|van halen|whitesnake|aerosmith|bon jovi|"
    r"queen|pink floyd|ac/dc|journey|foreigner|boston|deep purple|rush\b|heart\b|"
    r"cheap trick|blue oyster cult|eagles\b|lynyrd skynyrd|zz top|styx|kansas|"
    r"joe satriani|steve vai|dire straits|thin lizzy|kiss\b|accept|dokken|ratt\b|"
    r"ozzy|racer x|king diamond|stevie ray vaughan|the cult|the doors|dream theater|"
    r"tesla|slash\b|jimi hendrix|gary moore|joe bonamassa|"
    r"radiohead|smashing pumpkins|foo fighters|oasis|blur\b|beck\b|weezer|blink-?182|"
    r"sum 41|the cranberries|counting crows|third eye blind|gin blossoms|sister hazel|"
    r"bush\b|travis\b|keane|coldplay|the killers|arctic monkeys|kaiser chiefs|"
    r"the strokes|white stripes|royal blood|simple plan|silverchair|incubus|"
    r"a perfect circle|nine inch nails|muse\b|linkin park|limp bizkit|marilyn manson|"
    r"avenged sevenfold|arch enemy|children of bodom|red hot chili peppers|rhcp\b|"
    r"the smiths|depeche mode|tame impala|the warning|billy talent|"
    r"misfits|korn|rob zombie|emigrate|chevelle|hatebreed|"
    r"zz top|stone temple|rage against|soundgarden|nine inch",
    re.I,
)

TABRE = re.compile(r"\btab", re.I)
COVERRE = re.compile(r"cover|lesson|tutorial|play ?along|how to play", re.I)


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


def pick(vids, n=10):
    tab = [v for v in vids if TABRE.search(v.get("t", ""))]
    rock = [v for v in tab if ROCK.search(v.get("t", ""))]
    pool = rock or tab
    cov = [v for v in pool if COVERRE.search(v.get("t", ""))]
    pool = cov or pool
    if len(pool) <= n:
        return pool
    step = len(pool) / float(n)
    return [pool[int(i * step)] for i in range(n)]


def short(t, n=58):
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\bGuitar Lesson\b|\bGuitar Tabs?\b|\bTutorial\b|\bwith TABS\b|"
               r"\bPlay Along Tabs In Video\b|\bTabs\b", "", t, flags=re.I)
    t = re.sub(r"\s{2,}", " ", t).strip(" -|")
    return t if len(t) <= n else t[:n - 1] + "…"


def main():
    data = load()
    lines = []
    for label, handle, grp in TOP:
        vids = data.get(label, [])
        sel = pick(vids)
        lines.append("### %s — `%s`" % (label, handle))
        lines.append("")
        lines.append("**%s** · %d tab видеа измерени · 10 примера (5 в ред)" % (grp, len(vids)))
        lines.append("")
        for i in range(0, len(sel), 5):
            row = sel[i:i + 5]
            lines.append("| " + " | ".join(
                "[%s](%s)" % (short(v.get("t", "")), v.get("url", "")) for v in row) + " |")
            lines.append("|" + "---|" * len(row))
        lines.append("")
    out = "\n".join(lines)
    with open(os.path.join(R, "_top10_samples.md"), "w", encoding="utf-8") as f:
        f.write(out)
    print(out)


if __name__ == "__main__":
    main()
