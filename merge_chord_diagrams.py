# -*- coding: utf-8 -*-
"""
Merge the per-batch chord-diagram classification into one file.

The four worker runs classify every card as

    DIAGRAM  the card already shows a fretboard diagram (where to press)
    LETTERS  the card shows the chord names only  -> needs a legend
    NONE     the card shows no chord names at all   -> nothing to add

Input :  chords_diagram_p1.json .. chords_diagram_p4.json
Output:  chords_has_diagram.json   {card path: "DIAGRAM" | "LETTERS" | "NONE"}

    py -3.14 merge_chord_diagrams.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'chords_has_diagram.json')


def sort_key(path):
    """chords_diagram_p1, p2, ... p15 -> 1, 2, ... 15 (a plain string sort would
    put p13 before p2).  A high number (p99) is a correction file and is
    applied last, so it wins over the batch files."""
    name = os.path.basename(path)
    m = re.search(r'p(\d+)', name)
    return int(m.group(1)) if m else 0


def main():
    merged = {}
    import glob
    for p in sorted(glob.glob(os.path.join(ROOT, 'chords_diagram_p*.json')), key=sort_key):
        with open(p, encoding='utf-8') as f:
            data = json.load(f)
        for k, v in data.items():
            merged[k] = str(v).upper()
        print('  %s: %d cards' % (os.path.basename(p), len(data)))

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)

    counts = {}
    for v in merged.values():
        counts[v] = counts.get(v, 0) + 1
    print('\n%d cards -> %s' % (len(merged), counts))


if __name__ == '__main__':
    main()
