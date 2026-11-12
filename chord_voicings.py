# -*- coding: utf-8 -*-
"""
Find a playable guitar voicing for a chord name that is not in the shape
dictionary yet.

The search walks every combination of the six strings (muted, open, or
pressed at fret 1..5) and keeps the voicings that

  * contain the root of the chord,
  * use only tones of that chord (power chords: root + fifth),
  * put the requested bass note on the lowest sounding string,
  * are as close to a real hand position as possible:
    few muted strings, few different frets, small fret span, low position.

    py -3.14 chord_voicings.py Fsus2 Gadd11 Bbm/Eb D#dim7
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# open strings, from the 6th (low E) to the 1st (high e)
OPEN = [4, 9, 2, 7, 11, 4]          # E A D G B e
NAMES = ['E', 'A', 'D', 'G', 'B', 'e']

PC = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'Fb': 4,
      'E#': 5, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9,
      'A#': 10, 'Bb': 10, 'B': 11, 'Cb': 11}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def pitch(name):
    m = re.match(r'^([A-G][#b]?)(?:\((\d)\)|(\d))?$', name.strip())
    if not m:
        return None
    return PC[m.group(1)]


def tones(name):
    """-> (set of pitch classes, bass pitch class or None)"""
    n = name.strip()
    bass = None
    m = re.match(r'^(.+?)\(([^)]+)\)$', n)
    if m and m.group(2).upper() not in ('B5',):
        n, bass = m.group(1), pitch(m.group(2))
    if '/' in n:
        n, b = n.split('/', 1)
        bass = pitch(b)
    m = re.match(r'^([A-G][#b]?)(.*)$', n)
    root = PC[m.group(1)]
    rest = m.group(2).lower()

    if rest.startswith('5'):                      # power chord
        return {root, (root + 7) % 12}, bass
    if rest.startswith('dim'):                   # dim / dim7
        s = {root, (root + 3) % 12, (root + 6) % 12}
        if '7' in rest:
            s.add((root + 9) % 12)
        return s, bass
    if rest.startswith('aug'):
        return {root, (root + 4) % 12, (root + 8) % 12}, bass
    if rest.startswith('sus'):
        third = (root + 2) % 12 if rest.startswith('sus2') else (root + 5) % 12
        s = {root, third, (root + 7) % 12}
        if '7' in rest:
            s.add((root + 10) % 12)
        return s, bass
    if rest.startswith('maj') or rest.startswith(''):
        s = {root, (root + 4) % 12, (root + 7) % 12}
        if 'maj7' in rest or 'maj9' in rest:
            s.add((root + 11) % 12)
        if rest.startswith('m') or 'min' in rest:
            s = {root, (root + 3) % 12, (root + 7) % 12}
        if '7' in rest:
            s.add((root + 10) % 12)
        if '9' in rest:
            s.add((root + 2) % 12)
        if '11' in rest:
            s.add((root + 5) % 12)
        if '13' in rest:
            s.add((root + 9) % 12)
        if 'add2' in rest or 'add9' in rest:
            s.add((root + 2) % 12)
        if 'add11' in rest:
            s.add((root + 5) % 12)
        return s, bass
    s = {root, (root + 4) % 12, (root + 7) % 12}
    if '7' in rest:
        s.add((root + 10) % 12)
    if '9' in rest:
        s.add((root + 2) % 12)
    return s, bass


def voicings(chord, max_fret=5):
    """-> list of (score, frets) candidates, best first"""
    want, bass = tones(chord)
    root = PC[re.match(r'^([A-G][#b]?)', chord).group(1)]
    results = []
    # every string: -1 muted, 0 open, 1..max_fret pressed
    for state in range((max_fret + 2) ** 6):
        frets = []
        s = state
        for _ in range(6):
            frets.append(s % (max_fret + 2) - 1)
            s //= (max_fret + 2)
        frets.reverse()
        sounding = [i for i in range(6) if frets[i] >= 0]
        if len(sounding) < 4:
            continue
        pcs = [(OPEN[i] + frets[i]) % 12 for i in sounding]
        if not set(pcs) <= want:
            continue
        if root not in pcs:
            continue
        if bass is not None and pcs[0] != bass:
            continue
        pressed = [f for f in frets if f > 0]
        muted = sum(1 for f in frets if f < 0)
        span = (max(pressed) - min(pressed)) if pressed else 0
        distinct = len(set(pressed))
        score = (muted, distinct, span, max(pressed) if pressed else 0)
        results.append((score, frets))
    results.sort(key=lambda x: x[0])
    return results


def describe(frets):
    out = []
    for i, f in enumerate(frets):
        if f < 0:
            out.append('%s:x' % NAMES[i])
        else:
            out.append('%s%d' % (NAMES[i], f))
    return ' '.join(out)


def main():
    names = sys.argv[1:]
    if not names:
        print('usage: py -3.14 chord_voicings.py <chord> [<chord> ...]')
        return
    for name in names:
        want, bass = tones(name)
        res = voicings(name)
        print('\n%s   tones: %s%s' % (
            name,
            ' '.join(sorted(NOTE_NAMES[t] for t in want)),
            '   bass: %s' % NOTE_NAMES[bass] if bass is not None else ''))
        if not res:
            print('   no voicing found')
            continue
        for score, frets in res[:3]:
            pcs = [(OPEN[i] + frets[i]) % 12 for i in range(6) if frets[i] >= 0]
            print('   %-34s  %s   %s' % (
                describe(frets), str(frets),
                ' '.join(NOTE_NAMES[p] for p in pcs)))


if __name__ == '__main__':
    main()
