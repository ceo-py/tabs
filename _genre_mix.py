# -*- coding: utf-8 -*-
"""Genre mix per top-10 tab channel, computed from the real video titles."""
import json
import os
import re
import collections

R = os.path.dirname(os.path.abspath(__file__))

GENRES = {
    "Grunge / 90s alt": r"nirvana|pearl jam|soundgarden|alice in chains|stone temple pilots|"
                        r"mudhoney|screaming trees|melvins|dinosaur jr|sebad oh|sebadoh|hokum|"
                        r"mad season|the fray|hole|garbage|veruca salt|malice n forgery|"
                        r"grunge|tad pons|temple of the dog|mark lanegan|chavez|",
    "Punk / hardcore": r"ramones|bad religion|misfits|sex pistols|descendents|descendents|"
                        r"rancid|green day|nofx|dead kennedys|germs|the clash|the damned|"
                        r"social distortion|dropkick murphys|offspring|lagwagon|bad religion|"
                        r"d.r.i|choking victim|minor threat|black flag|exploited|"
                        r"the exploited|toy dolls|spitfires|the varukers|dr. feelgood|"
                        r"jigsaw|napalm death|hellbastards|backfire|real kids|"
                        r"punk rock|punk\b|the clash|hive|business|cro mags|lagwagon|"
                        r"against me|the bronx|descendents|obey|face to face|",
    "Metal / hard rock": r"metallica|iron maiden|black sabbath|slayer|megadeth|slipknot|"
                         r"pantera|system of a down|korn|deftones|tool\b|disturbed|"
                         r"motorhead|motörhead|rammstein|ghost\b|sepultura|anthrax|testament|"
                         r"exodus|judas priest|led zeppelin|rush\b|dio\b|accept|"
                         r"annihilator|overkill|exciter|hellyeah|void meadow|"
                         r"in flames|children of bodom|amazing venom|trivium|"
                         r"motley crue|gun n roses|guns n roses|def leppard|scorpions|"
                         r"van halen|white snake|whitesnake|aerosmith|bon jovi|"
                         r"happy sad face|body count|testament|danzig|death\b|",
    "Classic rock / 70s-80s": r"queen|led zeppelin|pink floyd|ac/dc|aerosmith|bon jovi|"
                              r"def leppard|scorpions|van halen|gun n roses|guns n roses|"
                              r"journey|foreigner|boston|deep purple|dio\b|rush\b|"
                              r"whitesnake|heart\b|cheap trick|blue oyster cult|"
                              r"black sabbath|carpenter|foo fighters|kansas|"
                              r"the eagles|eagles\b|lynyrd skynyrd|zz top|motley crue|"
                              r"boston|creed|three doors down|styx|kansas|joe satriani|"
                              r"steve vai|richie kotzen|dire straits|thin lizzy|rush|",
    "Alt / indie / pop-punk 90s+": r"radiohead|smashing pumpkins|foo fighters|oasis|blur\b|"
                                  r"beck\b|weezer|blink-?182|sum 41|the cranberries|"
                                  r"counting crows|third eye blind|gin blossoms|sister hazel|"
                                  r"bush\b|veruca salt|travis\b|keane|coldplay|the killers|"
                                  r"arctic monkeys|kaiser chiefs|the strokes|white stripes|"
                                  r"royal blood|temple of the dog|green day|simple plan|"
                                  r"good charlotte|new found glory|beck|the offspring|"
                                  r"the offended|funeral for a friend|nine days|"
                                  r"brand new|yellowcard|all time low|simple plan|"
                                  r"the all-American rejects|good music|"
                                  r"the wombats|arctic monkeys|kaiser chiefs|muse\b|"
                                  r"silverchair|incubus|madison avenue|"
                                  r"a perfect circle|tool\b|nine inch nails|"
                                  r"garbage\b|hole\b|weezer|"
                                  r"the killers|kaiser chiefs|",
    "Post-hardcore / emo": r"deftones|afi\b|thrice|coheed|brand new|taking back sunday|"
                           r"senses fail|finch\b|underoath|chiodos|saosin|"
                           r"pj harvey|barrington mills|emery|carcass|"
                           r"the used|nine inch nails|glass jaw|deadstar|",
    "Hard rock / stoner": r"black sabbath|led zeppelin|kyuss|fu manchu|monsters of rock|"
                          r"sleep\b|earthless|place of skulls|melvins|kyuss|"
                          r"ac/dc|van halen|motley crue|radiohead|nirvana|"
                          r"queen|thin lizzy|rush|judas priest|dio\b|",
    "Pop / soundtrack / misc": r"michael jackson|bruno mars|madonna|taylor swift|"
                               r"ed sheeran|adele|beyonce|justin bieber|katy perry|"
                               r"rihanna|beyonc|dua lipa|doja cat|stray kids|"
                               r"bts\b|bocchi|genshin|honkai|game|zelda|nintendo|"
                               r"final fantasy|mario|ocarina|assassin|elden|",
}

BASS_RE = re.compile(r"\bbass\b", re.I)
STRUM_RE = re.compile(r"strumm?ing|chords?\s*\+", re.I)

TOP = [
    "DadRock TABS", "Schmuck's Punk Tabs", "CWZ Guitar", "CoverSolutions",
    "Dotti Brothers", "Nikola Gugoski", "Steven Perrone", "GuitarForce.Com",
    "Godderdy Tabs", "guitar cover with tabs & chords",
]


def main():
    data = {}
    for f in ("_verify_channels.json", "_verify_new2.json"):
        p = os.path.join(R, f)
        if not os.path.exists(p):
            continue
        raw = json.load(open(p, encoding="utf-8"))
        for val in raw.values():
            label = val.get("label")
            vids = val.get("videos") or []
            if label and vids:
                data.setdefault(label, vids)

    for label in TOP:
        vids = data.get(label)
        if not vids:
            print("!! no titles for", label)
            continue
        tabv = [v for v in vids if v.get("tab") or BASS_RE.search(v.get("t", "")) or
                re.search(r"\btab", v.get("t", ""), re.I)]
        cnt = collections.Counter()
        bass = 0
        for v in tabv:
            t = v.get("t", "")
            hit = False
            for g, rx in GENRES.items():
                if re.search(rx.rstrip("|"), t, re.I):
                    cnt[g] += 1
                    hit = True
                    break
            if not hit:
                cnt["— other / not classified"] += 1
            if BASS_RE.search(t):
                bass += 1
        print("\n=== %s  (%d tab videos)" % (label, len(tabv)))
        for g, c in cnt.most_common():
            print("    %-32s %4d  (%4.0f%%)" % (g, c, 100.0 * c / max(1, len(tabv))))
        print("    %-32s %4d  (%4.0f%%)   [overlaps other genres]" % (
            "mentions bass", bass, 100.0 * bass / max(1, len(tabv))))


if __name__ == "__main__":
    main()
