# -*- coding: utf-8 -*-
"""Count tab-style videos per candidate channel (full /videos enumeration).

Uses flat playlist extraction (no download). Counts:
  total   - all videos on the channel
  tabs    - titles that look like tab/chord cover/lesson videos
  rock    - of those, rock/grunge/metal/alt universe
Writes _yt_counts.json
"""
import json
import re
import sys
import time

import yt_dlp

TAB_RE = re.compile(
    r"(\btab(s|bing)?\b|tabs\s*\+?\s*chords|chords\s*\+?\s*tabs|on.?screen tabs|screen tabs|"
    r"with tab|tab cover|tabs in (the )?video|tab in descri)",
    re.I,
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
    r"the damned|damned|cheap trick|nirvana|husker du|the dandy Warhols|sea level|"
    r"rock|metal|punk|grunge|alternative rock|alt rock|indie rock|hard rock|classic rock)",
    re.I,
)

OPTS = {
    "quiet": True,
    "skip_download": True,
    "extract_flat": True,
    "no_warnings": True,
    "ignoreerrors": True,
    "socket_timeout": 40,
    "extractor_args": {"youtube": {"player_client": ["web"]}},
}

# name -> channel url/id
CANDIDATES = {
    "guitar cover with tabs & chords": None,
    "Mr. Tabs": None,
    "GuitarZero2Hero Express": None,
    "Sparky Guitar": None,
    "Nikola Gugoski": None,
    "Nik Nocturnal": None,
    "De Gaspari Guitar": None,
    "yuichi112": None,
    "CoverSolutions": None,
    "Matt Ten": None,
    "East Village Guitar Method": None,
    "Lex Guitar Tabs": None,
    "Steven Perrone": None,
    "Etienne de Loriol - Guitar Lessons": None,
    "TAB 'EM ALL": None,
    "CWZ Guitar": None,
    "Sightline Guitar": None,
    "Schmuck's Punk Tabs": None,
    "Agape Guitar": "UCmytlCZYxdCHbL12SJc4VeQ",
    "GuitarZero2Hero": None,
    "BernadetteTeachesMusic": None,
    "Guitar Grind": None,
    "Mikkel Lassalle": None,
    "JB5alive14": None,
    "Guitar Tab Studio": None,
    "Abraham Lewis Guitar": None,
    "Thony Sabat": None,
    "Andy Hillier Guitar Channel": None,
    "GuitarPro? / G & Guitar": None,
    "Rockin Tabs": None,
    "Dotti Brothers": None,
    "juha aitakangas": None,
    "Etienne": None,
}

# extra handle guesses for channels not present in the search harvest
HANDLE_GUESS = {
    "guitar cover with tabs & chords": ["@guitarcoverwithtabsandchords"],
    "Mr. Tabs": ["@mrtabs", "@MrTabsOfficial"],
    "GuitarZero2Hero Express": ["@GuitarZero2HeroExpress"],
    "GuitarZero2Hero": ["@GuitarZero2Hero"],
    "BernadetteTeachesMusic": ["@BernadetteTeachesMusic"],
    "Sparky Guitar": ["@SparkyGuitar"],
    "Nikola Gugoski": ["@NikolaGugoski"],
    "Nik Nocturnal": ["@NikNocturnal"],
    "De Gaspari Guitar": ["@DeGaspariGuitar"],
    "yuichi112": ["@yuichi112"],
    "CoverSolutions": ["@CoverSolutions"],
    "Matt Ten": ["@MattTen", "@matt10ten"],
    "East Village Guitar Method": ["@EastVillageGuitarMethod"],
    "Lex Guitar Tabs": ["@LexGuitarTabs"],
    "Steven Perrone": ["@StevenPerrone"],
    "TAB 'EM ALL": ["@TABEALL", "@TabEmAll"],
    "CWZ Guitar": ["@CWZGuitar"],
    "Sightline Guitar": ["@SightlineGuitar"],
    "Schmuck's Punk Tabs": ["@PunkRockGuitarTabs"],
    "Guitar Grind": ["@GuitarGrind"],
    "Mikkel Lassalle": ["@MikkelLassalle"],
    "JB5alive14": ["@JB5alive14"],
    "Guitar Tab Studio": ["@GuitarTabStudio"],
    "Abraham Lewis Guitar": ["@AbrahamLewisGuitar"],
    "Thony Sabat": ["@ThonySabat"],
    "Andy Hillier Guitar Channel": ["@AndyHillier"],
    "Rockin Tabs": ["@RockinTabs"],
    "Dotti Brothers": ["@DottiBrothers"],
    "Juha Aitakangas": ["@JuhaAitakangas"],
}


