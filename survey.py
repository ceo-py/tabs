"""Extract survey frames from a video and build a labeled montage.

Usage:
  py -3.14 survey.py <video_path> <out_dir> [interval_seconds] [cols] [crop]

crop is optional: W:H:X:Y  (applied before scaling, in source pixels)
Frames are scaled to 320px wide for the montage.
"""
import os, sys, glob, subprocess

def run(cmd):
    subprocess.run(cmd, check=False, capture_output=True)

def main():
    video = sys.argv[1]
    outdir = sys.argv[2]
    interval = sys.argv[3] if len(sys.argv) > 3 else '20'
    cols = sys.argv[4] if len(sys.argv) > 4 else '6'
    crop = sys.argv[5] if len(sys.argv) > 5 else None

    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, '*.png')):
        os.remove(f)

    vf = 'fps=1/%s' % interval
    if crop:
        w, h, x, y = crop.split(':')
        vf += ',crop=%s:%s:%s:%s' % (w, h, x, y)
    vf += ',scale=320:-1'

    run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf', vf,
         os.path.join(outdir, 'f_%04d.png')])

    files = sorted(glob.glob(os.path.join(outdir, 'f_*.png')))
    if not files:
        print('NO FRAMES')
        return

    from PIL import Image, ImageDraw, ImageFont
    TW, TH, LAB = 320, 200, 22
    rows = (len(files) + int(cols) - 1) // int(cols)
    canvas = Image.new('RGB', (int(cols) * TW, rows * (TH + LAB)), (20, 20, 20))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 18)
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB').resize((TW, TH))
        x = (i % int(cols)) * TW
        y = (i // int(cols)) * (TH + LAB)
        canvas.paste(im, (x, y))
        d.rectangle([x, y + TH, x + TW, y + TH + LAB], fill=(0, 0, 0))
        d.text((x + 5, y + TH + 2), 't=%ds  (f_%04d)' % (i * float(interval), i + 1),
               font=fnt, fill=(255, 220, 0))
    out = outdir + '_montage.png'
    canvas.save(out)
    print('saved', out, canvas.size, 'frames', len(files), 'interval', interval)

main()
