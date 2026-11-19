"""b20b_edge.py - private helper (batch b20b): find the horizontal boundary
between the video picture and the white score sheet, plus report the exact
content dimensions of a frame.

Usage: py -3.14 b20b_edge.py <png-frame>
"""
import sys

from PIL import Image


def main():
    im = Image.open(sys.argv[1]).convert('RGB')
    W, H = im.size
    px = im.load()
    print('size', W, H)
    # row-wise mean brightness
    rows = []
    for y in range(H):
        s = 0
        for x in range(0, W, 8):
            r, g, b = px[x, y]
            s += r + g + b
        rows.append(s / (len(range(0, W, 8)) * 3))
    prev = None
    for y in range(H):
        v = rows[y]
        if prev is not None and abs(v - prev) > 18:
            print('jump at y=%d : %.1f -> %.1f' % (y, prev, v))
        prev = v
    # print the mean for selected rows
    for y in range(520, 640, 2):
        print('row', y, 'mean %.1f' % rows[y])


if __name__ == '__main__':
    main()
