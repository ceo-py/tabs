"""Accurate survey: extract full-res frames at exact timestamps (input seek),
then build a labeled montage from those exact frames.

Usage: py -3.14 b5_survey.py <video_path> <out_dir> [interval_seconds]
"""
import os, subprocess, sys, glob, json

def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def main():
    video = sys.argv[1]
    outdir = sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 15.0
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, '*.png')):
        os.remove(f)

    r = sh(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-show_entries', 'stream=width,height', '-of', 'json', video])
    info = json.loads(r.stdout)
    dur = float(info['format']['duration'])
    st = [s for s in info['streams'] if s.get('width')][0]
    W, H = st['width'], st['height']

    times = []
    t = 1.0
    while t < dur - 0.5:
        times.append(round(t, 2))
        t += interval
    times.append(round(dur - 1.0, 2))

    paths = []
    for t in times:
        p = os.path.join(outdir, 't%08.2f.png' % t)
        if not os.path.exists(p):
            sh(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', video,
                '-frames:v', '1', p])
        if os.path.exists(p):
            paths.append((t, p))

    from PIL import Image, ImageDraw, ImageFont
    TW, TH, LAB = 320, 200, 22
    cols = 6
    rows = (len(paths) + cols - 1) // cols
    canvas = Image.new('RGB', (cols * TW, rows * (TH + LAB)), (20, 20, 20))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 18)
    for i, (t, p) in enumerate(paths):
        im = Image.open(p).convert('RGB')
        im = im.resize((TW, TH))
        x = (i % cols) * TW
        y = (i // cols) * (TH + LAB)
        canvas.paste(im, (x, y))
        d.rectangle([x, y + TH, x + TW, y + TH + LAB], fill=(0, 0, 0))
        d.text((x + 5, y + TH + 2), 't=%.0fs' % t, font=fnt, fill=(255, 220, 0))
    out = outdir + '_montage.png'
    canvas.save(out)
    print('saved', out, canvas.size, 'frames', len(paths), 'src', W, H, 'dur', dur)

main()
