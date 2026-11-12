"""Build cards for the rock/tutorial batch (my own script; does not modify shared files)."""
import os, sys
sys.path.insert(0, r'D:\MiniMax Code Repos\Guitar Lessons')
os.chdir(r'D:\MiniMax Code Repos\Guitar Lessons')
from card import make_card

F = 'frames/'

# ---------------------------------------------------------------- Coldplay
make_card(
    'MfIguC1c2hQ',
    'YELLOW',
    'Coldplay  ·  EASY Guitar Tutorial  ·  Bernadette Teaches Music',
    [('CHORDS', [F + 'rock_MfIguC1c2hQ/c_chords_AED.png',
                 F + 'rock_MfIguC1c2hQ/c_chords_AAsus4.png',
                 F + 'rock_MfIguC1c2hQ/c_chords_DFsm7E.png',
                 F + 'rock_MfIguC1c2hQ/c_chords_AEmD.png']),
     ('CHORD PATTERN', [F + 'rock_MfIguC1c2hQ/c_pattern_verse.png']),
     ('STRUMMING PATTERN', [F + 'rock_MfIguC1c2hQ/c_strum_main.png',
                            F + 'rock_MfIguC1c2hQ/c_strum_trans.png'])],
    note='Chords: A E D (verse) | Asus4 (transition) | D F#m7 E (chorus) | A Em D (coda)   '
         'Verse chords: A A A A / E E E E / D D D D / A A A A   Strum: down-down-down-down-up',
    out_name='Coldplay-Yellow.png',
)

# ------------------------------------------------- CCR Bad Moon Rising (easy chords)
make_card(
    'M8rVBAJhcLI',
    'BAD MOON RISING',
    'Creedence Clearwater Revival  ·  EASY CHORDS  ·  Bernadette Teaches Music',
    [('CHORD PATTERN (ON-SCREEN LETTERS)', [F + 'rock_M8rVBAJhcLI/c_bar_verse1.png',
                                           F + 'rock_M8rVBAJhcLI/c_bar_verse2.png',
                                           F + 'rock_M8rVBAJhcLI/c_bar_chorus.png'])],
    note='Video shows chord LETTERS over a lyrics bar only - no fretboard diagrams and no '
         'strumming pattern graphic. Verse: D A G D D   Chorus: G G D D A G D',
    out_name='CCR-Bad-Moon-Rising-Easy-Chords.png',
)

# ------------------------------------------------------- The White Stripes
make_card(
    '9pH9cccg6t8',
    "WE'RE GOING TO BE FRIENDS",
    'The White Stripes  ·  EASY Guitar Tutorial  ·  Bernadette Teaches Music',
    [('CHORDS', [F + 'rock_9pH9cccg6t8/c_chords_GCDA.png']),
     ('CHORD PATTERN', [F + 'rock_9pH9cccg6t8/c_pattern_verse.png',
                        F + 'rock_9pH9cccg6t8/c_pattern_chorus.png']),
     ('FINGERPICKING', [F + 'rock_9pH9cccg6t8/c_fingerpicking.png']),
     ('STRUMMING PATTERN', [F + 'rock_9pH9cccg6t8/c_strum.png'])],
    note='Chords: G C D A   Fingerpicking: G chord 6-3-2-1, C chord 5-3-2-1, D chord 4-3-2-1   '
         'Verse pattern G G G G / C C G G   Chorus pattern D C G G / D C G G   Strum: down-down-up',
    out_name='White-Stripes-Were-Going-To-Be-Friends.png',
)
print('ALL OK')
