# -*- coding: utf-8 -*-
"""
Collect the `diagram` value each build agent recorded in its spec and write
chords_diagram_p20.json (the same shape as chords_diagram_p19.json).

    py -3.14 _b18_classify.py

Keys are card paths (`out_gz/<slug>.png`), values are LETTERS / DIAGRAM / NONE.
Also prints a summary and any spec that is missing the field.
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SPEC_DIRS = ['b18a_spec', 'b18b_spec', 'b18c_spec', 'b18d_spec']
OUT = os.path.join(ROOT, 'chords_diagram_p20.json')


def main():
    result = {}
    missing = []
    for d in SPEC_DIRS:
        for f in sorted(glob.glob(os.path.join(ROOT, d, '*.json'))):
            spec = json.load(open(f, encoding='utf-8'))
            out = spec.get('out', '').replace('\\', '/')
            val = spec.get('diagram')
            if not out:
                missing.append((f, 'no out'))
                continue
            if val not in ('LETTERS', 'DIAGRAM', 'NONE'):
                missing.append((os.path.basename(f), 'diagram=%r' % (val,)))
                continue
            result[out] = val

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)

    counts = {}
    for v in result.values():
        counts[v] = counts.get(v, 0) + 1
    print('chords_diagram_p20.json: %d cards  %s' % (len(result), counts))
    for out in sorted(result):
        print('  %-58s %s' % (out, result[out]))
    if missing:
        print('\nSPECS NEEDING ATTENTION:')
        for m in missing:
            print('  ', m)


if __name__ == '__main__':
    main()
