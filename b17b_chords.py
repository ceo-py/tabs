"""b17b_chords.py - private helper for the Nirvana (b17b) batch.

Crops the chord grid that sits above the "Strumming Pattern" pill for a list
of (video, time) pairs and stacks them for reading.
"""
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
TMP = 'frames/b17b_probe/_c.png'


def main():
    x0, y0, x1, y1 = 628, 615, 1770, 790
    items = sys.argv[1:]
    ims = []
    for it in items:
        vid, t = it.split(':')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', t, '-i',
                        'dl/w4_%s.mp4' % vid, '-frames:v', '1',
                        '-vf', 'crop=%d:%d:%d:%d' % (x1 - x0, y1 - y0, x0, y0), TMP],
                       check=True, capture_output=True)
        im = Image.open(TMP).convert('RGB')
        ims.append((it, im))
    W = max(i.size[0] for _, i in ims)
    H = sum(i.size[1] + 20 for _, i in ims)
    c = Image.new('RGB', (W, H), (20, 20, 20))
    d = ImageDraw.Draw(c)
    fo = ImageFont.truetype(F_BOLD, 15)
    y = 0
    for n, i in ims:
        d.text((3, y + 2), n, font=fo, fill=(255, 210, 0))
        c.paste(i, (0, y + 20))
        y += i.size[1] + 20
    c.save('frames/b17b_probe/z/chords.png')
    print(c.size)


if __name__ == '__main__':
    main()
