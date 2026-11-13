"""b13_compose.py - private card composer for the GuitarZero2HeroExpress batches.

Same look as the proven b10_compose.py (footer label GuitarZero2HeroExpress,
cards written into out_gz/).  The shared card.py / compose_lib.py are NOT
modified or used.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BG = (17, 17, 33)
CARD = (31, 31, 56)
CYAN = (86, 214, 232)
WHITE = (245, 245, 250)
DIM = (165, 165, 192)
LINK = (120, 190, 255)
RULE = (62, 62, 100)

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
F_REG = r'C:\Windows\Fonts\arial.ttf'


def font(path, size):
    return ImageFont.truetype(path, size)


def rounded_card(img, pad=24, radius=18, bg=CARD):
    img = img.convert('RGB')
    w, h = img.size
    card = Image.new('RGB', (w + pad * 2, h + pad * 2), bg)
    mask = Image.new('L', card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.size[0] - 1, card.size[1] - 1],
                                           radius=radius, fill=255)
    card.paste(img, (pad, pad))
    out = Image.new('RGBA', card.size, (0, 0, 0, 0))
    out.paste(card, (0, 0), mask)
    return out


def wrap_note(note, font, max_w):
    words = note.split(' ')
    lines, cur = [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if font.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def build(path_out, title, subtitle, sections, link, min_width=1400,
          title_size=72, sub_size=36, gap=32, pad=56, note=None,
          source='GuitarZero2HeroExpress'):
    head_h = 230
    body = []
    body_w = 0
    body_h = 0
    for label, imgs in sections:
        row = [rounded_card(im) for im in imgs]
        h = max(c.size[1] for c in row)
        w = sum(c.size[0] for c in row) + gap * (len(row) - 1)
        body_w = max(body_w, w)
        body_h += h + (62 if label else 0) + gap
        body.append((label, row, h))

    W = max(min_width, body_w + pad * 2)
    note_lines = []
    if note:
        nf = font(F_REG, 24)
        note_lines = wrap_note(note, nf, W - pad * 2)
    H = head_h + body_h + pad + (56 + 32 * len(note_lines) if note else 0)

    canvas = Image.new('RGBA', (W, H), BG + (255,))
    d = ImageDraw.Draw(canvas)

    avail = W - pad * 2
    while title_size > 30:
        f = font(F_BOLD, title_size)
        if d.textlength(title, font=f) <= avail:
            break
        title_size -= 2
    d.text((pad, 42), title, font=font(F_BOLD, title_size), fill=CYAN)
    d.text((pad + 3, 42 + title_size + 20), subtitle, font=font(F_REG, sub_size), fill=DIM)
    d.line([(pad, head_h - 40), (W - pad, head_h - 40)], fill=RULE, width=2)

    y = head_h
    for label, row, h in body:
        if label:
            d.text((pad, y), label, font=font(F_BOLD, 32), fill=WHITE)
            y += 60
        x = pad
        for c in row:
            canvas.paste(c, (x, y), c)
            x += c.size[0] + gap
        y += h + gap

    ly = H - (112 if note else 62)
    d.polygon([(pad, ly + 4), (pad, ly + 32), (pad + 22, ly + 18)], fill=LINK)
    d.text((pad + 40, ly + 2), link, font=font(F_BOLD, 32), fill=LINK)
    d.text((W - pad - 300, ly + 7), source,
           font=font(F_REG, 24), fill=(105, 105, 138))
    if note:
        ny = ly + 52
        for ln in note_lines:
            d.text((pad, ny), ln, font=font(F_REG, 24), fill=(120, 120, 152))
            ny += 32

    canvas.convert('RGB').save(path_out, quality=96)
    print('saved', path_out, canvas.size)


def make_card(video_id, title, subtitle, sections, note, out_path):
    """sections: list of (label, [crop_png_path, ...])"""
    url = 'https://www.youtube.com/watch?v=' + video_id
    secs = []
    for label, paths in sections:
        imgs = [Image.open(p).convert('RGB') for p in paths]
        secs.append((label, imgs))
    out = out_path if os.path.isabs(out_path) else os.path.normpath(out_path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(out, title, subtitle, secs, url, note=note, min_width=1400)
    return out
