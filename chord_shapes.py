# -*- coding: utf-8 -*-
"""
Guitar chord shapes for the TABS 90 chord legend.

Standard tuning, strings listed from the 6th (low E) to the 1st (high e):
    E  A  D  G  B  e
A shape is a list of 6 fret numbers:
    0  -> open string        (drawn as a small circle above the nut)
    -1 -> muted string       (drawn as a small cross above the nut)
    n  -> press at fret n    (drawn as a dot on the string)

    py -3.14 chord_shapes.py    -> chord_shapes.json
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

# name : frets (6th string -> 1st string)
SHAPES = {
    # ---- open / barre majors -------------------------------------------
    'A':    [-1, 0, 2, 2, 2, 0],
    'A7':   [-1, 0, 2, 0, 2, 0],
    'Am':   [-1, 0, 2, 2, 1, 0],
    'Am7':  [-1, 0, 2, 0, 1, 0],
    'Asus2':[-1, 0, 2, 2, 0, 0],
    'Asus4':[-1, 0, 2, 2, 3, 0],
    'B':    [-1, 2, 4, 4, 4, 2],
    'B7':   [-1, 2, 1, 2, 0, 2],
    'Bm':   [-1, 2, 4, 4, 3, 2],
    'Bm7':  [-1, 2, 4, 2, 3, 2],
    'Bmadd11': [-1, 2, 4, 4, 3, 2],
    'Bsus4':[-1, 2, 4, 4, 4, 0],
    'C':    [-1, 3, 2, 0, 1, 0],
    'C7':   [-1, 3, 2, 3, 1, 0],
    'C9':   [-1, 3, 2, 0, 1, 3],
    'Cadd9':[-1, 3, 2, 0, 3, 0],
    'Cm':   [-1, 3, 5, 5, 4, 3],
    'Cmaj7':[-1, 3, 2, 0, 0, 0],
    'Csus2':[-1, 3, 0, 0, 1, 3],
    'D':    [-1, -1, 0, 2, 3, 2],
    'D6':   [-1, -1, 0, 2, 0, 2],
    'D7':   [-1, -1, 0, 2, 1, 2],
    'Dm':   [-1, -1, 0, 2, 3, 1],
    'Dm7':  [-1, -1, 0, 2, 1, 1],
    'Dmaj7':[-1, -1, 0, 2, 2, 2],
    'Dsus2':[-1, -1, 0, 2, 3, 0],
    'Dsus4':[-1, -1, 0, 2, 3, 3],
    'E':    [0, 2, 2, 1, 0, 0],
    'E7':   [0, 2, 0, 1, 0, 0],
    'Em':   [0, 2, 2, 0, 0, 0],
    'Em7':  [0, 2, 0, 0, 0, 0],
    'F':    [1, 3, 3, 2, 1, 1],
    'Fmaj7':[1, 3, 2, 1, 0, 0],
    'Fm':   [1, 3, 3, 1, 1, 1],
    'G':    [3, 2, 0, 0, 0, 3],
    'G6':   [3, 2, 0, 0, 0, 2],
    'G7':   [3, 2, 0, 0, 0, 1],
    'Gm':   [3, 5, 5, 3, 3, 3],
    'Gm6':  [3, 5, 3, 3, 3, 3],
    'Gmaj7':[3, 2, 0, 0, 0, 2],
    'Gs':   [3, 5, 5, 4, 3, 3],
    'Gsus2':[-1, -1, 0, 0, 3, 3],

    # ---- flat / sharp --------------------------------------------------
    'Bb':   [-1, 1, 3, 3, 3, 1],
    'Bb7':  [-1, 1, 3, 2, 3, 1],
    'Bbsus2':[-1, 1, 3, 1, 1, 1],
    'C#':   [-1, 4, 6, 6, 5, 4],
    'C#7':  [-1, 4, 6, 4, 5, 4],
    'C#m':  [-1, 4, 6, 6, 5, 4],
    'D#':   [-1, 4, 6, 6, 5, 4],
    'F#':   [2, 4, 4, 3, 2, 2],
    'F#7':  [2, 4, 2, 3, 2, 0],
    'F#m':  [2, 4, 4, 3, 2, 2],
    'F#m7': [2, 4, 2, 3, 2, 2],
    'F#m11':[-1, 4, 4, 3, 2, 0],
    'G#':   [4, 6, 6, 5, 4, 4],
    'G#7':  [4, 6, 4, 5, 4, 4],

    # ---- power chords --------------------------------------------------
    'E5':   [0, 2, 2, -1, -1, -1],
    'D5':   [-1, 5, 7, -1, -1, -1],
    'A5':   [-1, 0, 2, -1, -1, -1],
    'B5':   [-1, 2, 4, -1, -1, -1],
    'G5':   [3, 5, 7, -1, -1, -1],
    'G5(5)': [8, 10, 12, -1, -1, -1],

    # ---- rarer voicings that show up in the lessons ---------------------
    'Am/E':  [0, 0, 2, 2, 1, 0],
    'C#m7':  [-1, 4, 6, 4, 5, 4],
    'Dadd11':[-1, -1, 0, 2, 3, 3],
    'E7/B':  [-1, 2, 0, 1, 0, 0],
    'Em/B':  [-1, 2, 2, 0, 0, 0],
    'Em/G':  [3, -1, 2, 0, 0, 0],
    'Fmaj7(b5)': [-1, -1, 3, 2, 1, 0],
    'G(A)':  [-1, 0, 0, 0, 3, 3],
    'G/F#':  [2, -1, 0, 0, 0, 3],
}

# slash chords: base shape + the note played in the bass
SLASH = {
    'A/B':   ('A', 'B'),
    'A/G':   ('A', 'G'),
    'A/D':   ('A', 'D'),
    'A/C#':  ('A', 'C#'),
    'A/E':   ('A', 'E'),
    'Am/C':  ('Am', 'C'),
    'C/G':   ('C', 'G'),
    'D/F#':  ('D', 'F#'),
    'F/A':   ('F', 'A'),
    'G/A':   ('G', 'A'),
    'G/B':   ('G', 'B'),
    'G/F':   ('G', 'F'),
    'G(F)':  ('G', 'F'),
    'A(D/F#)': ('A', 'D/F#'),
    'Em(D/F#)': ('Em', 'D/F#'),
    'C(D/F#)':  ('C', 'D/F#'),
}

# the bass note of a slash chord is sometimes written inside brackets
SLASH_RE = re.compile(r'^(?P<base>.+?)\((?P<bass>[^)]+)\)$')


def parse(name):
    """-> (base_name, bass_note or None, frets or None)"""
    n = name.strip()
    m = SLASH_RE.match(n)
    if m:
        base, bass = m.group('base'), m.group('bass')
        return base, bass, SHAPES.get(base)
    if n in SLASH:
        base, bass = SLASH[n]
        return base, bass, SHAPES.get(base)
    if '/' in n:
        base, bass = n.split('/', 1)
        return base, bass, SHAPES.get(base)
    return n, None, SHAPES.get(n)


def main():
    out = {}
    for name, frets in SHAPES.items():
        out[name] = {'frets': frets, 'base': name, 'bass': None}
    # a slash chord keeps the shape of its base chord and names the bass note
    for name, (base, bass) in SLASH.items():
        out[name] = {
            'frets': SHAPES.get(base),
            'base': base,
            'bass': bass,
        }
    with open(os.path.join(ROOT, 'chord_shapes.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('%d shapes -> chord_shapes.json' % len(out))


if __name__ == '__main__':
    main()
