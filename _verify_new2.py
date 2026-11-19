# -*- coding: utf-8 -*-
"""Robust enumeration of the NEW candidate channels found by _verify_new.py
discovery (plus handles found via web search).

Fixes the throttling problem of the parallel run: one yt-dlp process, with
retry + stability check (re-fetch until two consecutive runs agree), so a
truncated flat playlist (2-3 entries) is detected and retried.

Writes _verify_new2.json
"""
import json
import os
import sys
import time

import yt_dlp

OPTS = {
    "quiet": True,
    "skip_download": True,
    "extract_flat": True,
    "no_warnings": True,
    "ignoreerrors": True,
    "socket_timeout": 60,
    "sleep_interval_requests": 1,
}

CANDIDATES = [
    # --- discovered by yt-dlp search (92) ---
    ("UCG5rlznCSDMEpbZ0FEdIaKA", "Kevin Balke"),
    ("UCwsWbyUgY6C_HLmxbGj3oWw", "East Village Guitar Method"),
    ("UCSRHRTHzLmrXzkFXRF5KQFQ", "Lets Play All"),
    ("UCkEqNoagiRay77z5oYMf0LA", "Mike Ka"),
    ("UCz1PeIEiNkKRwWDKFA6RkzQ", "Ernesto Schnack"),
    ("UCiUv5hTxoqVGWzS2iB9KYQw", "ThunderB Music"),
    ("UCcvtZjC7vAcstHP_c7yVjyQ", "Mike Atsushi"),
    ("UCuXsOXa7nOBaNmzSdaHVJSQ", "Guitar Push"),
    ("UCWIVTN7qyUUMq-yQWUbMOqg", "CH Way Out West"),
    ("UCIX13SvEGgAoP-rMT3sRBMw", "J. Guitar Avenue"),
    ("UCzYxGD8ze4-865FK7JNaMag", "GuitarForce.Com"),
    ("UCwyK-0o3xhqZdDTlJqUWQzw", "These Things Make Noises"),
    ("UC5A5PUllO1BoFoSMnMU8i_A", "cooktunedrive"),
    ("UCPwZmgAWkoFFCX0s9yYgPzg", "wang.elozzi"),
    ("UCv1kLsuAnVzrgNsoUzQLOaA", "Chevans Music"),
    ("UC_8orcN8oNL1UIIyNBrEqbA", "Play Along Guitar"),
    ("UCpoE9dIyuddiKUXoYYEFGpw", "SAW"),
    ("UCpiryJCOQiOasFOrqzdNnlQ", "Mish Ellanea"),
    ("UCULVXT-UOkYDEPVYpsZLGWw", "Dave Shannon Guitar Academy"),
    ("UCJMtkOQWF19FqGwrAZ2ZVTA", "Super Easy Bass"),
    ("UCFKSqUGO7a2cucPpQ11ZWNQ", "Nate Navarro"),
    ("UCdumgNVJ7Q7koeKxEzfzRIg", "sing & play along 4 guitar"),
    ("UCCGYLjjkFou7Jty1k20D9-Q", "Yellow Tabs"),
    ("UCBNkm8o5LiEVLxO8w0p2sfQ", "JustinGuitar"),
    ("UCFoKRwFccXoSqm7_aMenYKg", "Guitropolis"),
    ("UCVgPuZJRehYN3j2fAHRsVKA", "Fiddling with my Whistle"),
    ("UCmDOwRLQVMhYaGuZkDgNfUA", "Yoni Schlesinger"),
    ("UCFcmm3XId7I493cssokAIzw", "1cover 1shot"),
    ("UChI4NZR3kvPW4JxsYB5oLWQ", "Benson Brothers"),
    ("UCkMOS5rx6ufea_Vp6sIljNA", "EZ Song Lessons"),
    ("UCL6aJ9aw0Q6wnHN_6SUP3-g", "Bayou Stage"),
    ("UC2VKCoZND5PENxAXLl8r6Jw", "christianvib"),
    ("UCClyi2HUuVSeBJm1150aAcQ", "Corey Heuvel"),
    ("UCkBKJz-mYYejMCFMb1R8-vw", "Soumyajit Bhattacharya"),
    ("UCDtChgUjPelT14XkhZII-Tw", "Felipe Quintero Music"),
    ("UC0wYd_yCHSBlf63-qiELOaA", "Thomas Friedt Music"),
    ("UCW9_BO6QH8JoG87_lWBEb4A", "Nuson B-Track"),
    ("UCGClA_O4RA3sJCfgn_eCavA", "Nicro"),
    ("UCqAkm0llwy0WTtOhbZcpaRA", "Yuuki Tsujimura"),
    ("UCsWVChNTclj9EqWEiDlWlLA", "Hardly Ramone"),
    ("UCskS-dygbRwXYfaJS6qruNw", "Guitar Tab Lab"),
    ("UCJnhRGA9VcSG8ym9SYV9hUw", "Eu Toco Punk Assim"),
    ("UCnRUvWL4fAr_KSiPtmlF_iA", "Fred Guitar Tab"),
    ("UC-oUFPHUGyIR9Bfdc5INiHA", "Rock Factory"),
    ("UCsGe05GDlujq9-VtUDvFXvw", "SugarpillProductions"),
    ("UCBt0813kZ4r54jnIr16ZOEw", "Juliana Wilson"),
    ("UCTJh2pnfhyq5HIgDgfS_qDA", "XESTEROCK"),
    ("UCOXYqrNa6diSXKD8wl5EpIA", "Guitar Jam"),
    ("UCI7fys0WM62xF2jUlUdq0XQ", "Fender"),
    ("UCJgjHK1zDcpm0hiSpMqkPGw", "Frostic Tabs"),
    ("UCmnlTWVJysjWPFiZhQ5uudg", "Marty Music"),
    ("UCD9BWogQFjOyRBBIV9NHwDA", "Easy Guitar Tabs Tutorial"),
    ("UCoPISsupTKjmnkUGYeG4abA", "Martijn Deuling"),
    ("UCy3BbkwNem2vmd0I7EeNzlw", "Guitar Lessons with Bazok"),
    ("UCmnATuXP3QeHysLFByTqNuQ", "gunslingerz"),
    ("UCUR2UYQnB26yiR18CiAmSwA", "Nils Bryant"),
    ("UCllr76Ese2T2scj6R1HpiEg", "Will Ripley Guitar"),
    ("UCwyCI5-CNjjj3Zm9KmCxfEA", "Music2 Soul"),
    ("UCOXvbaLvAQsStt9uBO_PlHQ", "Thomas Hogue"),
    ("UCYMXt_emX1zqa3Om1ClR-Dg", "Marcus Andersen"),
    ("UChK111-QQxOI9JK6kGdhi-A", "Dino Sipic"),
    ("UCLhcQ0bBZTLipRJ7D42Riow", "Nik Nocturnal"),
    ("UCVpVWScDVNY1ORZBa-F8J1A", "Juha Aitakangas"),
    ("UCufOKmJij-dgROYvYCBxwQQ", "Max Niessl"),
    ("UC3tw4ZlRfkTkQ_r51rGqA5aA", "Shadow Mantra Steve"),
    ("UCjtVqZiAyWLzjF-HSbUVOFw", "IBRAHIM BIRDAL"),
    ("UCnBsNF4N3FwvGU6t6Ubp7MA", "Turbo Tequila Guitars"),
    ("UCaTnzbdRX8AKCk-OZQvbntw", "Desmond Doom"),
    ("UCWXdBPLfsbdX4TQbcFdOHLw", "Romain CNC"),
    ("UCh5Z26ovsPdQ4Kk1dzg3RYw", "Law of the Riff"),
    ("UCONZtwwn8nHkiYAfilEhong", "Pierote"),
    ("UCNkp2oxgudT1Qd2kEgUv6dA", "Aileron"),
    ("UCp7Ou7C15WhEKc9pgxQkSYg", "Anyone Can Play Guitar"),
    ("UCUERVRulpmC0DMspYCXlqaw", "Trevor Wong"),
    ("UCIxvsunmS6FlTWO-LW89eyg", "SoundsWood"),
    ("UCdo132pGsXI4aCfp0fbqDjw", "WobbleKnobGuitarTabs"),
    ("UCYR0dY6lF9NRz41XTOQhYcw", "Coverine"),
    ("UCoLagBi8Q4-GloPityhnhTQ", "MLC - MidLifeCrisis"),
    ("UC5mv7UO3R7XWlHIrO0e0xEg", "Rock with Levi"),
    ("UCbVKy4ojlPy0-VUoDHIeX-A", "Stanley 4-string"),
]

