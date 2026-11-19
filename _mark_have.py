# -*- coding: utf-8 -*-
"""Mark the research lists with "вече го имаме" (we already have a card for it).

Source of truth: songs.json (one card per song).

Outputs
  _have_map.json          video id -> {artist, title, channel} of our card
  _channel_lists/*.md     regenerated with a "Карта" column
  _artist_lists/*.md      regenerated with an "Имаме" column (how many of that artist's tab videos we cover)
  _artists_per_channel.md/.csv   regenerated with have-counts
  _oasis_by_song.md       regenerated with a "Карта" column

Matching rule (conservative, no false positives by default):
  a research video matches a card when
    1) the card title's word sequence appears in the video title, AND
    2) the card artist's words appear in the video title (leading "the" ignored)
  Cards with an artist that cannot be found in the title are ignored
  (no "song alone" guessing) -- the summary prints how many that leaves out.
"""
import collections
import csv
import json
import os
import re

R = os.path.dirname(os.path.abspath(__file__))
import _channels_all_dump as D
import _artists_per_channel as A

CHAN_DIR = os.path.join(R, "_channel_lists")
ART_DIR = os.path.join(R, "_artist_lists")

_WORD = re.compile(r"[a-z0-9]+")
_ART_STOP = {"the", "a"}


def toks(s):
    return _WORD.findall((s or "").lower())


def art_toks(s):
    return [t for t in toks(s) if t not in _ART_STOP]


def seq_in(seq, sub):
    """True if sub (list) appears as a contiguous subsequence of seq (list)."""
    n, m = len(seq), len(sub)
    if m == 0 or m > n:
        return False
    first = sub[0]
    for i in range(n - m + 1):
        if seq[i] == first and seq[i:i + m] == sub:
            return True
    return False


def safe(name):
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")
    return s or "channel"


# ---------------------------------------------------------------- cards ----
_QUAL = re.compile(r"\s*[\(\[][^\)\]]*[\)\]]\s*$")


def load_cards():
    data = json.load(open(os.path.join(R, "songs.json"), encoding="utf-8"))
    cards = []
    for s in data:
        title = (s.get("title") or "").strip()
        artist = (s.get("artist") or "").strip()
        ct = toks(title)
        if not ct:
            continue
        at = art_toks(artist)
        # a card title may carry a qualifier: "Bad Moon Rising (Easy Chords)"
        # the research videos use the bare song name -> keep a second variant
        variants = [ct]
        base = toks(_QUAL.sub("", title))
        if base and base != ct:
            variants.append(base)
        cards.append({
            "artist": artist,
            "title": title,
            "at": at,
            "key": max(at, key=len) if at else "",
            "ct": ct,
            "variants": variants,
            "channel": s.get("channel", ""),
            "youtube_id": s.get("youtube_id", ""),
        })
    return cards


# --------------------------------------------------------------- match ----
def build_matches(cards, videos):
    """videos: list of (channel, title, url) -> {video_index: card}"""
    # document frequency over video titles
    df = collections.Counter()
    vtoks = []
    for _ch, title, _url in videos:
        t = toks(title)
        vtoks.append(t)
        for w in set(t):
            df[w] += 1

    matches = {}
    probable = {}
    unmatched = []
    for i, (_ch, title, _url) in enumerate(videos):
        t = vtoks[i]
        tset = set(t)
        hit = None
        for c in cards:
            ok = False
            for v in c["variants"]:
                if all(w in tset for w in v) and seq_in(t, v):
                    ok = True
                    break
            if not ok:
                continue
            # strict: the artist must be named in the video title.
            # ("song alone" guessing produced false positives -- some channels
            #  publish covers under a wrong artist name.)
            if c["at"] and not (all(w in tset for w in c["at"]) or c["key"] in tset):
                continue
            hit = c
            break
        if hit:
            matches[i] = hit
        else:
            unmatched.append(i)
    return matches, probable, unmatched


def _distinctive(card):
    """Song name specific enough to be a safe guess without the artist."""
    v = card["variants"][-1]
    if len(v) < 2:
        return False
    return sum(len(w) for w in v) >= 10


