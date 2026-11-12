# -*- coding: utf-8 -*-
"""
Remove the "▶ https://www.youtube.com/watch?v=..." line from a lesson card.

The link is drawn in LINK blue (120,190,255) while everything else in the
footer band is dim grey, so it can be targeted by colour alone: any pixel
where blue and green clearly dominate red belongs to the video link.

The detection is done with PIL/ImageChops only (no numpy): the two channel
differences are computed at C level, thresholded and multiplied into a
single 1-bit mask, then the mask bbox gives the exact link rectangle.
"""
from PIL import Image, ImageChops, ImageDraw

BG = (17, 17, 33)

SCAN = 150          # how far up from the bottom edge we look for the link
PAD = 6             # extra padding around the erased rectangle
THRESH = 40         # minimum channel difference that counts as "link blue"


def _is_link(px):
    r, g, b = px[:3]
    return b - g > THRESH and g - r > THRESH


def link_mask(im):
    """-> 'L' mask, 255 where the pixel belongs to the video link."""
    r, g, b = im.split()
    blue_over_green = ImageChops.subtract(b, g).point(lambda v: 255 if v > THRESH else 0)
    green_over_red = ImageChops.subtract(g, r).point(lambda v: 255 if v > THRESH else 0)
    return ImageChops.multiply(blue_over_green, green_over_red)


def find_link_box(im, scan=SCAN):
    """-> (x0, y0, x1, y1) of the video-link line in absolute image coords, or None"""
    w, h = im.size
    if h < 40 or w < 40:
        return None
    band = link_mask(im).crop((0, h - scan, w, h))
    bbox = band.getbbox()
    if not bbox:
        return None
    x0, y0, x1, y1 = bbox
    return (x0, h - scan + y0, x1, h - scan + y1)


def strip_link(im, pad=PAD):
    """
    Blank the video-link line in place (the image is modified and returned).

    The image must be RGB; other modes are converted first.
    Returns True if something was actually removed.
    """
    if im.mode != 'RGB':
        im = im.convert('RGB')
    box = find_link_box(im)
    if not box:
        return False
    x0, y0, x1, y1 = box
    ImageDraw.Draw(im).rectangle([x0 - pad, y0 - pad, x1 + pad, y1 + pad], fill=BG)
    return True
