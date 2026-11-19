# -*- coding: utf-8 -*-
"""Distribute every channel's tab videos BY ARTIST.

Title patterns handled:
  'Song - Artist - Guitar + Bass TABS Lesson'      (DadRock)
  'Artist - Song | Cover | Tutorial | Lesson'       (Godderdy)
  'Artist - Song (guitar cover & chords)'           (guitar cover with tabs)
  'Song by Artist | Guitar Lesson'                  (Let's Play All / Marty Music)
  '【Artist】[ Song ] cover by X | LESSON | GUITAR TAB' (Dotti Brothers)
  'Artist Song Guitar Lesson / Guitar Tab ...'      (CWZ)
"""
import collections
import csv
import json
import os
import re

R = os.path.dirname(os.path.abspath(__file__))
import _channels_all_dump as D

ARTISTS = [
    # --- 90s grunge / alt ---
    "Nirvana", "Pearl Jam", "Soundgarden", "Alice In Chains", "Stone Temple Pilots",
    "Hole", "Mudhoney", "Screaming Trees", "Melvins", "Dinosaur Jr", "Sebadoh",
    "Hokum", "Mad Season", "The Fray", "Veruca Salt", "Garbage", "Temple Of The Dog",
    "Chavez", "Tad", "L7", "Hole", "The Melvins", "Malice N Forgery", "Bush",
    "Radiohead", "Smashing Pumpkins", "Foo Fighters", "Oasis", "Blur", "Beck",
    "Weezer", "Blink-182", "Sum 41", "The Cranberries", "Counting Crows",
    "Third Eye Blind", "Gin Blossoms", "Sister Hazel", "Travis", "Keane", "Coldplay",
    "The Killers", "Arctic Monkeys", "Kaiser Chiefs", "The Strokes", "Royal Blood",
    "The White Stripes", "Simple Plan", "Silverchair", "Incubus", "Nine Inch Nails",
    "A Perfect Circle", "Muse", "Placebo", "Garbage", "Republica", "Echouse",
    "Daria Nikiforov", "Papa Roach", "Pulp", "The Verve", "The Cranberries",
    "Guided By Voices", "Stereophonics", "Ash", "Dodgy", "Supergrass", "The Verve",
    "Chris Cornell", "Mark Lanegan", "Scott Weiland", "Josh Homme", "Dave Grohl",
    # --- punk / hardcore ---
    "Ramones", "Bad Religion", "Misfits", "Sex Pistols", "Descendents", "Rancid",
    "Green Day", "NOFX", "Dead Kennedys", "The Germs", "The Clash", "The Damned",
    "Social Distortion", "Dropkick Murphys", "The Offspring", "Lagwagon",
    "Anti-Flag", "Minor Threat", "Dillinger Four", "Teenage Bottlerocket", "MxPx",
    "Toxic Reason", "Rise Against", "Propagandhi", "NOFX", "Pennywise", "The Damned",
    "Bad Brains", "Black Flag", "Exploited", "Joy Division", "Siouxsie",
    "The Exploited", "Cro Mags", "The Business", "Choking Victim", "Impaled Nazarene",
    "Backfire", "Real Kids", "Jigsaw", "Napalm Death", "Hellbastards", "D.R.I",
    # --- metal / hard rock ---
    "Metallica", "Iron Maiden", "Black Sabbath", "Slayer", "Megadeth", "Slipknot",
    "Pantera", "System Of A Down", "Korn", "Deftones", "Tool", "Disturbed",
    "Motörhead", "Rammstein", "Ghost", "Sepultura", "Anthrax", "Testament",
    "Exodus", "Judas Priest", "Led Zeppelin", "Dio", "Motley Crue", "Gun N' Roses",
    "Guns N' Roses", "Def Leppard", "Scorpions", "Van Halen", "Whitesnake",
    "Aerosmith", "Bon Jovi", "Avenged Sevenfold", "Arch Enemy", "Children Of Bodom",
    "Kiss", "Accept", "Dokken", "Ratt", "Ozzy Osbourne", "Racer X", "King Diamond",
    "Dream Theater", "Tesla", "Slash", "Daron Malakian", "Scars", "Scar Tissue",
    "Limp Bizkit", "Rob Zombie", "Emigrate", "Chevelle", "Hatebreed", "Marilyn Manson",
    "Till Lindemann", "Lindemann", "Ministry", "Static-X", "P.O.D.", "Godsmack",
    "Alice In Chains", "Stone Sour", "Soulfly", "Trivium", "In Flames", "Volbeat",
    "Opeth", "Meshuggah", "Gojira", "Suidakra", "Carcass", "Cynic",
    "Fear Factory", "Living Colour", "Suicidal Tendencies", "Mushroomhead",
    "Drowning Pool", "Coal Chamber", "Helmet", "Quicksand", "Monster Magnet",
    "Sleep", "Kyuss", "Monster Magnet", "Clutch", "Baroness", "Mastodon",
    "Lamb Of God", "Children Of Bodom", "The Warning", "Billy Talent",
    "Queens Of The Stone Age", "A Perfect Circle", "Godsmack", "Bad Wolves",
    "Bush", "Velvet Revolver", "Raimundos", "Papa Roach", "Eisbrecher",
    "Darkthrone", "Burzum", "Mayhem", "Watain", "Behemoth", "Immortal",
    # --- classic rock / 70-80s ---
    "Queen", "Pink Floyd", "AC/DC", "Journey", "Foreigner", "Boston", "Deep Purple",
    "Rush", "Heart", "Cheap Trick", "Blue Oyster Cult", "Eagles", "Lynyrd Skynyrd",
    "ZZ Top", "Styx", "Kansas", "Joe Satriani", "Steve Vai", "Dire Straits",
    "Thin Lizzy", "The Doors", "The Cult", "Stevie Ray Vaughan", "Jimi Hendrix",
    "Gary Moore", "Joe Bonamassa", "Van Morrison", "Creed", "Third Eye Down",
    "Aerosmith", "Scorpions", "Bon Jovi", "Free", "Bad Company", "Rainbow",
    "Black Sabbath", "Motley Crue", "Whitesnake", "UFO", "Twisted Sister",
    "Mötley Crüe", "Golden Earring", "Golden Earring", "Status Quo", "Slade",
    "Deep Purple", "Yes", "Genesis", "King Crimson", "Jethro Tull", "Wishbone Ash",
    "Budgie", "Krokus", "U.D.O.", "Triumph", "Pat Travers", "Michael Schenker",
    "Skid Row", "W.A.S.P.", "Rory Gallagher", "Eric Clapton", "Slash w/ Myles Kennedy",
    "Myles Kennedy", "Derek Sherinian", "Zakk Wylde", "Ozzy", "Sabbath",
    # --- alt/indie/pop-rock 90s+ ---
    "Red Hot Chili Peppers", "The Smiths", "Tame Impala", "Depeche Mode",
    "The Beatles", "Beatles", "Elvis", "Elvis Presley", "Johnny Cash",
    "Taylor Swift", "Ed Sheeran", "Michael Jackson", "Bruno Mars", "Adele",
    "Beyonce", "Ozzy Osbourne", "The Killers", "Bring Me The Horizon",
    "Linkin Park", "Limp Bizkit", "Three Days Grace", "Evanescence",
    "Evans Blue", "Hoobastank", "Incubus", "Sum 41", "Simple Plan",
    "Blink 182", "Good Charlotte", "Bowling for Soup", "New Found Glory",
    "The Used", "My Chemical Romance", "Fall Out Boy", "Panic At The Disco",
    "Thirty Seconds To Mars", "Imagine Dragons", "OneRepublic", "Maroon 5",
    "Sheryl Crow", "Bonnie Raitt", "Alanis Morissette", "Alanis", "Savage Garden",
    "Evanescence", "Hoobastank", "Cold", "Seether", "Creed", "Bush",
    "Vertical Horizon", "Fuel", "Days Of The New", "Matchbox Twenty",
    "Collective Soul", "Third Eye Blind", "Goo Goo Dolls", "Semisonic",
    "Fastball", "Everclear", "Weezer", "Offspring", "Blink", "Sum",
    "Smash Mouth", "Alien Ant Farm", "Lit", "Puddle Of Mudd", "Saliva",
    "Godsmack", "Staind", "Incubus", "Korn", "Deftones", "Rage Against The Machine",
    "Rage Against The Machine", "Audioslave", "System Of A Down", "Queens Of The Stone Age",
    "The Offspring", "The Verve", "The Cranberries", "Silverchair",
    # --- misc / artists seen in the dumps ---
    "Slash w/ Myles Kennedy", "W.A.S.P.", "Rory Gallagher", "Tesla", "Skid Row",
    "Accept", "Ratt", "Dokken", "King Diamond", "Racer X", "Ozzy Osbourne",
    "The Cult", "The Doors", "Dream Theater", "Ice Nine Kills", "Lorna Shore",
    "Daria Nikiforov", "Ichika Nito", "Buckethead", "Paul Gilbert",
    "Nolly Getgood", "Devin Townsend", "Marty Friedman", "Marty",
    "Eric Johnson", "Joe Satriani", "Steve Vai", " Guthrie Govan", "Andy Timmons",
    "Frank Gambale", "Al Di Meola", "John Petrucci", "Steve Morse", "Ritchie Blackmore",
    "Gary Moore", "Stevie Ray Vaughan", "Michael Schenker", "Uli Jon Roth",
    "Scorpions", "Kane Robertson", "Mick Mars", "Mötley Crüe", "Poison", "Skid Row",
    "Alice Cooper", "Shockwave", "Twisted Sister", "Dee Snider", "Ratt",
    "Motörhead", "Ace Frehley", "Doro", "Kiske", "Bon Jovi", "Richie Sambora",
    "Doc Holliday", "Lynch Mob", "Ratt", "Firewind", "Kamelot", "Symphony X",
    "Nevermore", "Arch Enemy", "Eluveitie", "In Flames", "Soilwork", "Dark Tranquillity",
    "Hyperborea", "Rotting Christ", "Mayhem", "Watain",
]

