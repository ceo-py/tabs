"""Write a spec JSON for one song (private helper).

Usage:
  py -3.14 b16_spec.py <spec_dir> <video_id> <TITLE> <ARTIST> <TAG> <OUT> <NOTE> \
        "LABEL:t:x:y:w:h" "LABEL:t:x:y:w:h" ...
"""
import json, os, sys


def main():
    d = sys.argv[1]
    vid = sys.argv[2]
    title = sys.argv[3]
    artist = sys.argv[4]
    tag = sys.argv[5]
    out = sys.argv[6]
    note = sys.argv[7]
    panels = []
    args = sys.argv[8:]
    video = None
    if args and args[0].startswith('video='):
        video = args[0][len('video='):]
        args = args[1:]
    for a in args:
        label, t, x, y, w, h = a.split(':')
        panels.append({'label': label, 't': float(t), 'bbox': [int(x), int(y), int(w), int(h)]})
    spec = {
        'title': title.upper(),
        'subtitle': '%s  ·  Guitar Cover  ·  %s  ·  GuitarZero2HeroExpress' % (artist, tag),
        'out': out,
        'panels': panels,
        'note': note,
    }
    if video:
        spec['video'] = video
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, vid + '.json')
    json.dump(spec, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('spec', p)


if __name__ == '__main__':
    main()
