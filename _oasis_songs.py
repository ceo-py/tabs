# -*- coding: utf-8 -*-
"""Oasis songs (canonical) + fuzzy matcher against video titles."""
import re

OASIS_SONGS = [
    "Wonderwall", "Don't Look Back In Anger", "Live Forever", "Supersonic",
    "Slide Away", "Some Might Say", "Whatever", "Champagne Supernova",
    "Rock 'n' Roll Star", "Half The World Away", "Cigarettes & Alcohol",
    "Morning Glory", "She's Electric", "Stand By Me", "D'You Know What I Mean?",
    "I Hope, I Think, I Know", "Songbird", "Lyla", "Stay Young", "Roll With It",
    "Columbia", "Masterplan", "Shakermaker", "Stop Crying Your Heart Out",
    "Go Let It Out", "Importance Of Being Idle", "My Big Mouth", "Mucky Fingers",
    "Fade Away", "Let It All Hang Out", "The Boy With The Blues",
    "Don't Believe The Truth", "Ain't Got Nothin'", "Born On The Reign Of Bang",
    "The Turning", "Trying To Get To Heaven", "All Around The World",
    "Acrid", "Killing Time", "Love Like A Bomb", "The Hindu Times", "Say What You Want",
    "Who Feels Love?", "Acquiesce", "Magnificent", "Digsy's Dinner", "Party On",
    "The Boy With The Blues", "Up On The Downtown", "Where We Born And Raised",
    "Natures Way", "(It's Good) To Be In A Band", "Long Distance Winner",
    "Pretty In Black", "Do What You Wanna", "Instant Karma",
]

_NORM = re.compile(r"[^a-z0-9]+")


# Oasis covered these songs - the lesson card we have is credited to the
# original performer, not to Oasis. Without this the coverage and gap reports
# would count a song we already have as missing and look for a second source.
CROSS_ARTIST_CARDS = {
    "Instant Karma": "John Lennon",
}


def _n(s):
    return _NORM.sub(" ", (s or "").lower()).strip()


_LOOKUP = {}
for s in OASIS_SONGS:
    key = _n(s)
    _LOOKUP.setdefault(key, s)
    # also index without leading article
    if key.startswith("the "):
        _LOOKUP.setdefault(key[4:], s)


def match_song(title):
    """Return the canonical Oasis song name found in the title, or None."""
    t = _n(title)
    if "oasis" not in t:
        return None
    best = None
    for key, canon in _LOOKUP.items():
        if key and key in t:
            if best is None or len(key) > len(best[0]):
                best = (key, canon)
    return best[1] if best else None


if __name__ == "__main__":
    tests = [
        "Oasis - Wonderwall (guitar cover with tabs & chords)",
        "Don't Look Back In Anger - Oasis | Tabs | Guitar Lesson | Cover | Tutorial",
        "Half The World Away - Oasis | Tabs + Chords | Guitar Lesson",
        "Oasis - D'you Know What I Mean? (guitar cover with tabs & chords)",
        "【OASIS】[ Wonderwall ] cover by Dotti Brothers | LESSON | GUITAR TAB",
        "Oasis 'Supersonic' Lead Guitar Tutorial: Play Along with Original Video",
        "Oasis Top 10 Riffs with Tabs",
        "Oasis - Slide Away (guitar cover with tabs & chords)",
    ]
    for t in tests:
        print("%-62s -> %s" % (t[:62], match_song(t)))
