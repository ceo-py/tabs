# -*- coding: utf-8 -*-
"""Shared matcher: which research videos we ALREADY have a lesson card for.

Source of truth: songs.json (389 cards). A research video counts as "have it"
when the (artist, song) pair matches a card we already built.
"""
import json
import os
import re

R = os.path.dirname(os.path.abspath(__file__))

_BAD = re.compile(r"[^a-z0-9 ]+")
_SP = re.compile(r"\s+")


def norm(s):
    s = (s or "").lower()
    s = _BAD.sub(" ", s)
    return _SP.sub(" ", s).strip()


def load_cards():
    """-> list of (artist_norm, song_norm, artist, song)"""
    data = json.load(open(os.path.join(R, "songs.json"), encoding="utf-8"))
    out = []
    for s in data:
        a = norm(s.get("artist"))
        t = norm(s.get("title"))
        if a or t:
            out.append((a, t, s.get("artist", ""), s.get("title", "")))
    return out


class Have:
    def __init__(self):
        self.cards = load_cards()
        # artist -> list of song norms
        self.by_artist = {}
        for a, t, _ra, _rt in self.cards:
            self.by_artist.setdefault(a, []).append(t)
        self.all_songs = {t for _a, t, _ra, _rt in self.cards}

    def match(self, artist, song):
        """Return the card title we already have, or None."""
        a = norm(artist)
        s = norm(song)
        if not s:
            return None
        # exact artist
        for ra, rt, orig_a, orig_t in self.cards:
            if ra != a:
                continue
            if rt == s or (len(rt) >= 4 and (rt in s or s in rt)):
                return orig_t
        # unknown artist: song alone (risky, only for long distinctive titles)
        if len(s) >= 8 and s in self.all_songs:
            for ra, rt, orig_a, orig_t in self.cards:
                if rt == s:
                    return orig_t
        return None


if __name__ == "__main__":
    h = Have()
    print("cards: %d   artists: %d" % (len(h.cards), len(h.by_artist)))
    for a, s in [("Oasis", "Don't Look Back In Anger"), ("Oasis", "Wonderwall"),
                 ("Nirvana", "Smells Like Teen Spirit"), ("Metallica", "Enter Sandman"),
                 ("Linkin Park", "In The End"), ("Oasis", "Slide Away")]:
        print("%-14s %-28s -> %s" % (a, s, h.match(a, s) or "— нямаме —"))