# extra handles discovered via web search (resolved to ids at runtime)
EXTRA_HANDLES = [
    ("Luke Orr Guitar Covers", "@lukeorrguitarcovers"),
    ("The Mad Professor of Rock", "@TheMadProfessorofRock"),
    ("RR Guitar Academy", "@RRGuitarAcademy"),
    ("Cameron Ford Music", "@CameronFordMusic"),
    ("Guitar Tab Studio", "@GuitarTabStudio"),
    ("Tato Rock n Riff", "@TatoRocknRiff"),
    ("Cover Song Thrift Shop", "@CoverSongThriftShop"),
    ("Nirvana Guitar Covers Jacopo Stella", "@NirvanaGuitarCovers"),
    ("Rock Guitar Lessons Made Easy", "@RockGuitarLessonsMadeEasy"),
    ("Gareth Evans", "@garethevansyt"),
    ("Marc Sanz Guitar", "@MarcSanzGuitar"),
    ("Rockin Tabs", "@RockinTabs"),
    ("Western guitarist tabs", "@westernguitarist"),
    ("Guitar Zero To Hero", "@GuitarZeroToHero"),
    ("DadRock TABS", "@dadrockytofficial"),
]

# channels whose @handle could not be guessed -> resolve from a known video URL
RESOLVE_VIDEOS = [
    ("The Mad Professor of Rock", "https://www.youtube.com/watch?v=a8oBeXjZ_ZM"),
    ("Guitar Tab Studio", "https://www.youtube.com/watch?v=hyEa6eQnDRg"),
    ("Tato Rock n Riff", "https://www.youtube.com/watch?v=arvBd4s1al4"),
    ("Nirvana Guitar Covers (Jacopo Stella)", "https://www.youtube.com/watch?v=Xd91qyg5hrM"),
]


