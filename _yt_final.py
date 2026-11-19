# -*- coding: utf-8 -*-
"""Refine per-channel tab counting with unicode-normalised titles.

Why: some channels (e.g. Agape Guitar) use mathematical-bold letters in titles
("[𝐓𝐚𝐛]"), so a plain ASCII regex misses them. This normalises first.

Also adds:
  grunge_tabs - grunge-specific artists (Nirvana, Pearl Jam, Soundgarden, ...)
  style_tabs  - tab videos whose title also mentions cover/lesson/playthrough
                (i.e. the GZ2H-style "cover with on-screen tabs" format)

Reads channel ids from _yt_counts.json + extra candidates, writes _yt_final.json
"""
import json
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
    "socket_timeout": 40,
    "extractor_args": {"youtube": {"player_client": ["web"]}},
}


def norm(s):
    """NFKC + strip mathematical alphanumeric formatting to plain ASCII."""
    if not s:
        return ""
    out = []
    for ch in unicodedata.normalize("NFKC", s):
        cp = ord(ch)
        if 0x1D400 <= cp <= 0x1D7FF:      # mathematical bold/italic/etc
            out.append(chr(cp - 0x1D400 + 65))
        elif 0x1D7CE <= cp <= 0x1D7FF:    # mathematical digits
            out.append(chr(cp - 0x1D7CE + 48))
        elif 0x1F130 <= cp <= 0x1F189:    # squared latin letters
            out.append(chr(cp - 0x1F130 + 65))
        else:
            out.append(ch)
    return unicodedata.normalize("NFKC", "".join(out)).lower()


TAB_RE = re.compile(
    r"(\btabs?\b|\btabbing\b|\btabs?\s*\+|\+\s*tabs?\b|on.?screen tabs?|screen tabs?|"
    r"with tabs?\b|tabs? in (the )?video|tab in descri|\bt\b\s*\||\|\s*t\b)",
)

COVER_RE = re.compile(r"(cover|playthrough|lesson|tutorial|play along|play-along|demonstration)")

GRUNGE_RE = re.compile(
    r"(nirvana|pearl jam|soundgarden|alice in chains|stone temple pilots|"
    r"mudhoney|screaming trees|melvins|dinosaur jr|hokum|mad season|"
    r"the fray|grunge|hole|garbage|veruca salt|mary go round)",
)

ROCK_RE = re.compile(
    r"(nirvana|pearl jam|soundgarden|alice in chains|stone temple pilots|led zeppelin|"
    r"queen|david bowie|the doors|red hot chili peppers|r\.?e\.?m\.?|foo fighters|green day|"
    r"blink-?182|sum 41|simple plan|offspring|slipknot|metallica|iron maiden|black sabbath|"
    r"ac/?dc|motley crue|gun n roses|guns n roses|aerosmith|bon jovi|def leppard|scorpions|"
    r"whitesnake|van halen|oasis|blur|pulp|travis|keane|coldplay|lana del rey|the killers|"
    r"arctic monkeys|kaiser chiefs|the strokes|white stripes|royal blood|smashing pumpkins|"
    r"radiohead|fleetwood mac|eagles|creed|third eye blind|matchbox twenty|staind|incubus|"
    r"goo goo dolls|silverchair|korn|deftones|rage against the machine|system of a down|"
    r"audioslave|disturbed|evanescence|seether|nickelback|theory of a deadman|smash mouth|"
    r"golden earring|twisted sister|bad religion|ramones|descendents|misfits|sex pistols|"
    r"the damned|cheap trick|husker du|the dandy Warhols|sea level|"
    r"blink-182|bad religion|rancid|social distortion|offspring|"
    r"\brock\b|\bmetal\b|\bpunk\b|\bgrunge\b|alternative rock|alt rock|indie rock|hard rock|classic rock)",
)

