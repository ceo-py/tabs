# -*- coding: utf-8 -*-
"""Second pass: additional tab-niche channels found via the ecosystem video
("The BEST Places to Learn Guitar Songs Online") and web search."""
import json
import sys
import time
import unicodedata
import re

import yt_dlp

OPTS = {
    "quiet": True, "skip_download": True, "extract_flat": True, "no_warnings": True,
    "ignoreerrors": True, "socket_timeout": 40,
    "extractor_args": {"youtube": {"player_client": ["web"]}},
}


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


TAB_RE = re.compile(
    r"(\btabs?\b|\btabbing\b|\btabs?\s*\+|\+\s*tabs?\b|on.?screen tabs?|screen tabs?|"
    r"with tabs?\b|tabs? in (the )?video|tab in descri)")
COVER_RE = re.compile(r"(cover|playthrough|lesson|tutorial|play along|play-along|demonstration)")
GRUNGE_RE = re.compile(
    r"(nirvana|pearl jam|soundgarden|alice in chains|stone temple pilots|mudhoney|"
    r"screaming trees|melvins|dinosaur jr|hokum|mad season|the fray|grunge|hole|garbage|"
    r"veruca salt|mary go round|malice n forgery|david gedge|smashing pumpkins)")
ROCK_RE = re.compile(
    r"(nirvana|pearl jam|soundgarden|alice in chains|stone temple pilots|led zeppelin|queen|"
    r"david bowie|the doors|red hot chili peppers|r\.?e\.?m\.?|foo fighters|green day|blink-?182|"
    r"sum 41|simple plan|offspring|slipknot|metallica|iron maiden|black sabbath|ac/?dc|"
    r"motley crue|gun n roses|guns n roses|aerosmith|bon jovi|def leppard|scorpions|whitesnake|"
    r"van halen|oasis|blur|pulp|travis|keane|coldplay|lana del rey|the killers|arctic monkeys|"
    r"kaiser chiefs|the strokes|white stripes|royal blood|smashing pumpkins|radiohead|"
    r"fleetwood mac|eagles|creed|third eye blind|matchbox twenty|staind|incubus|goo goo dolls|"
    r"silverchair|korn|deftones|rage against the machine|system of a down|audioslave|disturbed|"
    r"evanescence|seether|nickelback|theory of a deadman|smash mouth|golden earring|"
    r"twisted sister|bad religion|ramones|descendents|misfits|sex pistols|the damned|"
    r"cheap trick|husker du|dandy Warhols|sea level|rancid|social distortion|"
    r"\brock\b|\bmetal\b|\bpunk\b|\bgrunge\b|alternative rock|alt rock|indie rock|hard rock|classic rock)")

EXTRA = [
    ("Mr. Tabs (real)", ["@Mr.Tabs.Guitar.Lessons"]),
    ("Godderdy Tabs", ["@GodderdyTabs"]),
    ("Play Along Tabs", ["@PlayAlongTabs"]),
    ("Reliable Bandmate", ["@ReliableBandmate"]),
    ("EpicGuitarInstruction", ["@EpicGuitarInstruction"]),
    ("Simple Guitar Tabs", ["@SimpleGuitarTabsYoutube"]),
    ("Zombie Guitar", ["@zombieguitar"]),
    ("Lets Play All", ["@LetsPlayAll"]),
    ("JustinGuitarSongs", ["@JustinGuitarSongs"]),
    ("Marty Music", ["@MartyMusic"]),
    ("GuitarLessons365", ["@GuitarLessons365SongLessons", "@GuitarLessons365"]),
    ("Songnotes", ["@songnotes"]),
    ("Shutup And Play", ["@ShutupAndPlayGuitarTutorials"]),
    ("12 Foot Chain", ["@12FootChain"]),
    ("Marin Music Center", ["@MarinMusicCenter"]),
    ("Andrew Clark", ["@andrewclarkeguitar"]),
    ("Carl Brown", ["@CarlBrownGuitar"]),
    ("Tim Pierce", ["@TimPierceGuitar"]),
    ("MiniLessons", ["@MiniLessons"]),
    ("Guitar Tab Camp", ["@GuitarTabCamp"]),
    ("Andrei Moraru / Rock Tabs", ["@rocktabs", "@RockTabsOfficial"]),
    ("Traditional Baylor", ["@TraditionalBaylor"]),
    ("Dan Gilby / Dan The Man", ["@DanTheMan"]),
    ("Ultimate Guitar Lessons", ["@UltimateGuitarLessons"]),
    ("Rock Music Lessons", ["@RockMusicLessons"]),
]


def enum(url):
    t0 = time.time()
    with yt_dlp.YoutubeDL(OPTS) as y:
        info = y.extract_info(url, download=False)
    entries = [e for e in (info.get("entries") or []) if e]
    titles = [(e.get("title") or "") for e in entries]
    norms = [norm(t) for t in titles]
    idx = [i for i, t in enumerate(norms) if TAB_RE.search(t)]
    tabn = [norms[i] for i in idx]
    return {
        "channel": info.get("channel"),
        "channel_id": info.get("channel_id"),
        "subs": info.get("channel_follower_count"),
        "total": len(titles),
        "tabs": len(idx),
        "rock_tabs": sum(1 for t in tabn if ROCK_RE.search(t)),
        "grunge_tabs": sum(1 for t in tabn if GRUNGE_RE.search(t)),
        "style_tabs": sum(1 for k, i in enumerate(idx) if COVER_RE.search(norm(titles[i]))),
        "elapsed": round(time.time() - t0, 1),
        "sample_titles": [titles[i] for i in idx][:6],
        "sample_rock": [titles[i] for i in idx if ROCK_RE.search(norms[i])][:6],
    }


def main():
    out = []
    for label, handles in EXTRA:
        done = False
        for h in handles:
            try:
                r = enum("https://www.youtube.com/%s/videos" % h)
            except Exception as exc:  # noqa: BLE001
                print("FAIL %s %s: %s" % (label, h, exc), file=sys.stderr)
                continue
            r["label"] = label
            out.append(r)
            done = True
            print("%-32s total=%-5s tabs=%-5s rock=%-5s grunge=%-5s style=%-5s subs=%s"
                  % (label[:32], r["total"], r["tabs"], r["rock_tabs"], r["grunge_tabs"],
                     r["style_tabs"], r["subs"]), flush=True)
            break
        if not done:
            print("MISS %s" % label, file=sys.stderr)
        json.dump(out, open("_yt_extra.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n=== EXTRAS ===")
    for d in sorted(out, key=lambda x: -x["rock_tabs"]):
        print("%-32s rock=%-4s grunge=%-4s tabs=%-5s style=%-5s total=%-5s subs=%s"
              % (d["label"][:32], d["rock_tabs"], d["grunge_tabs"], d["tabs"],
                 d["style_tabs"], d["total"], d["subs"]))


if __name__ == "__main__":
    main()
