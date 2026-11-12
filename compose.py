from PIL import Image
from compose_lib import build

# ---------------------------------------------------------------- Hotel California
hc = 'https://www.youtube.com/watch?v=0AFmPkjl9Gc'

verse = Image.open('frames/sel/hc_c304.png').crop((1330, 40, 1916, 320))   # Am E7 G D
chorus = Image.open('frames/sel/hc_c412.png').crop((1330, 40, 1916, 320))  # F C Dm E7
strum = Image.open('frames/sel/hc_c412.png').crop((1330, 300, 1916, 392))  # Strum: D D U U D D U D U

build(
    'out/Hotel-California.png',
    'HOTEL CALIFORNIA',
    'The Eagles  ·  Easy Guitar Tutorial for Beginners  ·  Bernadette Teaches Music',
    [
        ('CHORDS', [verse, chorus]),
        ('STRUMMING PATTERN', [strum]),
    ],
    hc,
    note='Chords: Am E7 G D (verse)  ·  F C Dm E7 (chorus)',
    min_width=1400,
)

# ------------------------------------------------- Guns N' Roses Sweet Child O' Mine
sc = 'https://www.youtube.com/watch?v=TIpQb2yaKYY'

chords = Image.open('frames/sc_sel/t200_chords.png')      # D C G / A Em
strum = Image.open('frames/sc_sel/t204_strum.png')        # Strumming D DU UDU / DDU DDU
pat_dd = Image.open('frames/sc_sel/t40_pattern.png')      # D D C C / G G D D
pat_em = Image.open('frames/sc_sel/t200_pattern.png')     # Em G A / C-D

build(
    'out/Sweet-Child-O-Mine.png',
    "GUNS N' ROSES — SWEET CHILD O' MINE",
    'EASY Guitar Tutorial  ·  30 Day Guitar Challenge  ·  Bernadette Teaches Music',
    [
        ('CHORDS  ·  STRUMMING PATTERN', [chords, strum]),
        ('CHORD PATTERN  ·  VERSE  /  CHORUS', [pat_dd, pat_em]),
    ],
    sc,
    note='Chords: D C G  ·  A Em        Verse: D D C C / G G D D        Chorus: Em G A / C-D',
    min_width=1400,
)
