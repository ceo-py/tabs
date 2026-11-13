"""b13_build.py - build the GuitarZero2HeroExpress cards from the per-song specs.

The specs live in b13_spec/<video_id>.json:

  {
    "title":    "SONG TITLE IN CAPS",
    "subtitle": "ARTIST  ·  Guitar Cover  ·  TAG  ·  GuitarZero2HeroExpress",
    "out":      "out_gz/<File>.png",
    "panels":   [ {"label": "TAB  ·  VERSE", "t": 64,
                   "bbox": [x, y, w, h], "png": "frames/b13_<id>/p0.png"}, ... ],
    "note":     "Chords: ...   Strumming: ..."
  }

Every panel is cropped straight out of the video frame at timestamp t.

Usage:
  py -3.14 b13_build.py [video_id ...]     # default: every spec in b13_spec/
"""
import glob
import json
import os
import subprocess
import sys

SPEC_DIR = 'b13_spec'


def pick_video(vid):
    for c in ('dl/w4_%s.mp4' % vid, 'dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(c) and os.path.getsize(c) > 1000000:
            return c
    return None


def crop(video, t, bbox, out):
    x, y, w, h = bbox
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
           '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), out]
    subprocess.run(cmd, check=True, capture_output=True)


def render(vid, s):
    from b13_compose import make_card
    video = pick_video(vid)
    if not video:
        print('NO VIDEO for', vid)
        return
    sections = []
    for p in s['panels']:
        out = p['png']
        crop(video, p['t'], p['bbox'], out)
        sections.append((p['label'], [out]))
    make_card(vid, s['title'], s['subtitle'], sections, note=s.get('note'),
              out_path=s['out'])
    print('CARD', s['out'])


def main():
    ids = []
    for f in sorted(glob.glob(os.path.join(SPEC_DIR, '*.json'))):
        ids.append(os.path.splitext(os.path.basename(f))[0])
    for vid in (sys.argv[1:] or ids):
        spec = json.load(open(os.path.join(SPEC_DIR, vid + '.json'), encoding='utf-8'))
        render(vid, spec)


if __name__ == '__main__':
    main()
