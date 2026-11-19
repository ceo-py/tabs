# -*- coding: utf-8 -*-
"""Discover YouTube channels with on-screen tab/chord cover videos (rock/grunge style).

Strategy:
  1. Run several ytsearch queries (flat, no download) and count per-channel hits
     whose title looks like a tab/chord cover of a rock-ish song.
  2. Rank channels by that count.

Output: _yt_discover.json
"""
import json
import re
import sys
import collections

import yt_dlp

QUERIES = [
    "guitar cover tabs chords 90s rock",
    "grunge guitar cover tab on screen",
    "rock song guitar cover with tabs on screen",
    "punk rock guitar cover tab",
    "alt rock guitar cover tabs chords strumming",
    "guitar cover tab nirvana pearl jam soundgarden",
    "guitar cover tabs chords metal rock",
    "guitar cover with screen tabs",
]

TAB_RE = re.compile(
    r"\b(tab(s|bing)?\b|tabs\s*\+?\s*chords|chords\s*\+?\s*tabs|on.?screen tabs|screen tabs|"
    r"with tab|tab cover|tabs on screen|t\s*a\s*b)",
    re.I,
)

# artists/keywords that count as "rock / grunge / metal / 90s alt" universe
ROCK_RE = re.compile(
    r"(nirvana|pearl jam|soundgarden|alice in chains|stone temple pilots|"
    r"led zeppelin|queen|david bowie|the doors|red hot chili peppers|r\.?e\.?m\.?|"
    r"foo fighters|green day|blink-?182|sum 41|simple plan|offspring|slipknot|"
    r"metallica|iron maiden|black sabbath|ac/?dc|motley crue|gun n roses|guns n roses|"
    r"aerosmith|bon jovi|def leppard|scorpions|whitesnake|van halen|"
    r"oasis|blur|pulp|travis|keane|coldplay|lana del ray|the killers|arctic monkeys|"
    r"kaiser chiefs|the strokes|the white stripes|royal blood|temples|"
    r"foo|smashing pumpkins|radioshead|radiohead|fleetwood mac|eagles|"
    r"creed|third eye blind|matchbox twenty|staind|incubus|goo goo dolls|"
    r"silverchair|korn|deftones|rage against the machine|system of a down|"
    r"audioslave|disturbed|evanescence|seether|nickelback|theory of a deadman|"
    r"smash mouth|golden earring|white lion|bon jovi|twisted sister|"
    r"rock|metal|punk|grunge|alternative|indie)",
    re.I,
)

OPTS = {
    "quiet": True,
    "skip_download": True,
    "extract_flat": True,
    "no_warnings": True,
    "ignoreerrors": True,
    "socket_timeout": 30,
    "extractor_args": {"youtube": {"player_client": ["web"]}},
}


def search(q, n=120):
    out = []
    try:
        with yt_dlp.YoutubeDL(OPTS) as y:
            info = y.extract_info("ytsearch%d:%s" % (n, q), download=False)
            for e in info.get("entries") or []:
                if not e:
                    continue
                out.append(
                    {
                        "title": e.get("title") or "",
                        "channel": e.get("channel") or e.get("uploader") or "",
                        "channel_id": e.get("channel_id") or e.get("uploader_id") or "",
                        "id": e.get("id"),
                    }
                )
    except Exception as exc:  # noqa: BLE001
        print("QUERY FAILED %r: %s" % (q, exc), file=sys.stderr)
    return out


def main():
    hits = collections.defaultdict(lambda: {"tabs": 0, "rocktabs": 0, "samples": []})
    total = 0
    for q in QUERIES:
        rows = search(q)
        total += len(rows)
        print("query %-55s -> %d" % (q, len(rows)), file=sys.stderr)
        for r in rows:
            ch = r["channel"]
            if not ch:
                continue
            h = hits[ch]
            if TAB_RE.search(r["title"]):
                h["tabs"] += 1
                if ROCK_RE.search(r["title"]):
                    h["rocktabs"] += 1
                    if len(h["samples"]) < 3:
                        h["samples"].append(r["title"])

    data = [
        {
            "channel": ch,
            "channel_id": h["channel_id"] if "channel_id" in h else "",
            "tab_hits": h["tabs"],
            "rock_tab_hits": h["rocktabs"],
            "samples": h["samples"],
        }
        for ch, h in hits.items()
    ]
    data.sort(key=lambda d: (-d["rock_tab_hits"], -d["tab_hits"]))
    with open("_yt_discover.json", "w", encoding="utf-8") as fh:
        json.dump({"total_search_rows": total, "channels": data}, fh, ensure_ascii=False, indent=1)
    for d in data[:60]:
        print(
            "%4d %4d  %-45s %s"
            % (d["rock_tab_hits"], d["tab_hits"], d["channel"][:45], (d["samples"] or [""])[0][:70])
        )


if __name__ == "__main__":
    main()
