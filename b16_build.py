"""Card builder for my GuitarZero2HeroExpress batches (b12r_spec + b16_spec).

Each spec JSON lists the output path, card title / subtitle, the panels that
are cut straight out of the video frames (timestamp + source-pixel crop
rectangle) and the chord / strumming summary read off those panels.

Usage:
  py -3.14 b16_build.py [spec_name ...]      # default: every spec found
"""
import glob, json, os, subprocess, sys

SPEC_DIRS = ['b12r_spec', 'b16_spec']


def resolve_video(vid, explicit=None):
    if explicit and os.path.exists(explicit):
        return explicit
    for p in ('dl/gz_%s.mp4' % vid, 'dl/w4_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(p) and os.path.getsize(p) > 1000000:
            return p
    return None


def crop(video, t, bbox, out):
    x, y, w, h = bbox
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
           '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), out]
    subprocess.run(cmd, check=True, capture_output=True)


def load_specs():
    specs = []
    for d in SPEC_DIRS:
        for f in sorted(glob.glob(os.path.join(d, '*.json'))):
            specs.append((os.path.splitext(os.path.basename(f))[0], f))
    return specs


def render(vid, path):
    s = json.load(open(path, encoding='utf-8'))
    from b16_compose import make_card
    video = resolve_video(vid, s.get('video'))
    if not video:
        print('NO VIDEO', vid)
        return
    sections = []
    for i, p in enumerate(s['panels']):
        png = p.get('png') or ('frames/b16_build_%s/p_%02d.png' % (vid, i))
        crop(video, p['t'], p['bbox'], png)
        sections.append((p['label'], [png]))
    make_card(vid, s['title'], s['subtitle'], sections,
              note=s['note'], out_path=s['out'])
    print('CARD', s['out'])


def main():
    specs = load_specs()
    want = sys.argv[1:]
    for vid, path in specs:
        if want and vid not in want:
            continue
        render(vid, path)


if __name__ == '__main__':
    main()
