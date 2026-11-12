"""Extract frames at exact timestamps, crop a region, tile into one labelled strip.

Usage:
  py -3.14 vstrip.py <video> <out.png> <start> <end> <step> <cols> [crop W:H:X:Y] [tilewidth]
"""
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont


def main():
    video, out = sys.argv[1], sys.argv[2]
    start, end, step = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
    cols = int(sys.argv[6])
    crop = sys.argv[7] if len(sys.argv) > 7 else None
    tilew = int(sys.argv[8]) if len(sys.argv) > 8 else 300

    tmpdir = os.path.join('frames', '_strip')
    os.makedirs(tmpdir, exist_ok=True)
    for f in os.listdir(tmpdir):
        if f.startswith('s_'):
            os.remove(os.path.join(tmpdir, f))
    times = []
    t = start
    while t < end:
        times.append(round(t, 2))
        t += step

    files = []
    for i, tt in enumerate(times):
        p = os.path.join(tmpdir, 's_%03d.png' % i)
        cvf = []
        if crop:
            w, h, x, y = crop.split(':')
            cvf = ['-vf', 'crop={}:{}:{}:{}'.format(w, h, x, y)]
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(tt), '-i', video,
                        '-frames:v', '1'] + cvf + [p], check=False, capture_output=True)
        if os.path.exists(p):
            files.append((tt, p))

    if not files:
        print('NO FRAMES')
        return
    im0 = Image.open(files[0][1])
    sc = tilew / im0.size[0]
    th = int(im0.size[1] * sc)
    LAB = 24
    rows = (len(files) + cols - 1) // cols
    canvas = Image.new('RGB', (cols * tilew, rows * (th + LAB)), (20, 20, 20))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 18)
    for i, (tt, p) in enumerate(files):
        im = Image.open(p).convert('RGB').resize((tilew, th))
        x = (i % cols) * tilew
        y = (i // cols) * (th + LAB)
        canvas.paste(im, (x, y))
        d.rectangle([x, y + th, x + tilew, y + th + LAB], fill=(0, 0, 0))
        d.text((x + 5, y + th + 2), 't=%ss' % tt, font=fnt, fill=(255, 220, 0))
    canvas.save(out)
    print('saved', out, canvas.size, 'frames', len(files))


main()
