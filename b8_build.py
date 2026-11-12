"""Batch 8 card builder (GuitarZero2HeroExpress).

Usage: py -3.14 b8_build.py [id ...]   (no args = build all)
"""
import sys
from b8_compose import make_card, wrap_note, font, F_REG

CARDS = [
    dict(
        video_id='OYTcux3056o',
        title='AMERICAN PIE',
        subtitle='Don McLean  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('CHORD PATTERN & STRUMMING  ·  SOFT VERSE', ['frames/b8_OYTcux3056o/c_softverse.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE PT.1', ['frames/b8_OYTcux3056o/c_verse1.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE PT.2', ['frames/b8_OYTcux3056o/c_verse2.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b8_OYTcux3056o/c_chorus.png']),
        ],
        note='Chords: Soft verse G D/F# Em Am C Em D | V1 G Am C Am Em D D G D/F# Em Am C Em A7 D D | '
             'V2 Em D Em D C G/B Am C D7 G D/F# Em Am C | Chorus G C G D x3 Em A7 Em D7  ·  '
             'Strumming: V1 DUDUDDUDUU, V2 DUDUDUDUDU, Chorus DUDUDUDU  ·  No TAB shown.',
        out_path='out_gz/Don-McLean-American-Pie.png',
    ),
    dict(
        video_id='yCreWjATJqY',
        title='VINCENT (STARRY STARRY NIGHT)',
        subtitle='Don McLean  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  VERSE 1', ['frames/b8_yCreWjATJqY/c_tab_269.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE 1', ['frames/b8_yCreWjATJqY/c_grid_269.png']),
            ('TAB  ·  CHORUS 1', ['frames/b8_yCreWjATJqY/c_tab_325.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS 1', ['frames/b8_yCreWjATJqY/c_grid_325.png']),
            ('TAB  ·  BRIDGE', ['frames/b8_yCreWjATJqY/c_tab_437.png']),
            ('CHORD PATTERN & STRUMMING  ·  BRIDGE', ['frames/b8_yCreWjATJqY/c_grid_437.png']),
        ],
        note='Chords: Verse 1 G G Am Am C D7 G G | Chorus 1 Am D7 G G/F# Em Am D7 Em A7 Am D7 G G | '
             'Bridge Am D7 G G/F# Em Am Cm G F E7 Am C D7 G G  ·  '
             'Strumming: strum-bracket rhythm shown under every TAB line.',
        out_path='out_gz/Don-McLean-Vincent-Starry-Starry-Night.png',
    ),
    dict(
        video_id='w1WgEw3j3Ic',
        title='AFTERGLOW',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b8_w1WgEw3j3Ic/c_verse.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS 1', ['frames/b8_w1WgEw3j3Ic/c_chorus1.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS 2', ['frames/b8_w1WgEw3j3Ic/c_chorus2.png']),
        ],
        note='Chords: Verse G G Csus2 Csus2 Dsus4 Em7 Csus2 Csus2 | Chorus 1 Csus2 Csus2 G Dsus4 (x5) '
             'Csus2 Csus2 G G | Chorus 2 Csus2 Csus2 G Dsus4  ·  Strumming: D-D-D-D-D-D-D-D-DU over '
             '1 + 2 + 3 + 4 + (accent the highlighted strum).',
        out_path='out_gz/Ed-Sheeran-Afterglow.png',
    ),
    dict(
        video_id='oWkYpapgABc',
        title='BAD HABITS',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  PRECHORUS', ['frames/b8_oWkYpapgABc/c_prechorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b8_oWkYpapgABc/c_verse.png']),
            ('CHORD PATTERN & STRUMMING  ·  BRIDGE', ['frames/b8_oWkYpapgABc/c_bridge.png']),
            ('TAB  ·  CHORUS', ['frames/b8_oWkYpapgABc/c_chorus.png']),
        ],
        note='Chords: Verse Am CM7 F F G | Bridge Am CM7 Dm F G | Prechorus tab Am Cmaj7 Dm | '
             'Chorus tab Bm Dmaj7 Gadd9 Gadd9 A / Bm Dmaj7 Em7 G  ·  '
             'Strumming: DDDDDDDD on 1 + 2 + 3 + 4 + (change chords on 3 beat).',
        out_path='out_gz/Ed-Sheeran-Bad-Habits.png',
    ),
    dict(
        video_id='kzD_YraRlr4',
        title='BOAT',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('CHORD PATTERN & STRUMMING  ·  PRECHORUS', ['frames/b8_kzD_YraRlr4/c_prechorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b8_kzD_YraRlr4/c_verse.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b8_kzD_YraRlr4/c_chorus.png']),
        ],
        note='Chords: Prechorus Cadd9 G D / Cadd9 Em7 D Cadd9 | Verse Am7 Gadd11 C/E Fsus2 Fsus2 | '
             'Chorus C C/D C/E Gadd11/B Fsus2 Fsus2 (x4)  ·  Strumming: D-DUDU | D-DUDU over 1 2 3 4 5 6.',
        out_path='out_gz/Ed-Sheeran-Boat.png',
    ),
    dict(
        video_id='e-uOSjGyGrY',
        title='BEST PART OF ME',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Solo  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  VERSE RIFF', ['frames/b8_e-uOSjGyGrY/c_tabverse.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b8_e-uOSjGyGrY/c_chorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b8_e-uOSjGyGrY/c_verse.png']),
            ('CHORD PATTERN & STRUMMING  ·  PRECHORUS', ['frames/b8_e-uOSjGyGrY/c_prechorus.png']),
        ],
        note='Chords: Verse D D* Asus4* Bm7 Bm7* G* | Chorus D A G Bm7 A / D A G G / D A G Bm7 A (x2) | '
             'Prechorus G D A Bm7* A* / G D A A  ·  Strumming: verse D-DU, chorus D---D-DU, prechorus D-DU-UDU.',
        out_path='out_gz/Ed-Sheeran-Best-Part-Of-Me.png',
    ),
    dict(
        video_id='aBST752Efa4',
        title='DRUNK',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('CHORD PATTERN & STRUMMING  ·  PRE CHORUS', ['frames/b8_aBST752Efa4/c_prechorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b8_aBST752Efa4/c_verse.png']),
            ('CHORD PATTERN & STRUMMING  ·  BRIDGE', ['frames/b8_aBST752Efa4/c_bridge.png']),
        ],
        note='Chords: Pre chorus Em D G Cadd9 (x3) / G A7sus4 Cadd9 | Verse G G D/F# Em Em / '
             'Cadd9 Cadd9 D G G | Bridge Em G (x3) / Cadd9 Em  ·  '
             'Strumming: pre chorus D-D-D-DU, verse and bridge D--UDUD--UDUD-DU.',
        out_path='out_gz/Ed-Sheeran-Drunk.png',
    ),
    dict(
        video_id='lw0oVIpUbxk',
        title='ALL OF THE STARS',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b8_lw0oVIpUbxk/c_chorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b8_lw0oVIpUbxk/c_verse.png']),
            ('TAB  ·  VERSE', ['frames/b8_lw0oVIpUbxk/c_tabverse.png']),
        ],
        note='Chords: Chorus G(4) D(4) Em7(4) Cadd9(4) / G(4) D(4) Em7(1) Cadd9(1) G(1) D(1) | '
             'Verse Cadd9(1) G(1) Em7 D Cadd9(1) / G(2) D(2)  ·  '
             'Strumming: chorus D-DUDUDU, verse D-D--UDU  ·  TAB panels are shown for VERSE, CHORUS and BRIDGE.',
        out_path='out_gz/Ed-Sheeran-All-Of-The-Stars.png',
    ),
    dict(
        video_id='tlQvOA52XSc',
        title='BEAUTIFUL PEOPLE',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  MAIN', ['frames/b8_tlQvOA52XSc/c_tab.png']),
            ('CHORD PATTERN & STRUMMING  ·  CAPO PROGRESSION', ['frames/b8_tlQvOA52XSc/c_prog.png']),
        ],
        note='Chords: Capo progression Am C F F Em  ·  Strumming: D---D-DU-UD-D-DU  ·  '
             'TAB staff shown in 4/4 with strum rhythm symbols.',
        out_path='out_gz/Ed-Sheeran-Beautiful-People.png',
    ),
    dict(
        video_id='wa5dDum3BFo',
        title='BLOODSTREAM',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  RIFF 2', ['frames/b8_wa5dDum3BFo/c_riff2.png']),
            ('TAB  ·  OUTRO', ['frames/b8_wa5dDum3BFo/c_outro.png']),
        ],
        note='TAB: riff 2 and outro shown as 6-line notation (strings E A D G B E, capo on 4th). '
             'No chord names or strumming pattern are printed in these frames.',
        out_path='out_gz/Ed-Sheeran-Bloodstream.png',
    ),
    dict(
        video_id='ymV7jMxuaUA',
        title='FIRST TIMES',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  VERSE 2', ['frames/b8_ymV7jMxuaUA/c_tabverse.png']),
            ('TAB  ·  PRECHORUS', ['frames/b8_ymV7jMxuaUA/c_tabprechorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  PRECHORUS', ['frames/b8_ymV7jMxuaUA/c_prechorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b8_ymV7jMxuaUA/c_chorus.png']),
        ],
        note='Chords: Tab verse 2 G Am7 Em Em G Am7 Em C | Tab prechorus Em Em G G/B C C D D | '
             'Chords prechorus C C D D Em Em G G/B C C D D | Chorus G Am7 Em C (x3) G Am7 C D  ·  '
             'Strumming: D-D--UDU.',
        out_path='out_gz/Ed-Sheeran-First-Times.png',
    ),
    dict(
        video_id='bPatTlH_IxU',
        title='HAPPIER',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  MAIN RIFF', ['frames/b8_bPatTlH_IxU/c_tabriff.png']),
            ('CHORD PATTERN & STRUMMING  ·  PRECHORUS', ['frames/b8_bPatTlH_IxU/c_prechorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE 2', ['frames/b8_bPatTlH_IxU/c_verse2.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS',
             ['frames/b8_bPatTlH_IxU/c_chorus.png']),
        ],
        note='Chords: Prechorus Am7 F C | Verse 2 Am7 F C | Chorus Am7 F C C  ·  '
             'Strumming: D-D-D-D- (played once for each chord above)  ·  TAB main riff is shown.',
        out_path='out_gz/Ed-Sheeran-Happier.png',
    ),
    dict(
        video_id='Z5qMvrEuOpI',
        title="HEARTS DON'T BREAK AROUND HERE",
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  CHORUS PT.1', ['frames/b8_Z5qMvrEuOpI/c_chorus.png']),
            ('TAB  ·  PRECHORUS PT.2', ['frames/b8_Z5qMvrEuOpI/c_prechorus.png']),
            ('TAB  ·  TAG', ['frames/b8_Z5qMvrEuOpI/c_tag.png']),
        ],
        note='Chords: Chorus pt.1 (x3) C G / Am7 F G | Prechorus pt.2 F C / G | '
             'Tag Am7 Am7 G / F F  ·  TAB staff only - no strumming pattern is printed on screen.',
        out_path='out_gz/Ed-Sheeran-Hearts-Dont-Break-Around-Here.png',
    ),
    dict(
        video_id='FPU2cThXAFU',
        title='HOW WOULD YOU FEEL?',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  MAIN RIFF', ['frames/b8_FPU2cThXAFU/c_tabriff.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b8_FPU2cThXAFU/c_verse.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b8_FPU2cThXAFU/c_chorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  BRIDGE', ['frames/b8_FPU2cThXAFU/c_bridge.png']),
        ],
        note='Chords: Verse G Bm Cadd9 Cadd9 | Chorus G Bm Cadd9 Cadd9 (x3) Am Am D, '
             'G Bm Cadd9 Cadd9 (x2) | Bridge G Bm Cadd9 Cadd9 (x4)  ·  '
             'Strumming: D-D-D-DDU (shown with the main-riff TAB).',
        out_path='out_gz/Ed-Sheeran-How-Would-You-Feel.png',
    ),
    dict(
        video_id='pMszV9GdnCg',
        title="I DON'T CARE (ACOUSTIC)",
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  MAIN RIFF', ['frames/b8_pMszV9GdnCg/c_mainriff.png']),
        ],
        note='Chord names over the TAB: G, Em7, Cadd9, D, G (strings Eb Ab Db Bb Gb Eb, capo on 4th). '
             'Rhythm counts (1 e + a) are printed under the TAB staff. No strumming pattern or '
             'chord-pattern panel is shown.',
        out_path='out_gz/Ed-Sheeran-I-Dont-Care-Acoustic.png',
    ),
    dict(
        video_id='jO78M8b9asg',
        title='I SEE FIRE',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  INTRO/BREAK', ['frames/b8_jO78M8b9asg/c_tab.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE 2 & 3',
             ['frames/b8_jO78M8b9asg/c_verse.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS 2',
             ['frames/b8_jO78M8b9asg/c_chorus.png']),
        ],
        note='Chords: Verse 2 & 3 Em G D C / Em G D Am7 / Em G D C / Am7 G/B C (x2) | '
             'Chorus 2 Em7 Cadd9 Dsus4 Em7 (x3) Em7 Cadd9 Dsus4 Am7 / Am7 Am7 Am7 Am7  ·  '
             'Strumming: D-D-D-D---D-D-DU (change chords on highlighted strum).',
        out_path='out_gz/Ed-Sheeran-I-See-Fire.png',
    ),
    dict(
        video_id='0JDPugiwFRI',
        title="I'M A MESS",
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('CHORD PATTERN & STRUMMING  ·  PRECHORUS', ['frames/b8_0JDPugiwFRI/c_prechorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b8_0JDPugiwFRI/c_chorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  BRIDGE', ['frames/b8_0JDPugiwFRI/c_bridge.png']),
        ],
        note='Chords: Prechorus A(2) E(1) B(1) (x2) A | Chorus C#m(2) B(2) A(2) E F#m / '
             'C#m(2) B(2) A(2) E(2) / F#m A | Bridge C#m E2 B / A E1 B C#m  ·  '
             'Strumming: typical pattern D D D D D D D D (accented strums highlighted).',
        out_path='out_gz/Ed-Sheeran-Im-A-Mess.png',
    ),
    dict(
        video_id='I7gOCyXhYrg',
        title='KISS ME',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('CHORD PATTERN & STRUMMING  ·  PRECHORUS', ['frames/b8_I7gOCyXhYrg/c_prechorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE/CHORUS', ['frames/b8_I7gOCyXhYrg/c_verse.png']),
            ('CHORD PATTERN & STRUMMING  ·  BRIDGE', ['frames/b8_I7gOCyXhYrg/c_bridge.png']),
        ],
        note='Chords: Prechorus G A D5 Bm7 / G A | Verse/chorus D5 (A) Bm7 (A) G, D5 (D/A) | '
             'Bridge A(2) A/A#(2) Bm7(1) A(1) / G(2) Gm  ·  '
             'Strumming: DUDUDUDUDUDUDUDUDU (prechorus, verse/chorus), D-D-D-DU (bridge).',
        out_path='out_gz/Ed-Sheeran-Kiss-Me.png',
    ),
    dict(
        video_id='fUTl3vAMyzM',
        title='LEGO HOUSE',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  CHORUS RIFF', ['frames/b8_fUTl3vAMyzM/c_chorusriff.png']),
            ('TAB  ·  VERSE RIFF', ['frames/b8_fUTl3vAMyzM/c_verseriff.png']),
        ],
        note='TAB: chorus riff and verse riff shown as 6-line notation with rhythm counts under the staff. '
             'No chord names or strumming pattern are printed in these frames.',
        out_path='out_gz/Ed-Sheeran-Lego-House.png',
    ),
    dict(
        video_id='kXxoga-4JqY',
        title='LIFE GOES ON',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('CHORD PATTERN & STRUMMING  ·  PRECHORUS', ['frames/b8_kXxoga-4JqY/c_prechorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b8_kXxoga-4JqY/c_verse.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS 3', ['frames/b8_kXxoga-4JqY/c_chorus.png']),
        ],
        note='Chords: Prechorus Em Am G G | Verse C Fsus2 Fsus2 G / C Fsus2 F Fsus2 F G | '
             'Chorus 3 C Fsus2 Fsus2 C G / C Fsus2 F Fsus2 F G / C Fsus2 Fsus2 C G / Am G F C/E G  ·  '
             'Strumming: D-D-D-D-D---X--- / D---UDUD--UDUD-DU (verse and chorus).',
        out_path='out_gz/Ed-Sheeran-Life-Goes-On.png',
    ),
    dict(
        video_id='wnmx0ItiN-g',
        title='LOVE IN SLOW MOTION',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('CHORD PATTERN & STRUMMING  ·  PRECHORUS', ['frames/b8_wnmx0ItiN-g/c_prechorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b8_wnmx0ItiN-g/c_verse.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b8_wnmx0ItiN-g/c_chorus.png']),
        ],
        note='Chords: Prechorus Dm F C G | Verse C C G G / F F C G | Chorus C Dm F (x3) / Am G F  ·  '
             'Strumming: D--UDU | D--UDU (1 2 3 4 5 6).',
        out_path='out_gz/Ed-Sheeran-Love-In-Slow-Motion.png',
    ),
    dict(
        video_id='AleTTEqmkOI',
        title='ONE',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b8_AleTTEqmkOI/c_verse.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b8_AleTTEqmkOI/c_chorus.png']),
            ('TAB  ·  VERSE', ['frames/b8_AleTTEqmkOI/c_tabverse.png']),
            ('TAB  ·  CHORUS', ['frames/b8_AleTTEqmkOI/c_tabchorus.png']),
        ],
        note='Chords: Verse D D A Bm G D | Chorus D D A/C# A/C# / Bm G A G A  ·  '
             'Strumming: D--UDUD--UDUD-DU (change chords on highlighted strum)  ·  '
             'TAB staff is shown for the verse and the chorus.',
        out_path='out_gz/Ed-Sheeran-One.png',
    ),
    dict(
        video_id='4rGimHDLb68',
        title='ONE LIFE',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  VERSE', ['frames/b8_4rGimHDLb68/c_tabverse.png']),
            ('TAB  ·  CHORUS', ['frames/b8_4rGimHDLb68/c_tabchorus.png']),
            ('CHORD PATTERN & STRUMMING  ·  OUTRO', ['frames/b8_4rGimHDLb68/c_outro.png']),
        ],
        note='Chords: Verse tab G D/F# Em7 Cadd9 | Chorus tab G D/F# Cadd9 Em7 D (x2) | '
             'Outro G D/F# Em7 Cadd9  ·  Strumming: D-D-DUDU (chord played for 2 strumming patterns).',
        out_path='out_gz/Ed-Sheeran-One-Life.png',
    ),
    dict(
        video_id='eBi5f7LiXsI',
        title='OVERPASS GRAFFITI',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b8_eBi5f7LiXsI/c_verse.png']),
            ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b8_eBi5f7LiXsI/c_chorus.png']),
        ],
        note='Chords: Verse Am7 G Fsus2 Fsus2 G / Am7 G Fsus2 Fsus2 | '
             'Chorus C G Dm Am7/E Fsus2 (x2) / G G  ·  Strumming: D-D-DUDU | D-D-DUDU.',
        out_path='out_gz/Ed-Sheeran-Overpass-Graffiti.png',
    ),
    dict(
        video_id='W76V1agADTI',
        title='PENGUINS',
        subtitle='Ed Sheeran  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
        sections=[
            ('TAB  ·  PRECHORUS', ['frames/b8_W76V1agADTI/c_prechorus.png']),
            ('TAB  ·  VERSE', ['frames/b8_W76V1agADTI/c_verse.png']),
            ('TAB  ·  BRIDGE', ['frames/b8_W76V1agADTI/c_bridge.png']),
        ],
        note='Chords: Prechorus Dmaj7/F# G5 D Asus4 D G5 Asus4 Bm Dmaj7/F# | Verse D Bm Asus4 G5 | '
             'Bridge Bm G5 D Asus4 D (4x)  ·  TAB staff only - no strumming pattern is printed on screen.',
        out_path='out_gz/Ed-Sheeran-Penguins.png',
    ),
]


def main():
    want = set(sys.argv[1:])
    for c in CARDS:
        if want and c['video_id'] not in want:
            continue
        ls = wrap_note(c['note'], font(F_REG, 24), 1716)
        if len(ls) > 2:
            print('!! NOTE TOO LONG (%d lines) for %s' % (len(ls), c['video_id']))
        make_card(c['video_id'], c['title'], c['subtitle'], c['sections'],
                  c['note'], c['out_path'])


main()
