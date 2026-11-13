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
    'b5_build.py', 'b6_build.py', 'b7_build.py', 'b8_build.py',
    'b6_rest_build.py', 'b7_rest_build.py',
    'b9_build.py', 'b10_build.py', 'b11_build.py', 'b12_build.py',
]


def discover_sources():
    """every batch build script of the repo, not just the ones listed above"""
    found = set(SOURCES)
    for pat in ('b*_build.py', 'b*_compose.py', '*_cards.py'):
        for fn in os.listdir(ROOT):
            if fn.endswith('.py') and fn.startswith(pat.replace('*', '')):
                found.add(fn)
    return sorted(found)


def discover_spec_dirs():
    """every folder with JSON card specs (b5_spec, b10_spec, b12r_spec, ...)"""
    dirs = []
    for name in os.listdir(ROOT):
        p = os.path.join(ROOT, name)
        if os.path.isdir(p) and 'spec' in name.lower():
            if any(f.endswith('.json') for f in os.listdir(p)):
                dirs.append(name)
    return sorted(dirs)


QUAL = r'(?:maj|min|m|sus|add|dim|aug)'
CHORD_TOKEN = re.compile(
    r'^(?P<root>[A-G][#b]?)'
    r'(?P<qual>' + QUAL + r'\d*)?'
    r'(?P<num>[0-9]{1,2})?'
    r'(?:\((?P<paren>[^)]*)\))?'
    r'(?P<slash>/[A-G][#b]?(?:' + QUAL + r')?\d*)?'
    r'\*?$')

# a chord name that can stand on its own inside brackets, e.g. "D/F#", "A", "Fsus2"
BRACKET_CHORD = re.compile(
    r'^([A-G][#b]?)(?:maj|min|m|sus|add|dim|aug)?\d*'
    r'(?:/[A-G][#b]?(?:maj|min|m|sus|add|dim|aug)?\d*)?$', re.I)


def expand_token(tok):
    """-> the real chord names one note token stands for.

    The note lines of the cards are written by hand, so the same chord can
    show up in several notations:
      "Am7/E"      -> one chord, bass note E
      "A(D/F#)"    -> two chords of the lesson: A and D/F#
      "Bm7(1)"     -> one chord, the bracket is a position hint
      "Fmaj7(b5)"  -> one chord, the bracket is a quality note
    """
    m = CHORD_TOKEN.match(tok)
    if not m or m.end() != len(tok):
        return []
    base = m.group('root') + (m.group('qual') or '') + (m.group('num') or '')
    slash = m.group('slash') or ''
    paren = m.group('paren')
    if paren is None:
        return [base + slash]
    p = paren.strip()
    bm = BRACKET_CHORD.match(p)
    if bm:
        # a second chord of the lesson in brackets
        second = p[0].upper() + p[1:]
        return [base + slash, second]
    # a position hint ("1".."6") or a quality note ("b5") -> plain chord
    return [base + slash]



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
        # a tuple like (panels_list, 'Chords: ...', 'out_gz/X.png') carries the
        # note and the output path next to each other - keep the plain strings
        return [e.value for e in node.elts
                if isinstance(e, ast.Constant) and isinstance(e.value, str)]
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
    text = note
    # the chord list of the lesson is what follows a "Chords:" / "Chord names
    # above the tab:" label - everything before it is a description
    labels = list(re.finditer(r'\bChords?\b[^.:]*:', text, flags=re.I))
    if labels:
        text = text[labels[0].end():]
    # a strumming segment is a rhythm, not a chord list - but only when it is
    # written as a label ("Strumming:"), not in a sentence ("no strumming panel")
    text = re.split(r'\bStrumming\b\s*[:=]', text, flags=re.I)[0]
    # the chord list ends with its sentence
    text = re.split(r'[.;]\s', text)[0]
    # a parenthesis that describes the tuning or the capo is not a chord
    text = re.sub(r'\((?:[^)]*\bstrings?\b[^)]*)\)', ' ', text, flags=re.I)
    text = re.sub(r'\((?:[^)]*\btuning\b[^)]*)\)', ' ', text, flags=re.I)
    out = []
    for tok in text.split():
        t = tok.strip(',.;:')
        if ':' in t:
            left, right = t.split(':', 1)
            left, right = left.strip(), right.strip()
            # "B:maj7" -> Bmaj7,  "A:5" -> a fret number, not a chord
            if right and re.match(r'^(?:maj|min|m|sus|add|dim|aug)', right, re.I) \
                    and re.match(r'^[A-G][#b]?$', left):
                t = left + right
            else:
                t = right
        if not t:
            continue
        for name in expand_token(t):
            # "A(2)" / "E2" -> the bracket is an inversion marker, the chord is A / E
            # (only 1 and 2 are inversion marks; 5/6/7/9/11/13 are chord qualities)
            m2 = re.match(r'^(.+?)(?:\((\d)\)|([12]))$', name)
            if m2 and re.match(r'^[A-G][#b]?[m]?$', m2.group(1)):
                name = m2.group(1)
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
    for s in discover_sources():
        pairs = harvest(s)
        for png, note in pairs:
            found.setdefault(png, note)
        if pairs:
            print('  %-26s %d notes' % (s, len(pairs)))
    for folder in discover_spec_dirs():
        pairs = harvest_json_dir(folder)
        for png, note in pairs:
            found.setdefault(png, note)
        if pairs:
            print('  %-26s %d notes' % (folder + '/', len(pairs)))

    # join with the catalogue: card basename -> card path
    catalog = json.load(open(os.path.join(ROOT, 'songs.json'), encoding='utf-8'))
    by_base = {}
    for e in catalog:
        by_base.setdefault(os.path.basename(e['card']), []).append(e['card'])

    # a card classified as NONE shows no chord names at all -> it has no chord
    # list, even if the note line mentions a chord-looking word
    cls_path = os.path.join(ROOT, 'chords_has_diagram.json')
    classes = json.load(open(cls_path, encoding='utf-8')) if os.path.exists(cls_path) else {}

    out = OrderedDict()
    vocab = OrderedDict()
    for base, note in sorted(found.items()):
        chords = parse_chords(note)
        # the same file name can exist in both channels -> both get the note
        for path in by_base.get(base, []):
            if not chords:
                continue
            if classes.get(path) == 'NONE':
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