EXTRA = {
    "Rockin Tabs": ["@RockinTabs", "@rockintabs"],
    "Dotti Brothers": ["@DottiBrothers"],
    "Juha Aitakangas": ["@JuhaAitakangas"],
    "Andy Hillier Guitar Channel": ["@AndyHillierGuitarChannel", "@AndyHillier"],
    "G & Guitar": ["@gguitar"],
    "Mr. Tabs": ["@MrTabs", "@mrtabs"],
    "guitar cover with tabs & chords": ["@guitarcoverwithtabsandchords", "@guitarcoverwithtabs"],
    "ThunderB Music": ["@ThunderBMusic"],
    "Traditional Baylor": ["@TraditionalBaylor"],
    "RockStone": ["@RockStoneGuitar"],
    "Guitar Stuff": ["@GuitarStuff"],
    "Guitorama": ["@Guitorama"],
}


def enum(cid=None, url=None):
    target = url or ("https://www.youtube.com/channel/%s/videos" % cid)
    t0 = time.time()
    with yt_dlp.YoutubeDL(OPTS) as y:
        info = y.extract_info(target, download=False)
    entries = [e for e in (info.get("entries") or []) if e]
    titles = [(e.get("title") or "") for e in entries]
    norms = [norm(t) for t in titles]
    tab = [i for i, t in enumerate(norms) if TAB_RE.search(t)]
    tab_titles = [titles[i] for i in tab]
    tabn = [norms[i] for i in tab]
    return {
        "channel": info.get("channel"),
        "channel_id": info.get("channel_id"),
        "subs": info.get("channel_follower_count"),
        "total": len(titles),
        "tabs": len(tab),
        "rock_tabs": sum(1 for t in tabn if ROCK_RE.search(t)),
        "grunge_tabs": sum(1 for t in tabn if GRUNGE_RE.search(t)),
        "style_tabs": sum(1 for k, i in enumerate(tab) if COVER_RE.search(tabn[k])),
        "elapsed": round(time.time() - t0, 1),
        "sample_titles": tab_titles[:6],
        "sample_rock": [titles[i] for i in tab if ROCK_RE.search(norms[i])][:6],
    }


def main():
    with open("_yt_counts.json", encoding="utf-8") as fh:
        prev = json.load(fh)
    out = []
    seen = set()
    for p in prev:
        cid = p.get("channel_id")
        if not cid:
            continue
        seen.add(p["label"])
        try:
            r = enum(cid=cid)
        except Exception as exc:  # noqa: BLE001
            print("FAIL %s %s" % (p["label"], exc), file=sys.stderr)
            continue
        r["label"] = p["label"]
        out.append(r)
        print("%-38s total=%-5s tabs=%-5s rock=%-5s grunge=%-5s style=%-5s subs=%s"
              % (p["label"][:38], r["total"], r["tabs"], r["rock_tabs"], r["grunge_tabs"],
                 r["style_tabs"], r["subs"]), flush=True)
        json.dump(out, open("_yt_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # extras
    for label, handles in EXTRA.items():
        if label in seen:
            continue
        ok = False
        for h in handles:
            try:
                r = enum(url="https://www.youtube.com/%s/videos" % h)
            except Exception:  # noqa: BLE001
                continue
            r["label"] = label
            out.append(r)
            ok = True
            print("%-38s total=%-5s tabs=%-5s rock=%-5s grunge=%-5s style=%-5s subs=%s"
                  % (label[:38], r["total"], r["tabs"], r["rock_tabs"], r["grunge_tabs"],
                     r["style_tabs"], r["subs"]), flush=True)
            break
        if not ok:
            print("MISS %s" % label, file=sys.stderr)
        json.dump(out, open("_yt_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    out.sort(key=lambda d: (-d["rock_tabs"], -d["tabs"]))
    print("\n=== FINAL RANK (rock tab videos) ===")
    for i, d in enumerate(out, 1):
        print("%2d. %-36s rock=%-4s grunge=%-4s tabs=%-5s style=%-5s total=%-5s subs=%s"
              % (i, d["label"][:36], d["rock_tabs"], d["grunge_tabs"], d["tabs"],
                 d["style_tabs"], d["total"], d["subs"]))


if __name__ == "__main__":
    main()
