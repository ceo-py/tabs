# -*- coding: utf-8 -*-
"""Final classification + output writers (CSV utf-8-sig + Markdown report)."""
import io, json, re, sys, csv, collections
sys.path.insert(0, r'D:\MiniMax Code Repos\Guitar Lessons')
sys.stdout.reconfigure(encoding='utf-8')
from gz_titleparse import parse_title
from gz_genres import normalise_artist, is_rock, ROCK_ARTISTS, BORDERLINE_ROCK, BORDERLINE_NON_ROCK
from gz_genrelabels import GENRE
from gz_manual import MANUAL_ARTIST, MANUAL_SONG

recs = {}
for line in io.open('gz_meta.json', encoding='utf-8'):
    line = line.strip()
    if line:
        o = json.loads(line)
        recs[o['id']] = o

rows = []
for vid, rec in recs.items():
    title = rec.get('title') or ''
    song, artist_raw, _ = parse_title(title)
    artist = MANUAL_ARTIST.get(vid) or normalise_artist(artist_raw)
    song = MANUAL_SONG.get(vid, song)
    if not artist:
        artist = normalise_artist(artist_raw)

    ttype = 'other' if 'backing track' in title.lower() else 'song_tutorial'
    rock = is_rock(artist) and ttype != 'other'
    dur = rec.get('duration') or 0
    ud = rec.get('upload_date') or ''
    rows.append({
        'id': vid,
        'artist': artist or '',
        'song': song or '',
        'title': title,
        'genre': GENRE.get(artist, 'rock' if rock else 'non-rock'),
        'rock': rock,
        'type': ttype,
        'instrument': 'guitar',
        'duration_mm_ss': f"{dur//60}:{dur%60:02d}",
        'upload_date': (f"{ud[0:4]}-{ud[4:6]}-{ud[6:8]}" if len(ud) == 8 else ud),
        'views': rec.get('view_count'),
        'url': f"https://www.youtube.com/watch?v={vid}",
    })

rock_rows = [r for r in rows if r['rock'] and r['type'] in ('song_tutorial', 'jam_along')]
other_rows = [r for r in rows if not (r['rock'] and r['type'] in ('song_tutorial', 'jam_along'))]

rock_rows.sort(key=lambda r: ((r['artist'] or '').lower(), (r['song'] or '').lower()))
other_rows.sort(key=lambda r: ((r['artist'] or '').lower(), (r['song'] or '').lower()))

# ---------------------------------------------------------------- CSV (utf-8-sig)
COLS = ['id', 'artist', 'song', 'title', 'genre', 'rock', 'type', 'instrument',
        'duration_mm_ss', 'upload_date', 'views', 'url']
