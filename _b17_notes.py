# -*- coding: utf-8 -*-
"""
Check the note line of every card: does it fit under the link row?

The composer draws the note starting 60 px above the bottom edge and puts
32 px between the lines, so only two lines fit.  Cards with a longer note
lose their last line.

    py -3.14 _b17_notes.py [spec-dir ...]

Prints every spec whose note needs more than two lines.
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from b13_compose import wrap_note, font, F_REG  # noqa: E402

MAX_LINES = 2


def lines_of(note, width=1400, pad=56):
    if not note:
        return []
    return wrap_note(note, font(F_REG, 24), width - pad * 2)


def main():
    dirs = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, 'b*_spec')))
    bad = []
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for f in sorted(glob.glob(os.path.join(d, '*.json'))):
            spec = json.load(open(f, encoding='utf-8'))
            note = spec.get('note') or ''
            n = len(lines_of(note))
            if n > MAX_LINES:
                bad.append((os.path.relpath(f, ROOT), spec.get('out'), n, note))
    print('%d spec(s) with a note longer than %d lines' % (len(bad), MAX_LINES))
    for f, out, n, note in bad:
        print('  %-34s %-56s %d lines' % (f, out, n))
        print('      %s' % note)
    return bad


if __name__ == '__main__':
    main()