# longest first so 'Alice In Chains' wins over 'Alice'
ARTISTS.sort(key=len, reverse=True)
ART_RE = re.compile("|".join(re.escape(a) for a in ARTISTS), re.I)

NOISE = re.compile(
    r"\b(tab|tabs|guitar|bass|lesson|tutorial|cover|song|chords?|strumming|play|"
    r"how|to|the|by|full|breakdown|version|official|audio|hd|mv|remastered|"
    r"instrumental|performance|session|demo|part|vol|no\.\d+)\b", re.I)


JUNK = {"solo", "riff", "riffs", "mix", "top", "full", "part", "intro", "outro", "lesson",
        "guitar", "bass", "tab", "tabs", "cover", "song", "chords", "unknown", "unknownartist"}


def clean_artist(s):
    s = re.sub(r"[【】\[\]（）()]", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" -|,")
    s = NOISE.sub(" ", s).strip(" -|,")
    s = re.sub(r"\s{2,}", " ", s)
    if s.casefold() in JUNK:
        return ""
    return s


def artist_of(title):
    t = re.sub(r"\s+", " ", (title or "")).strip()
    if not t:
        return None
    # 2) 【ARTIST】 — must win over "by X" (Dotti: "【NIRVANA】[ In Bloom ] cover by Masuka")
    m = re.search(r"[【\[]([^】\]]{2,40})[】\]]", t)
    if m:
        a = clean_artist(m.group(1))
        if a:
            return a
    # 1) explicit "by ARTIST"
    m = re.search(r"\bby\s+(.+?)(?:\s*\||\s+-|$)", t, re.I)
    if m:
        a = clean_artist(m.group(1))
        if 2 <= len(a) <= 40:
            return a
    # 3) known artist anywhere
    m = ART_RE.search(t)
    if m:
        a = clean_artist(m.group(0))
        if a:
            return a
    # 4) "A - B - <instrumental cue>"  -> A = song, B = artist  (DadRock)
    parts = [p.strip() for p in t.split(" - ") if p.strip()]
    if len(parts) >= 3 and re.search(r"guitar|bass|tabs?", parts[-1], re.I):
        a = clean_artist(parts[1])
        if a:
            return a
    # 5) "A - B" -> artist is the shorter/more artist-like part
    if len(parts) >= 2:
        cands = [clean_artist(p) for p in parts[:2]]
        cands = [c for c in cands if c]
        if cands:
            cands.sort(key=len)
            return cands[0]
    # 6) "ARTIST SONG Guitar Lesson ..." -> tokens before the instrument cue
    m = re.match(r"^(.*?)\s+(guitar|bass)\b", t, re.I)
    if m:
        head = clean_artist(m.group(1))
        if head:
            words = head.split()
            # keep 1..4 leading words that are not the song title
            return " ".join(words[:4]) if len(words) > 4 else head
    # 7) fallback: first 3 words
    head = clean_artist(t.split(" - ")[0])
    words = head.split()
    return " ".join(words[:3]) if words else None


