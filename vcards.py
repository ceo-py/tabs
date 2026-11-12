"""Compose the 7 Shorts cards for this worker session.

Imports the shared (unmodified) card.py / compose_lib.py helpers.
"""
import os
from PIL import ImageFont
from card import make_card
from compose_lib import F_REG

os.chdir(os.path.dirname(os.path.abspath(__file__)))

F = ImageFont.truetype(F_REG, 24)


def check_note(note, min_width=1400, pad=56):
    w = F.getlength(note)
    avail = min_width - pad * 2
    flag = 'OVERFLOW' if w > avail else 'ok'
    print('   note width %d / %d  %s' % (w, avail, flag))


CARDS = [
    dict(
        video_id='vqZuzVZgHW8',
        title='LOVE ME TENDER',
        subtitle='Elvis Presley  \u00b7  Love Me Tender Guitar Tutorial  \u00b7  Bernadette Teaches Music',
        out_name='Elvis-Love-Me-Tender.png',
        sections=[
            ('CHORDS', ['frames/c_elvis/C.png', 'frames/c_elvis/D7.png', 'frames/c_elvis/G7.png']),
            ('CHORD PATTERN \u00b7 VERSE', ['frames/c_elvis/verse.png']),
            ('STRUMMING PATTERN', ['frames/c_elvis/strum.png']),
        ],
        note='Chords: C, D7, G7   \u00b7   Strumming: D DU UDU   \u00b7   Verse: C / D7',
    ),
    dict(
        video_id='2_Bc3Pb-BYw',
        title='TAKE ME HOME, COUNTRY ROADS',
        subtitle='John Denver  \u00b7  Take Me Home, Country Roads  \u00b7  Bernadette Teaches Music',
        out_name='John-Denver-Take-Me-Home-Country-Roads.png',
        sections=[
            ('CHORDS', ['frames/c_cr/chords.png']),
            ('CHORD PATTERN', ['frames/c_cr/pat1.png', 'frames/c_cr/pat2.png']),
            ('STRUMMING PATTERN', ['frames/c_cr/strum.png']),
        ],
        note='Chords: G, D, Em, C   \u00b7   Strumming: \u2193 \u2193 \u2191 \u2193 \u2191 \u2193 \u2191   \u00b7   Verse: G G D D / Em Em C C',
    ),
    dict(
        video_id='gQXGVDNC-ic',
        title='I WALK THE LINE',
        subtitle='Johnny Cash  \u00b7  I Walk The Line - Easy  \u00b7  Bernadette Teaches Music',
        out_name='Johnny-Cash-I-Walk-The-Line.png',
        sections=[
            ('CHORDS', ['frames/c_jc/chords.png']),
            ('CHORD PATTERN \u00b7 VERSE', ['frames/c_jc/pat.png']),
            ('CHORD PATTERN \u00b7 CHORUS', ['frames/c_jc/pat_chorus.png']),
            ('STRUMMING PATTERN', ['frames/c_jc/strum.png']),
        ],
        note='Chords: E, A, D   \u00b7   Strumming: E: 6 \u2191\u2193 5 \u2191\u2193 \u00b7 A: 5 \u2191\u2193 6 \u2191\u2193 \u00b7 D: 4 \u2191\u2193 5 \u2191\u2193',
    ),
    dict(
        video_id='dYdX16QX84c',
        title='YELLOW',
        subtitle='Coldplay  \u00b7  Easy Guitar Tutorial - Yellow  \u00b7  Bernadette Teaches Music',
        out_name='Coldplay-Yellow-Short-2023.png',
        sections=[
            ('CHORDS', ['frames/c_y23/G.png', 'frames/c_y23/D.png', 'frames/c_y23/C.png']),
            ('CHORD PATTERN \u00b7 VERSE', ['frames/c_y23/patverse.png']),
            ('CHORD PATTERN \u00b7 CHORUS', ['frames/c_y23/patchorus.png']),
            ('STRUMMING PATTERN', ['frames/c_y23/strum.png']),
        ],
        note='Chords: G, D, C   \u00b7   Strumming: D D D DU   \u00b7   Verse: G G / G G D D   \u00b7   Chorus: D D C C / C C',
    ),
    dict(
        video_id='Jo4tMXg6wmI',
        title='YELLOW',
        subtitle='Coldplay  \u00b7  Yellow - Easy Guitar Tutorial  \u00b7  Bernadette Teaches Music',
        out_name='Coldplay-Yellow-Short-2023b.png',
        sections=[
            ('CHORDS', ['frames/c_y23b/chords.png']),
            ('CHORD PATTERN', ['frames/c_y23b/pat.png']),
            ('STRUMMING PATTERN', ['frames/c_y23b/strum.png']),
        ],
        note='Chords: A, E, Dmaj7   \u00b7   Strumming: DDD DU   \u00b7   Verse: A A / A A E E',
    ),
    dict(
        video_id='4TnTv2t5dQU',
        title='YELLOW',
        subtitle='Coldplay  \u00b7  Yellow - Easy Guitar Tutorial  \u00b7  Bernadette Teaches Music',
        out_name='Coldplay-Yellow-Short-2024.png',
        sections=[
            ('CHORDS', ['frames/c_y24/chords.png']),
            ('CHORD PATTERN', ['frames/c_y24/pat.png']),
            ('STRUMMING PATTERN', ['frames/c_y24/strum.png']),
        ],
        note='Chords: A, E, D   \u00b7   Strumming: \u2193 \u2193 \u2193 \u2193 \u2191   \u00b7   Verse: A A / A A E',
    ),
    dict(
        video_id='olBBttZ9dxk',
        title='HAVE YOU EVER SEEN THE RAIN',
        subtitle='CCR  \u00b7  Have You Ever Seen the Rain  \u00b7  Bernadette Teaches Music',
        out_name='CCR-Have-You-Ever-Seen-The-Rain-Short.png',
        sections=[
            ('CHORDS', ['frames/c_ccr/chords.png']),
            ('CHORD PATTERN \u00b7 VERSE', ['frames/c_ccr/pat.png']),
            ('STRUMMING PATTERN', ['frames/c_ccr/strum.png']),
        ],
        note='Chords: D, A, G, Bm   \u00b7   Strumming: D DU UDU   \u00b7   Verse: D D / D D',
    ),
]

for c in CARDS:
    for label, paths in c['sections']:
        for p in paths:
            assert os.path.exists(p), p
    print(c['out_name'])
    check_note(c['note'])
    out = make_card(c['video_id'], c['title'], c['subtitle'], c['sections'],
                    note=c['note'], out_name=c['out_name'])
    from PIL import Image
    W = Image.open(out).size[0]
    sub_w = ImageFont.truetype(F_REG, 36).getlength(c['subtitle'])
    avail = W - 56 * 2
    print('   subtitle width %d / %d  %s' % (sub_w, avail,
          'OVERFLOW' if sub_w > avail else 'ok'))
    assert sub_w <= avail, 'subtitle overflows ' + out
    assert F.getlength(c['note']) <= avail, 'note overflows ' + out