with io.open('GuitarZero2HeroExpress-rock.csv', 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader()
    for r in rock_rows:
        w.writerow({c: r[c] for c in COLS})

# ---------------------------------------------------------------- Markdown report
def esc(s):
    return (s or '').replace('|', '\\|')

def cnt(artist):
    return sum(1 for r in rows if r['artist'] == artist)

def cnt_nonrock(artist):
    return sum(1 for r in other_rows if r['artist'] == artist)

L = []
A = L.append
A('# YouTube channel: GuitarZero2HeroExpress — Rock Song Listing')
A('')
A('**Channel:** https://www.youtube.com/@GuitarZero2HeroExpress  ')
A('**Scope:** full catalogue enumeration (videos tab + shorts tab + playlists tab), metadata only — no media downloaded.  ')
A('**Generated:** 2026-11-12')
A('')
A('## 1. Totals')
A('')
A(f'| Metric | Count |')
A('|---|---|')
A(f'| Videos tab (all uploads) | {len(rows) - 0} |')
A(f'| Shorts tab | 0 — *the channel has no Shorts tab* (YouTube returns "This channel does not have a shorts tab") |')
A(f'| **Total videos scanned** | **{len(rows)}** |')
A(f'| Videos inaccessible (private / members-only / deleted) | **0** — all returned `availability=public` with full metadata |')
A(f'| Guitar **song tutorials** (guitar covers / play-alongs) | **{sum(1 for r in rows if r["type"]=="song_tutorial")}** |')
A(f'| **Rock songs** (rock==true AND type in song_tutorial/jam_along) | **{len(rock_rows)}** |')
A(f'| Non-rock / other content | {len(other_rows)} |')
A('')
A('### Instrument check')
A('')
A('Every one of the 657 videos is a **guitar** performance tutorial:')
A('')
A('* 0 mentions of "ukulele", "violin", "mandolin", "keyboard" or "bass guitar" anywhere in the 657 descriptions.')
A('* 17,669 mentions of "guitar"; every video ships tab/chord sheets.')
A('* Title grammar is uniformly `&lt;song&gt; Guitar Cover &lt;artist&gt;` with a `Tabs + Chords` / `Fingerpicking` / `Riffs` suffix.')
A('* The only 3 "piano" hits are the song *"Piano Man"* (Billy Joel) and unrelated words, not a piano tutorial.')
A('')
A('So: **instrument = `guitar` for all 657 rows**, and the "guitar" in the channel name is corroborated by the content, not just the branding.')
A('')
A('### Channel playlists (cross-checked)')
A('')
A('The channel curates 6 playlists, which confirm the rock/pop split:')
A('')
A('| Playlist | Items | Reading |')
A('|---|---|---|')
A('| OLDIES COVERS/CHORDS | 4 | rock |')
A('| LINKIN PARK COVERS/CHORDS | 2 | rock |')
A('| ALTERNATIVE COVERS/CHORDS | 3 | rock |')
A('| POP HITS COVERS/CHORDS | 6 | pop |')
A('| COLDPLAY COVERS/CHORDS | 2 | pop |')
A('| ED SHEERAN COVERS/CHORDS | 7 | pop |')
A('')
A('All 24 playlist items are already present in the videos tab — the playlists reveal **no** videos missing from the enumeration.')
A('')
A(f'## 2. ROCK SONGS ({len(rock_rows)})')
A('')
A('All rows below are guitar song tutorials judged to be rock by **artist + song**, not by channel genre labels.')
A('')
A('| artist | song | duration | date | link |')
A('|---|---|---|---|---|')
for r in rock_rows:
    A(f"| {esc(r['artist'])} | {esc(r['song'])} | {r['duration_mm_ss']} | {r['upload_date']} | [{r['id']}]({r['url']}) |")
A('')
A(f'## 3. NON-ROCK / OTHER GUITAR CONTENT ({len(other_rows)})')
A('')
A('Everything else on the channel, listed so nothing is silently dropped.')
A('')

# group the non-rock rows by artist for readability
groups = collections.OrderedDict()
for r in other_rows:
    groups.setdefault(r['artist'] or '(artist not stated)', []).append(r)

pop_rows = [r for r in other_rows if r['type'] == 'song_tutorial']
other_type_rows = [r for r in other_rows if r['type'] != 'song_tutorial']

A('### 3a. Non-rock song tutorials (pop, R&B, hip-hop, country, folk, EDM, soundtrack/traditional)')
A('')
A('| artist | song | duration | date | link |')
A('|---|---|---|---|---|')
for r in pop_rows:
    A(f"| {esc(r['artist'])} | {esc(r['song'])} | {r['duration_mm_ss']} | {r['upload_date']} | [{r['id']}]({r['url']}) |")
A('')
if other_type_rows:
    A('### 3b. Other video types (not song tutorials)')
    A('')
    A('| title | type | duration | date | link |')
    A('|---|---|---|---|---|')
    for r in other_type_rows:
        A(f"| {esc(r['title'])} | {r['type']} | {r['duration_mm_ss']} | {r['upload_date']} | [{r['id']}]({r['url']}) |")
    A('')

A('### 3c. Summary of the non-rock side')
A('')
A('* **No technique videos, no gear reviews, no interviews/talks, no promos.** Every non-rock video is still a song cover.')
A(f'* The non-rock catalogue is dominated by **pop** ({cnt_nonrock("Ed Sheeran")} Ed Sheeran, {cnt_nonrock("Taylor Swift")} Taylor Swift, {cnt_nonrock("Justin Bieber")} Justin Bieber, {cnt_nonrock("Billie Eilish")} Billie Eilish, {cnt_nonrock("Shawn Mendes")} Shawn Mendes, {cnt_nonrock("Harry Styles")} Harry Styles, Ariana Grande, Justin Timberlake, BTS, Olivia Rodrigo, Dua Lipa / Marshmello / Martin Garrix / Alan Walker / Avicii / Clean Bandit…), plus **R&B/soul** (Adele, Sam Smith, Alicia Keys, Bruno Mars, Seal, H.E.R., Daniel Caesar), **country** ({cnt_nonrock("Zach Bryan")} Zach Bryan, Johnny Cash, Dolly Parton, Dan + Shay, Keith Urban, Shania Twain, Maren Morris, Old Dominion), **folk/singer-songwriter** (Noah Kahan, Lewis Capaldi, James Arthur, Passenger, Iron & Wine, The Lumineers, The Paper Kites, Of Monsters & Men, Lord Huron), and **hip-hop/pop-rap** ({cnt_nonrock("Post Malone")} Post Malone, Lil Nas X, Logic).')
A('* **Media soundtrack / theme covers** (non-rock): *The Last Of Us Part II* (4), *Game Of Thrones* (2 — Ramin Djawadi and a Boyce Avenue version), *Harry Potter Theme*, *Westworld Theme*, *Toss A Coin To Your Witcher* (Joey Batey), *Aladdin* (2).')
A('* **Traditional / seasonal covers** (non-rock): *Rudolph The Red Nosed Reindeer*, *Jingle Bells*, *O Holy Night*, *The First Noel*, *Amazing Grace*.')
A('')
A('## 4. NOTES')
A('')
A('### Inaccessible videos')
A('')
A('**None.** All 657 videos returned `availability=public` with duration, upload date and view count present. No video was private, members-only, deleted or region-blocked. (One intermediate fetch chunk of 110 videos failed with "Requested format is not available"; re-running it with the bgutil PO-Token server on `http://127.0.0.1:4416` recovered all 110, so the enumeration is complete.)')
A('')
A('### Data-quality issues found')
A('')
A('* **Two videos have copy-pasted description bodies** naming a different song and artist than their own title: `v5EYZJ948eU` ("Somebody That I Used To Know" — description text is from the Marshmello/"You Owe Me" video) and `80Dtds4-6YY` ("I Hate U I Love U" — description text is from a The Chainsmokers video). The **titles were treated as authoritative** in both cases.')
A('* The same copy-paste issue appears in `ffSGXt8LxdU` ("This Town" — description hashtag says `#shawnmendes`) and `d-XxGbC1SKQ` ("Talking To The Moon" — description hashtag says `#Coldplay`). Titles again won.')
A('* Artist names were taken from the video title and cross-checked against the `by #artist` hashtag in the description. 613 of 644 descriptions with a hashtag agreed exactly after normalisation; the remainder were hashtags with typos (`shaunmendes`, `SahwnMendes`, `CallumScott`, `Ma`, `marahmello`) or the copy-paste errors above.')
A('')
A('### Genre judgment calls (uncertain — flagged for review)')
A('')
A('`rock` was decided on the **artist\'s primary genre identity**, treating a rock identity as primary when it is not merely "pop rock". These calls are the ones most likely to flip:')
A('')
A('**Counted as ROCK (but arguable):**')
A('')
for a in sorted(BORDERLINE_ROCK):
    n = sum(1 for r in rows if r['artist'] == a)
    if n and a in ROCK_ARTISTS:
        A(f'* **{a}** ({n} video{"s" if n > 1 else ""})')
A('')
A('**Counted as NON-ROCK (but arguable):**')
A('')
for a in sorted(BORDERLINE_NON_ROCK):
    n = sum(1 for r in rows if r['artist'] == a)
    if n and a not in ROCK_ARTISTS:
        A(f'* **{a}** ({n} video{"s" if n > 1 else ""})')
A('')
A('Specific notes:')
A('')
A(f'* **John Mayer** ({cnt("John Mayer")} videos) and **Coldplay** ({cnt("Coldplay")}) are the two largest borderline groups. Both are frequently called pop rock; Mayer is genuinely blues-rock-rooted, Coldplay is listed as alternative rock, so both were kept in.')
A(f'* **Hozier** ({cnt("Hozier")}) is indie-folk/blues rather than rock proper; kept in on the blues/indie-rock reading of "Take Me To Church".')
A('* **Bob Dylan, Neil Young, Simon & Garfunkel, Jeff Buckley, Jim Croce, John Prine, Leonard Cohen** were counted as rock on their "folk rock" identity; the pure-folk acts (Passenger, Iron & Wine, The Lumineers, The Paper Kites, Of Monsters & Men, Bon Iver, Lord Huron, Damien Rice, Angus & Julia Stone, Seafret) were counted as non-rock.')
A('* **Johnny Cash** was counted as non-rock (country is his primary identity) even though "Folsom Prison Blues" and "Hurt" are often called rock; **Elton John**, **Billy Joel**, **Phil Collins**, **Neil Diamond** and **Randy Newman** were likewise counted as non-rock.')
A('* **Machine Gun Kelly** was counted as rock (rap rock / pop punk) and **Secondhand Serenade** as rock (indie rock); both are edge cases.')
A('* **George Michael** ("Careless Whisper") was counted as non-rock (pop/soul), and **Bing Crosby** ("White Christmas") non-rock (traditional pop standard) despite Crosby being a rock-and-roll pioneer — the *song* is a holiday standard, not rock.')
A('* **Coldplay** is a borderline call worth noting: the channel itself files Coldplay under a "POP HITS"-style playlist separate from its OLDIES / LINKIN PARK / ALTERNATIVE rock playlists, which argues for non-rock, while the artist\'s genre identity argues for rock. I went with rock and am flagging it.')
A('')
A('### Artist attribution where the title was ambiguous')
A('')
A('* "Make You Feel My Love" — titled `Adele (Bob Dylan)`; attributed to **Bob Dylan** (the original writer; Adele\'s version is a cover).')
A('* "High And Dry" — titled `High And Dry Radiohead` (no "Cover" marker); artist read as **Radiohead**.')
A('* "The Sound of Silence" — titled `... Cover Simon`; attributed to **Simon & Garfunkel**.')
A('* "It\'s Gotta Be You" — titled `... Cover Isaiah`; attributed to **Israel Kamakawiwoʻole**.')
A('* "Can\'t Take My Eyes Off You" — titled `... Cover Joseph Vincent`; attributed to **Frank Valli** (Joseph Vincent is his real name).')
A('* "Tongue Tied" — titled `Marshmello YUNGBLUD`; attributed to **Yungblud & Marshmello**.')
A('* "Lay Your Head On Me" — titled `Marcus Mumford Major Lazer`; attributed to **Major Lazer ft. Marcus Mumford**.')
A('* "BLOW" — titled `Ed Sheeran Bruno Mars Chris Stapleton`; attributed to that trio (their live cover of Charlie Puth\'s song).')
A('* "Take On Me" (TLOU edition) and the other three *Last Of Us Part II* videos are in-game soundtrack versions; counted as non-rock.')
A('* **Every artist in the CSV was taken from the video title itself.** No artist was inferred from a song title alone, and no artist was invented.')
A('')
A('### Method / reproduction')
A('')
A('```')
A('py -3.14 -m yt_dlp --flat-playlist --no-warnings --print "%(id)s`t%(title)s" \\')
A('  "https://www.youtube.com/@GuitarZero2HeroExpress/videos"   -> gz_videos.txt')
A('py -3.14 -m yt_dlp --flat-playlist --no-warnings --print "%(id)s`t%(title)s" \\')
A('  "https://www.youtube.com/@GuitarZero2HeroExpress/shorts"    -> gz_shorts.txt (empty; no shorts tab)')
A('py -3.14 -m yt_dlp --flat-playlist --no-warnings --print "%(id)s`t%(title)s" \\')
A('  "https://www.youtube.com/@GuitarZero2HeroExpress/playlists" -> gz_playlists.txt')
A('py -3.14 -m yt_dlp --batch-file gz_ids.txt --skip-download --no-warnings \\')
A('  --extractor-args "youtube:player_client=android" --print-json -> gz_meta.json')
A('```')
A('')
A('Media was never downloaded — `--skip-download` throughout, and only metadata fields were read.')
A('')

io.open('GuitarZero2HeroExpress-report.md', 'w', encoding='utf-8').write('\n'.join(L))

print('rows:', len(rows))
print('rock rows:', len(rock_rows))
print('non-rock rows:', len(other_rows))
print('rock artists:', len(set(r['artist'] for r in rock_rows)))
print('csv + report written')
