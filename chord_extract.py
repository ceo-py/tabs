# -*- coding: utf-8 -*-
"""
Extract the chord names used by every lesson card.

The cards are rendered by a handful of batch scripts (b2/b3/b4/w/vcards/
compose/rock). Each of them carries the chord list in the `note` string of
the card spec. This script walks those files with `ast` and pairs every
`note` with the card it belongs to.

    py -3.14 chord_extract.py          # -> chords.json  (card path -> chords)
"""
import ast
import json
import os
import re
from collections import OrderedDict

ROOT = os.path.dirname(os.path.abspath(__file__))

SOURCES = [
    'b2_build.py', 'b3_specs.py', 'w_build.py', 'vcards.py', 'compose.py',
    'build_rock_cards.py', 'build_rock_batch2.py', 'gz_manual.py',
    'b4_specs.py', 'b1_specs.py', 'b4_build.py',
]

QUAL = r'(?:maj|min|m|sus|add|dim|aug)'
CHORD_TOKEN = re.compile(
    r'^(?P<root>[A-G][#b]?)'
    r'(?P<qual>' + QUAL + r'\d*)?'
    r'(?P<num>[0-9]{1,2})?'
    r'(?:\((?P<paren>[^)]*)\))?'
    r'(?P<slash>/[A-G][#b]?(?:' + QUAL + r')?\d*)?'
    r'\*?$')


def _record_strings(node):
    """direct string values of a record-like node — never a nested container"""
    vals = []
    if isinstance(node, ast.Dict):
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                vals.append(v.value)
    elif isinstance(node, ast.Call):
        for a in node.args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                vals.append(a.value)
        for kw in node.keywords:
            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                vals.append(kw.value.value)
    elif isinstance(node, (ast.Tuple, ast.List)):
        if all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.elts):
            vals = [e.value for e in node.elts]
    return vals


def harvest(path):
    """-> list of (png_basename, note_text)"""
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return []
    try:
        tree = ast.parse(open(full, encoding='utf-8').read(), filename=path)
    except SyntaxError as e:
        print('  ! %s: %s' % (path, e))
        return []

    pairs = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Dict, ast.Tuple, ast.List, ast.Call)):
            continue
        vals = _record_strings(node)
        if not vals:
            continue
        png = None
        for s in vals:
            if s.endswith('.png') and (png is None or s.startswith('out')):
                png = s
        # the note is the string that yields the most chord tokens
        best, best_n = None, 0
        for s in vals:
            n = len(parse_chords(s))
            if n > best_n:
                best, best_n = s, n
        if best and png:
            pairs.append((os.path.basename(png), best))
    return pairs


def parse_chords(note):
    """-> ordered unique chord names found in a note string"""
    if not note:
        return []
    text = re.split(r'\bStrum(?:ming)?\b', note, flags=re.I)[0]
    out = []
    for tok in text.split():
        t = tok.strip(',.;:')
        if ':' in t:
            t = t.split(':', 1)[1].strip()
        if not t:
            continue
        m = CHORD_TOKEN.match(t)
        if not m or m.end() != len(t):
            continue
        name = m.group(0).rstrip('*')
        if name not in out:
            out.append(name)
    return out


def harvest_json_dir(folder):
    """-> list of (png_basename, note_text) from a folder of JSON card specs"""
    d = os.path.join(ROOT, folder)
    if not os.path.isdir(d):
        return []
    pairs = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.json'):
            continue
        try:
            spec = json.load(open(os.path.join(d, fn), encoding='utf-8'))
        except Exception:
            continue
        out, note = spec.get('out'), spec.get('note')
        if out and note:
            pairs.append((os.path.basename(out), note))
    return pairs


def main():
    found = OrderedDict()
    for s in SOURCES:
        pairs = harvest(s)
        for png, note in pairs:
            found.setdefault(png, note)
        if pairs:
            print('  %-26s %d notes' % (s, len(pairs)))
    for folder in ('b4_specs',):
        pairs = harvest_json_dir(folder)
        for png, note in pairs:
            found.setdefault(png, note)
        if pairs:
            print('  %-26s %d notes' % (folder + '/', len(pairs)))

    # join with the catalogue: card basename -> card path
    catalog = json.load(open(os.path.join(ROOT, 'songs.json'), encoding='utf-8'))
    by_base = {os.path.basename(e['card']): e['card'] for e in catalog}

    out = OrderedDict()
    vocab = OrderedDict()
    for base, note in sorted(found.items()):
        chords = parse_chords(note)
        path = by_base.get(base)
        if not chords or not path:
            continue
        out[path] = chords
        for c in chords:
            vocab[c] = vocab.get(c, 0) + 1

    covered = set(out)
    missing = [e['card'] for e in catalog if e['card'] not in covered]

    # hand-read chords for the cards whose note line is not in any script
    manual_path = os.path.join(ROOT, 'chords_manual.json')
    if os.path.exists(manual_path):
        manual = json.load(open(manual_path, encoding='utf-8'))
        for path, chords in manual.items():
            if path in covered:
                continue
            out[path] = chords
            for c in chords:
                vocab[c] = vocab.get(c, 0) + 1
        print('  manual override        %d cards' % len(manual))

    covered = set(out)
    missing = [e['card'] for e in catalog if e['card'] not in covered]

    with open(os.path.join(ROOT, 'chords.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('\ncards with chords: %d / %d   (missing %d)' % (len(out), len(catalog), len(missing)))
    print('distinct chord tokens: %d' % len(vocab))
    for c, n in sorted(vocab.items(), key=lambda kv: (-kv[1], kv[0])):
        print('   %-10s %d' % (c, n))
    with open(os.path.join(ROOT, 'chords_missing.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(missing))


if __name__ == '__main__':
    main()
