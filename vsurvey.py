"""Vertical-friendly survey montage for Shorts.

Usage:
  py -3.14 vsurvey.py <video_path> <out_dir> [interval_seconds] [cols] [crop]

Unlike survey.py this preserves the source aspect ratio (scales to a fixed WIDTH),
so vertical 1080x1920 frames stay readable.
"""
import os, sys, glob, subprocess


def run(cmd):
    subprocess.run(cmd, check=False, capture_output=True)


def main():
    video = sys.argv[1]
    outdir = sys.argv[2]
    interval = sys.argv[3] if len(sys.argv) > 3 else '5'
    cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    crop = sys.argv[5] if len(sys.argv) > 5 else None

    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, 'f_*.png')):
        os.remove(f)

    vf = 'fps=1/%s' % interval
    if crop:
        w, h, x, y = crop.split(':')
        vf += ',crop=%s:%s:%s:%s' % (w, h, x, y)
    vf += ',scale=360:-1'

    run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf', vf,
         os.path.join(outdir, 'f_%04d.png')])

    files = sorted(glob.glob(os.path.join(outdir, 'f_*.png')))
    if not files:
        print('NO FRAMES')
        return

    from PIL import Image, ImageDraw, ImageFont
    first = Image.open(files[0])
    TW = first.size[0]
    TH = first.size[1]
    LAB = 26
    rows = (len(files) + cols - 1) // cols
    canvas = Image.new('RGB', (cols * TW, rows * (TH + LAB)), (20, 20, 20))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 20)
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB').resize((TW, TH))
        x = (i % cols) * TW
        y = (i // cols) * (TH + LAB)
        canvas.paste(im, (x, y))
        d.rectangle([x, y + TH, x + TW, y + TH + LAB], fill=(0, 0, 0))
        d.text((x + 5, y + TH + 3), 't=%ds f_%04d' % (i * float(interval), i + 1),
               font=fnt, fill=(255, 220, 0))
    out = outdir + '_montage.png'
    canvas.save(out)
    print('saved', out, canvas.size, 'frames', len(files), 'interval', interval)


main()
