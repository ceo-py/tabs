"""b17b_zoom.py - private helper for the Nirvana (b17b) batch.

Cuts the strumming-pattern row out of a frame and blows it up 4x so every
character of the pattern can be read unambiguously.

Usage: py -3.14 b17b_zoom.py <video>:<t>:<y0>:<y1> ...
"""
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
TMP = 'frames/b17b_probe/_z.png'


def main():
    items = sys.argv[1:]
    ims = []
    for it in items:
        vid, t, y0, y1 = it.split(':')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', t, '-i',
                        'dl/w4_%s.mp4' % vid, '-frames:v', '1',
                        '-vf', 'crop=520:%d:840:%s' % (int(y1) - int(y0), y0), TMP],
                       check=True, capture_output=True)
        im = Image.open(TMP).convert('RGB')
        im = im.resize((im.size[0] * 4, im.size[1] * 4), Image.LANCZOS)
        ims.append((it, im))
    W = max(i.size[0] for _, i in ims)
    H = sum(i.size[1] + 18 for _, i in ims)
    c = Image.new('RGB', (W, H), (20, 20, 20))
    d = ImageDraw.Draw(c)
    fo = ImageFont.truetype(F_BOLD, 14)
    y = 0
    for n, i in ims:
        d.text((3, y + 2), n, font=fo, fill=(255, 210, 0))
        c.paste(i, (0, y + 18))
        y += i.size[1] + 18
    c.save('frames/b17b_probe/z/zoom4x.png')
    print(c.size)


if __name__ == '__main__':
    main()
