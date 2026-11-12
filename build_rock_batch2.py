"""Build the seven rock/tutorial cards for the BernadetteTeachesMusic batch.

Uses the shared card.make_card helper (read-only); this file is my own.
Every crop comes from an actual frame of the actual video.
"""
import os, sys
sys.path.insert(0, r'D:\MiniMax Code Repos\Guitar Lessons')
os.chdir(r'D:\MiniMax Code Repos\Guitar Lessons')
from card_rock import make_card

F = 'frames/'
Y = F + 'rock_MfIguC1c2hQ/'      # Coldplay - Yellow
B = F + 'rock_M8rVBAJhcLI/'      # CCR - Bad Moon Rising (EASY CHORDS)
W = F + 'rock_9pH9cccg6t8/'      # The White Stripes
R = F + 'rock_bYOD1FQ9sgc/'      # CCR - Have You Ever Seen the Rain
M = F + 'rock_dK27UjMr1UI/'      # CCR - Bad Moon Rising (Challenge 2)
P = F + 'rock_e-XedYIyKC0/'      # CCR - Proud Mary (Challenge 3)
C = F + 'rock_tFfQAG50H2g/'      # CCR - Down on the Corner

# ------------------------------------------------------------------ 1 Coldplay
make_card(
    'MfIguC1c2hQ', 'YELLOW',
    'Coldplay  ·  EASY Guitar Tutorial  ·  Bernadette Teaches Music',
    [('CHORDS', [Y + 'c_chords_AED.png', Y + 'c_chords_AAsus4.png',
                 Y + 'c_chords_DFsm7E.png', Y + 'c_chords_AEmD.png']),
     ('CHORD PATTERN', [Y + 'c_pattern_verse.png']),
     ('STRUMMING PATTERN', [Y + 'c_strum_main.png', Y + 'c_strum_trans.png'])],
    note='Chords: A E D | Asus4 | D F#m7 E | A Em D   '
         'Verse: A A A A / E E E E / D D D D / A A A A   Strum: down-down-down-down-up',
    out_name='Coldplay-Yellow.png',
)

# ------------------------------------- 2 CCR Bad Moon Rising (older, letters only)
make_card(
    'M8rVBAJhcLI', 'BAD MOON RISING',
    'Creedence Clearwater Revival  ·  EASY CHORDS  ·  Bernadette Teaches Music',
    [('CHORD PATTERN  ·  VERSE', [B + 'c_bar_verse1.png']),
     ('CHORD PATTERN  ·  CHORUS', [B + 'c_bar_chorus.png'])],
    note='Video shows chord LETTERS over a lyrics bar only - no fretboard diagrams and no '
         'strumming pattern graphic.   Verse: D A G D D   Chorus: G G D D A G D',
    out_name='CCR-Bad-Moon-Rising-Easy-Chords.png',
)

# ------------------------------------------------------------- 3 The White Stripes
make_card(
    '9pH9cccg6t8', "WE'RE GOING TO BE FRIENDS",
    'The White Stripes  ·  EASY Guitar Tutorial  ·  Bernadette Teaches Music',
    [('CHORDS', [W + 'c_chords_GCDA.png']),
     ('CHORD PATTERN', [W + 'c_pattern_verse.png', W + 'c_pattern_chorus.png']),
     ('FINGERPICKING', [W + 'c_fingerpicking.png']),
     ('STRUMMING PATTERN', [W + 'c_strum.png'])],
    note='Chords: G C D A   Fingerpicking: G 6-3-2-1, C 5-3-2-1, D 4-3-2-1   '
         'Verse: G G G G / C C G G   Strum: down-down-up',
    out_name='White-Stripes-Were-Going-To-Be-Friends.png',
)