def normalise(counts):
    """Fold case-only duplicates (KISS/Kiss, RUSH/Rush) into the top spelling."""
    folded = collections.defaultdict(lambda: [0, collections.Counter()])
    for a, n in counts.items():
        f = a.casefold()
        folded[f][0] += n
        folded[f][1][a] += n
    out = []
    for f, (total, forms) in folded.items():
        best = forms.most_common(1)[0][0]
        out.append((best, total))
    return out


def main():
    data = D.load()
    all_counts = {}
    ranked = sorted(data.items(), key=lambda kv: -sum(
        1 for v in kv[1] if D.TAB_RE.search(v.get("t", ""))))

    for label, vids in ranked:
        tabv = [v for v in vids if D.TAB_RE.search(v.get("t", ""))]
        if not tabv:
            continue
        c = collections.Counter()
        for v in tabv:
            a = artist_of(v.get("t", "")) or "(непознат)"
            c[a] += 1
        all_counts[label] = c

    out_md = ["# Разпределение по артист — всички канали\n"]
    csv_rows = []
    # global case-fold so METALLICA (TAB 'EM ALL) merges with Metallica (DadRock)
    folded = collections.defaultdict(lambda: [0, collections.Counter()])
    for label, c in all_counts.items():
        for a, n in c.items():
            f = a.casefold()
            folded[f][0] += n
            folded[f][1][a] += n
    canon = {f: forms.most_common(1)[0][0] for f, (t, forms) in folded.items()}

    for label, c in all_counts.items():
        tabv = [v for v in data[label] if D.TAB_RE.search(v.get("t", ""))]
        merged = collections.Counter()
        for a, n in c.items():
            merged[canon[a.casefold()]] += n
        c = merged
        out_md.append("## %s — %d видеа с tab, %d различни артисти" % (label, len(tabv), len(c)))
        out_md.append("")
        out_md.append("| # | Артист | Видеа с tab |")
        out_md.append("|---|---|---|")
        for i, (a, n) in enumerate(c.most_common(), 1):
            out_md.append("| %d | %s | %d |" % (i, a.replace("|", "\\|"), n))
            csv_rows.append([label, a, n])
        out_md.append("")

    with open(os.path.join(R, "_artists_per_channel.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out_md))
    with open(os.path.join(R, "_artists_per_channel.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["channel", "artist", "tab_videos"])
        w.writerows(csv_rows)
    print("channels: %d   rows: %d" % (len(ranked), len(csv_rows)))
    print("\n".join(out_md[:150]))


if __name__ == "__main__":
    main()