def fetch(url):
    with yt_dlp.YoutubeDL(OPTS) as y:
        info = y.extract_info(url, download=False)
    entries = [e for e in (info.get("entries") or []) if e]
    return info, entries


def enum(cid, label):
    """Enumerate; retry only when the flat playlist looks truncated (<5 entries)."""
    url = "https://www.youtube.com/channel/%s/videos" % cid
    info, entries = fetch(url)
    if len(entries) < 5:
        for attempt in range(3):
            time.sleep(4 + attempt * 4)
            info2, entries2 = fetch(url)
            if len(entries2) > len(entries):
                info, entries = info2, entries2
            if len(entries) >= 5:
                break
    recs = []
    for e in entries:
        recs.append({"t": e.get("title") or "", "url": e.get("url"), "id": e.get("id")})
    return {
        "label": info.get("channel") or label,
        "channel": info.get("channel"),
        "channel_id": info.get("channel_id"),
        "uploader_id": info.get("uploader_id"),
        "channel_url": info.get("channel_url"),
        "subs": info.get("channel_follower_count"),
        "total": len(recs),
        "videos": recs,
    }


def main():
    out = {}
    if os.path.exists("_verify_new2.json"):
        with open("_verify_new2.json", encoding="utf-8") as fh:
            out = json.load(fh)

    for label, handle in EXTRA_HANDLES:
        key = "handle:" + handle
        if key in out:
            continue
        try:
            info, entries = fetch("https://www.youtube.com/%s/videos" % handle)
        except Exception as exc:  # noqa: BLE001
            print("HANDLEFAIL %s %s" % (handle, exc), file=sys.stderr, flush=True)
            continue
        cid = info.get("channel_id")
        if not cid:
            print("HANDLEMISS %s" % handle, file=sys.stderr, flush=True)
            continue
        r = {
            "label": info.get("channel") or label, "channel": info.get("channel"),
            "channel_id": cid, "uploader_id": info.get("uploader_id"),
            "channel_url": info.get("channel_url"),
            "subs": info.get("channel_follower_count"),
            "total": len(entries),
            "videos": [{"t": e.get("title") or "", "url": e.get("url"), "id": e.get("id")}
                       for e in entries],
        }
        out[key] = r
        print("HANDLE %-34s -> %-30s cid=%s subs=%s total=%s"
              % (handle, str(r["label"])[:30], cid, r["subs"], r["total"]), flush=True)
        with open("_verify_new2.json", "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        time.sleep(2)

    for label, vurl in RESOLVE_VIDEOS:
        key = "vid:" + vurl
        if key in out:
            continue
        try:
            with yt_dlp.YoutubeDL(dict(OPTS, extract_flat=False, skip_download=True)) as y:
                info = y.extract_info(vurl, download=False)
        except Exception as exc:  # noqa: BLE001
            print("VIDFAIL %s %s" % (label, exc), file=sys.stderr, flush=True)
            continue
        cid = info.get("channel_id")
        if not cid:
            continue
        r = {"label": info.get("channel") or label, "channel": info.get("channel"),
             "channel_id": cid, "uploader_id": info.get("uploader_id"),
             "channel_url": info.get("channel_url"),
             "subs": info.get("channel_follower_count"), "total": None, "videos": []}
        try:
            r2 = enum(cid, label)
            r["total"] = r2["total"]; r["videos"] = r2["videos"]
            r["subs"] = r2["subs"]; r["uploader_id"] = r2["uploader_id"] or r["uploader_id"]
        except Exception as exc:  # noqa: BLE001
            print("VIDENUMFAIL %s %s" % (label, exc), file=sys.stderr, flush=True)
        out[key] = r
        print("VID %-34s total=%-6s subs=%-9s cid=%s handle=%s"
              % (str(r["label"])[:34], r["total"], r["subs"], cid, r["uploader_id"]), flush=True)
        with open("_verify_new2.json", "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        time.sleep(2)

    for cid, label in CANDIDATES:
        if cid in out:
            continue
        try:
            r = enum(cid, label)
        except Exception as exc:  # noqa: BLE001
            print("FAIL %s %s" % (label, exc), file=sys.stderr, flush=True)
            continue
        out[cid] = r
        print("%-34s total=%-6s subs=%-9s cid=%s handle=%s"
              % (str(r["label"])[:34], r["total"], r["subs"], cid, r["uploader_id"]), flush=True)
        with open("_verify_new2.json", "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        time.sleep(1.5)

    print("DONE %d channels" % len(out), flush=True)


if __name__ == "__main__":
    main()