# ------------------------------------------------------- channel lists ----
def write_channel_lists(videos, matches, probable):
    by_ch = collections.defaultdict(list)
    for i, (ch, title, url) in enumerate(videos):
        by_ch[ch].append((i, title, url))

    order = sorted(by_ch.items(), key=lambda kv: -len(kv[1]))
    index = []
    for label, items in order:
        fn = "%s.md" % safe(label)
        lines = ["# %s" % label, "",
                 "Всички видеа от канала (%d). Флагове: TAB / COVER / BASS / жанр." % len(items), "",
                 "`✅` = вече имаме карта за тази песен (в коятото и да е канал).", "",
                 "| # | Видео | Флагове | Карта |", "|---|---|---|---|"]
        have = 0
        for n, (i, title, url) in enumerate(items, 1):
            t = re.sub(r"\s+", " ", title).strip().replace("|", "\\|")
            fl = " ".join(D.flags(title))
            c = matches.get(i)
            if c:
                have += 1
                mark = "✅ %s — %s" % (c["artist"], c["title"])
            elif i in probable:
                have += 1
                mark = "🎯 %s — %s" % (probable[i]["artist"], probable[i]["title"])
            else:
                mark = "—"
            lines.append("| %d | [%s](%s) | %s | %s |" % (n, t, url, fl, mark))
        with open(os.path.join(CHAN_DIR, fn), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        tab = sum(1 for _i, title, _u in items if D.TAB_RE.search(title))
        index.append((label, len(items), tab, have, fn))

    index.sort(key=lambda x: -x[1])
    with open(os.path.join(CHAN_DIR, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("# Индекс на каналите\n\n")
        f.write("`Имаме` = брой видеа в канала, за които вече имаме карта.\n\n")
        f.write("| # | Канал | Видеа | С tab | Имаме | Файл |\n|---|---|---|---|---|---|\n")
        for i, (label, tot, tab, have, fn) in enumerate(index, 1):
            f.write("| %d | %s | %d | %d | %d | [%s](%s) |\n" % (i, label, tot, tab, have, fn, fn))
    return index


# ------------------------------------------------------- artist lists ----
def write_artist_lists(videos, matches, probable):
    by_ch = collections.defaultdict(list)
    for i, (ch, title, url) in enumerate(videos):
        by_ch[ch].append((i, title, url))

    order = sorted(by_ch.items(), key=lambda kv: -len(kv[1]))
    index = []
    for label, items in order:
        tabv = [(i, t, u) for (i, t, u) in items if D.TAB_RE.search(t)]
        if not tabv:
            continue
        cnt = collections.Counter()
        for i, t, _u in tabv:
            a = A.artist_of(t) or "(непознат)"
            cnt[a] += 1
        fn = "%s.md" % safe(label)
        lines = ["# %s" % label, "",
                 "Видеа с tab по артист (общо %d). `Имаме` = колко от тях вече имаме карта." % len(tabv), "",
                 "| # | Артист | Видеа с tab | Имаме |", "|---|---|---|---|"]
        have_by_artist = collections.Counter()
        for i, t, _u in tabv:
            if i in matches or i in probable:
                have_by_artist[A.artist_of(t) or "(непознат)"] += 1
        for n, (a, n2) in enumerate(cnt.most_common(), 1):
            h = have_by_artist.get(a, 0)
            lines.append("| %d | %s | %d | %s |" % (n, a.replace("|", "\\|"), n2,
                                                    ("✅ %d" % h) if h else "—"))
        with open(os.path.join(ART_DIR, fn), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        index.append((label, len(tabv), len(cnt), sum(have_by_artist.values()), fn))

    index.sort(key=lambda x: -x[1])
    with open(os.path.join(ART_DIR, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("# Индекс: артисти по канал\n\n")
        f.write("`Имаме` = брой видеа с tab от този артист, за които вече имаме карта.\n\n")
        f.write("| # | Канал | Tab видеа | Артисти | Имаме | Файл |\n|---|---|---|---|---|---|\n")
        for i, (label, tabv, arts, have, fn) in enumerate(index, 1):
            f.write("| %d | %s | %d | %d | %d | [%s](%s) |\n" % (i, label, tabv, arts, have, fn, fn))
    return index


# ------------------------------------------------- artists per channel ----
def write_artists_per_channel(videos, matches, probable):
    by_ch = collections.defaultdict(list)
    for i, (ch, title, url) in enumerate(videos):
        by_ch[ch].append((i, title, url))

    all_counts = {}
    have_counts = {}
    for label, items in by_ch.items():
        tabv = [(i, t, u) for (i, t, u) in items if D.TAB_RE.search(t)]
        if not tabv:
            continue
        c = collections.Counter()
        h = collections.Counter()
        for i, t, _u in tabv:
            a = A.artist_of(t) or "(непознат)"
            c[a] += 1
            if i in matches or i in probable:
                h[a] += 1
        all_counts[label] = c
        have_counts[label] = h

    folded = collections.defaultdict(lambda: [0, collections.Counter()])
    for label, c in all_counts.items():
        for a, n in c.items():
            f = a.casefold()
            folded[f][0] += n
            folded[f][1][a] += n
    canon = {f: forms.most_common(1)[0][0] for f, (_t, forms) in folded.items()}

    out_md = ["# Разпределение по артист — всички канали\n",
              "`Имаме` = брой видеа с tab от този артист, за които вече имаме карта.\n"]
    csv_rows = []
    for label, c in sorted(all_counts.items(), key=lambda kv: -sum(kv[1].values())):
        merged = collections.Counter()
        merged_h = collections.Counter()
        for a, n in c.items():
            merged[canon[a.casefold()]] += n
        for a, n in have_counts.get(label, {}).items():
            merged_h[canon[a.casefold()]] += n
        out_md.append("## %s — %d видеа с tab, %d различни артисти" % (label, sum(c.values()), len(c)))
        out_md.append("")
        out_md.append("| # | Артист | Видеа с tab | Имаме |")
        out_md.append("|---|---|---|---|")
        for i, (a, n) in enumerate(merged.most_common(), 1):
            h = merged_h.get(a, 0)
            out_md.append("| %d | %s | %d | %s |" % (i, a.replace("|", "\\|"), n,
                                                    ("✅ %d" % h) if h else "—"))
            csv_rows.append([label, a, n, h])
        out_md.append("")

    with open(os.path.join(R, "_artists_per_channel.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out_md))
    with open(os.path.join(R, "_artists_per_channel.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["channel", "artist", "tab_videos", "have"])
        w.writerows(csv_rows)
    return csv_rows


# --------------------------------------------------------------- oasis ----
def write_oasis_by_song(matches, probable, videos, cards):
    p = os.path.join(R, "_oasis_videos.csv")
    if not os.path.exists(p):
        return
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    per = collections.defaultdict(collections.Counter)
    tabs = collections.defaultdict(collections.Counter)
    for x in rows:
        s = _oasis_song(x["title"]) or "(друго)"
        per[s][x["channel"]] += 1
        if x.get("has_tab") == "да":
            tabs[s][x["channel"]] += 1

    # a card for an Oasis song covers the research song key when the key's
    # words are contained in the card title (the extractor truncates to 4 words)
    oasis_cards = [c for c in cards if "oasis" in c["at"]]
    have = {}
    for s in per:
        st = set(toks(s))
        if not st:
            continue
        for c in oasis_cards:
            ct = set(c["ct"])
            if st <= ct or ct <= st:
                have[s] = c["title"]
                break
    out = ["# Oasis — разбивка по песен\n",
           "`✅` = вече имаме карта за тази песен.\n",
           "| Песен | Видеа | С tab | Канали | Карта |", "|---|---|---|---|---|"]
    for s in sorted(per, key=lambda k: (-sum(tabs[k].values()), -sum(per[k].values()))):
        tot, tt = sum(per[s].values()), sum(tabs[s].values())
        chs = ", ".join("%s(%d)" % (c[:16], n) for c, n in per[s].most_common(4))
        mark = "✅" if s in have else "—"
        out.append("| %s | %d | %d | %s | %s |" % (s, tot, tt, chs, mark))
    with open(os.path.join(R, "_oasis_by_song.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def _oasis_song(title):
    import _oasis_by_song as OB
    return OB.song(title)


def main():
    data = D.load()
    videos = []
    for label, vids in data.items():
        for v in vids:
            videos.append((label, v.get("t", ""), v.get("url", "")))
    print("channels: %d   videos: %d" % (len(data), len(videos)))

    cards = load_cards()
    print("cards: %d" % len(cards))

    matches, probable, unmatched = build_matches(cards, videos)
    print("matched videos: %d exact + %d probable / %d (%.1f%%)" % (
        len(matches), len(probable), len(videos),
        100.0 * (len(matches) + len(probable)) / max(1, len(videos))))

    os.makedirs(CHAN_DIR, exist_ok=True)
    os.makedirs(ART_DIR, exist_ok=True)

    idx = write_channel_lists(videos, matches, probable)
    print("channel files: %d   covered: %d" % (len(idx), sum(x[3] for x in idx)))

    aidx = write_artist_lists(videos, matches, probable)
    print("artist files: %d   covered tab videos: %d" % (len(aidx), sum(x[3] for x in aidx)))

    rows = write_artists_per_channel(videos, matches, probable)
    print("artists_per_channel rows: %d   have>0: %d" % (len(rows), sum(1 for r in rows if r[3])))

    write_oasis_by_song(matches, probable, videos, cards)

    # machine-readable map
    mp = {}
    for i, (ch, title, url) in enumerate(videos):
        if i in matches:
            mp[url] = {"channel": ch, "title": title, "match": "exact",
                       "card_artist": matches[i]["artist"],
                       "card_title": matches[i]["title"]}
        elif i in probable:
            mp[url] = {"channel": ch, "title": title, "match": "probable",
                       "card_artist": probable[i]["artist"],
                       "card_title": probable[i]["title"]}
    with open(os.path.join(R, "_have_map.json"), "w", encoding="utf-8") as f:
        json.dump(mp, f, ensure_ascii=False, indent=1)
    print("have_map: %d entries" % len(mp))

    # top artists we already cover
    have_art = collections.Counter()
    for c in matches.values():
        have_art[c["artist"]] += 1
    print("\nTop artists we already cover:")
    for a, n in have_art.most_common(25):
        print("  %-28s %d" % (a, n))


if __name__ == "__main__":
    main()