def resolve_id_by_search(name):
    """Find a channel id for a channel name via YouTube search."""
    try:
        with yt_dlp.YoutubeDL(OPTS) as y:
            info = y.extract_info("ytsearch8:%s" % name, download=False)
        for e in info.get("entries") or []:
            if not e:
                continue
            ch = (e.get("channel") or "").strip().lower()
            key = name.split(" - ")[0].strip().lower()
            if ch and (ch == key or key in ch or ch in key):
                return e.get("channel_id")
    except Exception:  # noqa: BLE001
        pass
    return None


def resolve_id_by_handle(name):
    for h in HANDLE_GUESS.get(name, []):
        try:
            with yt_dlp.YoutubeDL(OPTS) as y:
                info = y.extract_info("https://www.youtube.com/%s" % h, download=False)
            if info and info.get("channel_id"):
                return info["channel_id"]
        except Exception:  # noqa: BLE001
            continue
    return None


def resolve(url):
    with yt_dlp.YoutubeDL(OPTS) as y:
        info = y.extract_info(url, download=False)
        return info


def enumerate_channel(cid, url=None):
    target = url or ("https://www.youtube.com/channel/%s/videos" % cid)
    t0 = time.time()
    with yt_dlp.YoutubeDL(OPTS) as y:
        info = y.extract_info(target, download=False)
    entries = info.get("entries") or []
    titles = [(e.get("title") or "") for e in entries if e]
    subs = info.get("channel_follower_count")
    return {
        "channel": info.get("channel"),
        "channel_id": info.get("channel_id"),
        "subs": subs,
        "total": len(titles),
        "tabs": sum(1 for t in titles if TAB_RE.search(t)),
        "rock_tabs": sum(1 for t in titles if TAB_RE.search(t) and ROCK_RE.search(t)),
        "elapsed": round(time.time() - t0, 1),
        "samples": [t for t in titles if TAB_RE.search(t)][:5],
    }


def main():
    with open("_yt_discover.json", encoding="utf-8") as fh:
        disc = json.load(fh)
    ids = {}
    for c in disc["channels"]:
        if c.get("channel_id"):
            ids.setdefault(c["channel"], c["channel_id"])

    resolved = []
    for name, cid in CANDIDATES.items():
        if not cid:
            cid = ids.get(name) or resolve_id_by_search(name) or resolve_id_by_handle(name)
        if not cid:
            print("SKIP (no id): %s" % name, file=sys.stderr)
            continue
        try:
            r = enumerate_channel(cid)
        except Exception as exc:  # noqa: BLE001
            print("FAIL %s: %s" % (name, exc), file=sys.stderr)
            continue
        r["label"] = name
        resolved.append(r)
        print(
            "%-38s total=%-5s tabs=%-5s rock=%-5s subs=%s (%.0fs)"
            % (name[:38], r["total"], r["tabs"], r["rock_tabs"], r["subs"], r["elapsed"]),
            flush=True,
        )
        with open("_yt_counts.json", "w", encoding="utf-8") as fh:
            json.dump(resolved, fh, ensure_ascii=False, indent=1)

    resolved.sort(key=lambda d: (-d["rock_tabs"], -d["tabs"]))
    print("\n=== RANKED by rock tab videos ===")
    for i, d in enumerate(resolved, 1):
        print(
            "%2d. %-38s rock_tabs=%-4s tabs=%-4s total=%-5s subs=%s"
            % (i, d["label"][:38], d["rock_tabs"], d["tabs"], d["total"], d["subs"])
        )


if __name__ == "__main__":
    main()