# ------------------------------------- 4 CCR Have You Ever Seen the Rain
make_card(
    'bYOD1FQ9sgc', 'HAVE YOU EVER SEEN THE RAIN',
    'Creedence Clearwater Revival  ·  EASY Guitar Tutorial  ·  Bernadette Teaches Music',
    [('CHORDS', [R + 'c_chord_Am.png', R + 'c_chord_C.png',
                 R + 'c_chord_G.png', R + 'c_chord_F.png']),
     ('STRUMMING PATTERN', [R + 'c_strum_main.png', R + 'c_strum_intro.png']),
     ('INTRO CHORD PATTERN', [R + 'c_pattern_intro.png']),
     ('VERSE CHORD PATTERN', [R + 'c_pattern_verse1.png']),
     ('VERSE CHORD PATTERN (CONT.)', [R + 'c_pattern_verse3.png']),
     ('CHORUS CHORD PATTERN', [R + 'c_pattern_chorus.png'])],
    note='Chords: Am C G F   Strum: down-down-up-up-down-up   '
         'Verse: G G C C / D D G G   Chorus: F G C Am   Intro: Em C G D G G',
    out_name='CCR-Have-You-Ever-Seen-The-Rain.png',
)

# ------------------------------------- 5 CCR Bad Moon Rising (Challenge Song 2)
make_card(
    'dK27UjMr1UI', 'BAD MOON RISING',
    'Creedence Clearwater Revival  ·  CCR Challenge Song 2  ·  Bernadette Teaches Music',
    [('CHORDS', [M + 'c_chord_D.png', M + 'c_chord_A.png', M + 'c_chord_G.png']),
     ('STRUMMING PATTERN', [M + 'c_strum.png']),
     ('VERSE CHORD PATTERN', [M + 'c_pattern_verse.png']),
     ('CHORUS CHORD PATTERN', [M + 'c_pattern_chorus.png'])],
    note='Chords: D A G   Verse & Chorus: D A G D D   '
         'Strum: down-down-up-down-up on first D; bracketed chords [down-down-up - down-down-up]',
    out_name='CCR-Bad-Moon-Rising-Challenge.png',
)

# ------------------------------------- 6 CCR Proud Mary (Challenge Song 3)
make_card(
    'e-XedYIyKC0', 'PROUD MARY',
    'Creedence Clearwater Revival  ·  CCR Challenge Song 3  ·  Bernadette Teaches Music',
    [('CHORDS', [P + 'c_chord_D.png', P + 'c_chord_A.png', P + 'c_chord_Bm.png']),
     ('STRUMMING PATTERN', [P + 'c_strum_options.png', P + 'c_chuck.png',
                            P + 'c_bm_trans.png']),
     ('INTRO & INSTRUMENTAL CHORDS', [P + 'c_intro_C.png', P + 'c_intro_F.png',
                                     P + 'c_intro_A.png', P + 'c_intro_D.png',
                                     P + 'c_intro_G.png']),
     ('CHORD PATTERN', [P + 'c_pattern_intro.png'])],
    note='Chords: D A Bm   Intro & instrumental: C F A D G   '
         'Strum: down-down-down-down; chuck pattern down-up',
    out_name='CCR-Proud-Mary.png',
)

# ------------------------------------- 7 CCR Down on the Corner (CCR Challenge)
make_card(
    'tFfQAG50H2g', 'DOWN ON THE CORNER',
    'Creedence Clearwater Revival  ·  CCR Challenge  ·  Bernadette Teaches Music',
    [('CHORDS', [C + 'c_chord_C.png', C + 'c_chord_G.png', C + 'c_chord_F.png']),
     ('STRUMMING PATTERN', [C + 'c_strum_option.png', C + 'c_strum_count.png']),
     ('CHORD PATTERN  ·  INTRO', [C + 'c_pattern_intro.png']),
     ('CHORD PATTERN  ·  VERSE + CHORUS', [C + 'c_pattern_verse.png']),
     ('BASS LINE PICKING (TAB)', [C + 'c_tab_bass.png'])],
    note='Chords: C G F   Strum: down-down-down-down-up   '
         'Intro: C C G C C C G C F F C C C C G C',
    out_name='CCR-Down-on-the-Corner.png',
)
print('ALL OK')
