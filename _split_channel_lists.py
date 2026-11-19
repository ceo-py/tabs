# -*- coding: utf-8 -*-
"""Split the full dump into one markdown file per channel (_channel_lists/)."""
import json
import os
import re

R = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(R, "_channel_lists")

GENRES = {
    "GRUNGE": r"nirvana|pearl jam|soundgarden|alice in chains|stone temple pilots|mudhoney|"
              r"screaming trees|melvins|dinosaur jr|sebadoh|hokum|mad season|the fray|"
              r"\bhole\b|garbage|veruca salt|malice n forgery|grunge|temple of the dog|chavez",
    "PUNK": r"ramones|bad religion|misfits|sex pistols|descendents|rancid|green day|nofx|"
            r"dead kennedys|germs|the clash|the damned|social distortion|dropkick murphys|"
            r"offspring|lagwagon|anti-flag|minor threat|dillinger four|teenage bottlerocket|"
            r"mxpx|toxic reason|punk",
    "METAL": r"metallica|iron maiden|black sabbath|slayer|megadeth|slipknot|pantera|"
             r"system of a down|korn|deftones|\btool\b|disturbed|motorhead|rammstein|\bghost\b|"
             r"sepultura|anthrax|testament|exodus|judas priest|led zeppelin|\bdio\b|"
             r"motley crue|gun n roses|guns n roses|def leppard|scorpions|van halen|whitesnake|"
             r"aerosmith|bon jovi|avenged sevenfold|arch enemy|children of bodom|\bkiss\b|"
             r"accept|dokken|ratt\b|ozzy|racer x|king diamond|dream theater|marilyn manson|"
             r"lindemann|limp bizkit|rob zombie|emigrate|chevelle|hatebreed|"
             r"the warning|billy talent|nine inch nails|queens of the stone age",
    "CLASSIC": r"queen|pink floyd|ac/dc|journey|foreigner|boston|deep purple|\brush\b|"
               r"\bheart\b|cheap trick|blue oyster cult|eagles\b|lynyrd skynyrd|zz top|styx|"
               r"kansas|joe satriani|steve vai|dire straits|thin lizzy|the doors|the cult|"
               r"stevie ray vaughan|jimi hendrix|gary moore|joe bonamassa|creed",
    "ALT": r"radiohead|smashing pumpkins|foo fighters|oasis|\bblur\b|\bbeck\b|weezer|blink-?182|"
           r"sum 41|the cranberries|counting crows|third eye blind|gin blossoms|sister hazel|"
           r"\bbush\b|travis\b|keane|coldplay|the killers|arctic monkeys|kaiser chiefs|"
           r"the strokes|white stripes|royal blood|simple plan|silverchair|incubus|"
           r"a perfect circle|\bmuse\b|linkin park|red hot chili peppers|\brhcp\b|"
           r"the smiths|depeche mode|tame impala",
    "POSTHC": r"\bafi\b|thrice|coheed|brand new|taking back sunday|senses fail|\bfinch\b|"
              r"underoath|chiodos|saosin|emery|carcass|the used|glass jaw|deadstar|"
              r"pj harvey|barrington mills",
    "POP": r"michael jackson|bruno mars|madonna|taylor swift|ed sheeran|adele|beyonce|"
           r"katy perry|rihanna|dua lipa|doja cat|stray kids|\bbts\b|bocchi|genshin|"
           r"zelda|nintendo|final fantasy|mario|ocarina|assassin|elden|yorushika|specialz|"
           r"zutomayo|king gnu|lilac|buwan",
}
GEN_RE = {k: re.compile(v, re.I) for k, v in GENRES.items()}
TAB_RE = re.compile(r"\btab", re.I)
BASS_RE = re.compile(r"\bbass\b", re.I)
COVER_RE = re.compile(r"cover|lesson|tutorial|play ?along|how to play|walkthrough", re.I)


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


def flags(t):
    fl = []
    if TAB_RE.search(t):
        fl.append("TAB")
    for g, rx in GEN_RE.items():
        if rx.search(t):
            fl.append(g)
    if BASS_RE.search(t):
        fl.append("BASS")
    if COVER_RE.search(t):
        fl.append("COVER")
    return fl


def safe(name):
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")
    return s or "channel"


def main():
    data = load()
    os.makedirs(OUT, exist_ok=True)
    index = []
    for label, vids in sorted(data.items(), key=lambda kv: -len(kv[1])):
        fn = "%s.md" % safe(label)
        lines = ["# %s" % label, "",
                 "Всички видеа от канала (%d). Флагове: TAB / COVER / BASS / жанр." % len(vids), "",
                 "| # | Видео | Флагове |", "|---|---|---|"]
        for i, v in enumerate(vids, 1):
            t = re.sub(r"\s+", " ", v.get("t", "")).strip().replace("|", "\\|")
            lines.append("| %d | [%s](%s) | %s |" % (i, t, v.get("url", ""), " ".join(flags(t))))
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        tab = sum(1 for v in vids if TAB_RE.search(v.get("t", "")))
        index.append((label, len(vids), tab, fn))
    index.sort(key=lambda x: -x[1])
    with open(os.path.join(OUT, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("# Индекс на каналите\n\n| # | Канал | Видеа | С tab | Файл |\n|---|---|---|---|---|\n")
        for i, (label, tot, tab, fn) in enumerate(index, 1):
            f.write("| %d | %s | %d | %d | [%s](%s) |\n" % (i, label, tot, tab, fn, fn))
    print("written %d channel files to _channel_lists/" % len(index))
    print("total videos: %d" % sum(x[1] for x in index))


if __name__ == "__main__":
    main()
