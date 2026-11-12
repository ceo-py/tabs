import os
from PIL import Image
from compose_lib import build

os.makedirs('out_gz', exist_ok=True)

# --- reference card for GuitarZero2HeroExpress (style guide for the agents)
verse = Image.open('frames/gz1/c_tab_verse.png').convert('RGB')
bridge = Image.open('frames/gz1/c_tab_bridge.png').convert('RGB')

build(
    'out_gz/3-Doors-Down-Here-Without-You.png',
    'HERE WITHOUT YOU',
    '3 Doors Down  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
    [
        ('TAB  ·  VERSE', [verse]),
        ('CHORD PATTERN & STRUMMING  ·  BRIDGE', [bridge]),
    ],
    'https://www.youtube.com/watch?v=5Tzz_5vpAn8',
    note='Chords: Bm  A  G  D        Strumming: D---D-DU-UD-D-DU',
    min_width=1400,
    source='GuitarZero2HeroExpress',
)
