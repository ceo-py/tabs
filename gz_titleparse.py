# -*- coding: utf-8 -*-
"""Parse GZ2H Express titles into (song, artist) with high accuracy."""
import re

EMOJI = r'[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]'

# Multi-word qualifier phrases that may sit between "Cover" and the artist.
PHRASE_QUALIFIERS = [
    r'Boyce Avenue Version',
    r'Live In LA Intro',
    r'Including Solo',
    r'Standard & Alternate Tuning',
    r'Standard Tuning',
    r'Studio Tuning',
    r'Alternate Tuning',
]

# Single tokens that are never part of an artist name in this channel's grammar.
TOKEN_QUALIFIERS = {
    'acoustic', 'fingerstyle', 'electric', 'solo', 'chords', 'tabs', 'tab',
    'intro', 'live', 'version', 'standard', 'studio', 'alternate', 'tuning',
    'onscreen', 'including', 'cover', 'guitar', 'by',
}

# Trailing marketing suffixes appended to the artist part.
TRAILING_SUFFIXES = [
    r'\+\s*Onscreen\s*Chords\s*&\s*Tab\b',
    r'\+\s*Onscreen\s*Chords\s*&\s*Solo\b',
    r'\+\s*Onscreen\s*Chords\b',
    r'\+\s*Solo\b',
    r'&\s*Tab\b',
    r'&\s*Solo\b',
]


def _strip_emoji(s):
    return re.sub(EMOJI, ' ', s)


def parse_title(title):
    """Return (song, artist, notes). artist may be None."""
    notes = []
    t = _strip_emoji(title)
    # drop pipe suffix
    if '|' in t:
        t = t.split('|')[0]
    t = re.sub(r'\s+', ' ', t).strip()

    # Locate the "Cover" marker. Prefer "Guitar Cover" so that a song whose
    # own name contains "Cover" (e.g. "Cover Me In Sunshine") still parses.
    m = re.search(r'\bGuitar\s+Cover\b', t, re.I) or re.search(r'\bCover\b', t, re.I)
    if not m:
        m2 = re.search(r'\bGuitar\s+Backing\s+Track\b', t, re.I)
        if not m2:
            return None, None, ['no-cover-marker']
        left = t[:m2.start()].strip()
        right = t[m2.end():].strip()
        notes.append('backing_track')
    else:
        left = t[:m.start()].strip()
        right = t[m.end():].strip()

    # --- left side: song title -------------------------------------------
    song = left
    # "X Acoustic Guitar Cover" -> qualifier before Cover
    for q in ('Acoustic', 'Fingerstyle', 'Electric'):
        song = re.sub(r'\b' + q + r'\b\s*$', '', song, flags=re.I).strip()
    song = re.sub(r'[-\u2013\u2014]\s*$', '', song).strip()
    song = re.sub(r'\s*\(.*?\)\s*$', '', song).strip()

    # --- right side: artist ----------------------------------------------
    r = right.strip()
    r = re.sub(r'^[\-\u2013\u2014]\s*', '', r)
    for suf in TRAILING_SUFFIXES:
        r = re.sub(suf + r'$', '', r, flags=re.I).strip()
    for ph in PHRASE_QUALIFIERS:
        r = re.sub(r'\b' + ph + r'\b', ' ', r, flags=re.I)
    r = re.sub(r'\b' + PHRASE_QUALIFIERS[0] + r'\b', ' ', r, flags=re.I)

    # Remove dash-separated qualifier tail, e.g. " - Queen" is kept as artist,
    # but " - Poison" style artist must be kept too. Only strip a leading
    # qualifier that we recognise.
    r = r.strip()
    toks = [t for t in re.split(r'\s+', r) if t]
    kept = []
    for t in toks:
        core = t.strip('.,:;!?()[]"\'').lower()
        if core in TOKEN_QUALIFIERS:
            continue
        kept.append(t)
    r = ' '.join(kept).strip()

    # "Dan + Shay" must survive -> re-join a '+' that got separated
    r = re.sub(r'\bDan\s*\+\s*Shay\b', 'Dan + Shay', r)

    # Strip a leading dash again (e.g. "- Queen" -> "Queen")
    r = re.sub(r'^[\-\u2013\u2014]\s*', '', r).strip()
    r = re.sub(r'[\-\u2013\u2014]\s*$', '', r).strip()
    r = re.sub(r'\s+', ' ', r)

    if not r:
        return song, None, notes + ['no-artist']

    artist = r
    return song, artist, notes
