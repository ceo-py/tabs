from PIL import Image, ImageDraw, ImageFont
import b7_compose as C

_PROBE = ImageDraw.Draw(Image.new('RGB', (16, 16)))
_SUB_FONT = ImageFont.truetype(C.F_REG, 36)


def make(video_id, title, subtitle, sections, note, out_path):
    """Same as b7_compose.make_card but widens the canvas so the subtitle fits."""
    url = 'https://www.youtube.com/watch?v=' + video_id
    secs = [(label, [Image.open(p).convert('RGB') for p in paths])
            for label, paths in sections]
    need = int(_PROBE.textlength(subtitle, font=_SUB_FONT)) + 112 + 48
    C.build(out_path, title, subtitle, secs, url, note=note,
            min_width=max(1400, need))
    return out_path


make(
    'lhR434nrXK4',
    'VIVA LA VIDA',
    'Coldplay  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
    [('TAB  ·  VERSE', ['frames/b7_lhR434nrXK4/c_verse_tab.png']),
     ('TAB  ·  CHORUS', ['frames/b7_lhR434nrXK4/c_chorus_tab.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b7_lhR434nrXK4/c_verse_ch.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b7_lhR434nrXK4/c_chorus_ch.png']),
     ('CHORD PATTERN & STRUMMING  ·  BUILD UP', ['frames/b7_lhR434nrXK4/c_buildup_ch.png'])],
    note='Chords: Verse C D G Em  |  Chorus C D G Em  |  Build up C Em x3 D   Strumming: D-D-DUDU-UDU-UDU (verse, chorus, build up)',
    out_path='out_gz/Coldplay-Viva-La-Vida.png',
)

make(
    'v3oYhgz0Oa0',
    'YELLOW',
    'Coldplay  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
    [('CHORD PATTERN & STRUMMING  ·  INTRO', ['frames/b7_v3oYhgz0Oa0/c_intro.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b7_v3oYhgz0Oa0/c_verse.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b7_v3oYhgz0Oa0/c_chorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  BRIDGE', ['frames/b7_v3oYhgz0Oa0/c_bridge.png']),
     ('CHORD PATTERN & STRUMMING  ·  OUTRO', ['frames/b7_v3oYhgz0Oa0/c_outro.png'])],
    note='Chords: Intro B  Badd11  |  Verse B F#6 Emaj7  |  Chorus Emaj7 G#m F#6 x3 Emaj7  |  Bridge B F#6 Emaj7  |  Outro B F#m11 Emaj7   Strumming: D D D D D D D DU over 1 + 2 + 3 + 4 + (accented strums highlighted)   No TAB panel in this video — only chord-shape diagrams on the fretboard.',
    out_path='out_gz/Coldplay-Yellow.png',
)

make(
    'lif_1sv1-u4',
    'SOMETHING JUST LIKE THIS',
    'Coldplay & The Chainsmokers  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
    [('TAB  ·  SOFT P.CHORUS', ['frames/b7_lif_1sv1-u4/c_tab_soft.png']),
     ('TAB  ·  OUTRO LEAD', ['frames/b7_lif_1sv1-u4/c_tab_lag.png']),
     ('CHORD PATTERN & STRUMMING  ·  INTRO/VERSE 1', ['frames/b7_lif_1sv1-u4/c_intro.png']),
     ('CHORD PATTERN & STRUMMING  ·  PRECHORUS 1/2', ['frames/b7_lif_1sv1-u4/c_prech.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS 1/2', ['frames/b7_lif_1sv1-u4/c_chorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  INTERLUDE', ['frames/b7_lif_1sv1-u4/c_interlude.png'])],
    note='Chords: Intro/Verse 1 G A Bm7 A  |  Prechorus 1/2 G A Bm7 A  |  Chorus 1/2 G A Bm7 A  |  Interlude G A Bm7 / G D/F# A / D/F# A Bm7 / G D/F# A   Strumming: downstrokes (D) on 1 + 2 + 3 + 4 + - intro/verse D D D D, prechorus all downstrokes, chorus D | D D D | D D D | D D D D D D   TAB panels on screen: Soft P.Chorus (G A Bm7 Dmaj7/F#) and Outro Lead',
    out_path='out_gz/Coldplay-The-Chainsmokers-Something-Just-Like-This.png',
)

make(
    'm5bN4DFlVwU',
    'ASTRONOMY',
    'Conan Gray  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
    [('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b7_m5bN4DFlVwU/c_verse.png']),
     ('CHORD PATTERN & STRUMMING  ·  PRECHORUS', ['frames/b7_m5bN4DFlVwU/c_prechorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b7_m5bN4DFlVwU/c_chorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  BRIDGE', ['frames/b7_m5bN4DFlVwU/c_bridge.png'])],
    note='Chords: Verse and Chorus G6 F#m11 Em D over C/G C/G C/G C/G  |  Prechorus Em Em Em Em over C/G C/G C/G C/G  |  Bridge Am Am Am Am over Em Em D D   Strumming: D--UDU (all sections)   No TAB panel in this video - only a fretboard chord-shape diagram.',
    out_path='out_gz/Conan-Gray-Astronomy.png',
)

make(
    'Cm6hFhSFmlQ',
    'THE WORLD I KNOW',
    'Collective Soul  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
    [('TAB  ·  VERSE', ['frames/b7_Cm6hFhSFmlQ/c_verse_tab.png']),
     ('TAB  ·  BRIDGE', ['frames/b7_Cm6hFhSFmlQ/c_bri_tab.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b7_Cm6hFhSFmlQ/c_verse_ch.png', 'frames/b7_Cm6hFhSFmlQ/c_verse_str.png']),
     ('CHORD PATTERN & STRUMMING  ·  PRECHORUS', ['frames/b7_Cm6hFhSFmlQ/c_pre_ch.png', 'frames/b7_Cm6hFhSFmlQ/c_pre_str.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b7_Cm6hFhSFmlQ/c_cho_ch.png', 'frames/b7_Cm6hFhSFmlQ/c_cho_str.png']),
     ('CHORD PATTERN & STRUMMING  ·  BRIDGE', ['frames/b7_Cm6hFhSFmlQ/c_bri_chstr.png']),
     ('CHORD PATTERN & STRUMMING  ·  OUTRO', ['frames/b7_Cm6hFhSFmlQ/c_out_ch.png', 'frames/b7_Cm6hFhSFmlQ/c_out_str.png'])],
    note='Chords: Verse Bm F#m G A  |  Prechorus A A G Cadd9 G/B G  |  Chorus D A7 G D / D A7 Cadd9 G  |  Bridge Bm F#m G A  |  Outro D D/F# G A   Strumming: D - DUD - DU - UD - DUDU on 1 e + a 2 e + a 3 e + a 4 e + a (verse, bridge and outro end on UDU) - change chords on the highlighted strum   TAB: Bm(add11) F#m11(b13) G6 Aadd9,11',
    out_path='out_gz/Collective-Soul-The-World-I-Know.png',
)

make(
    '8TSla0VNVr8',
    'HEATHER',
    'Conan Gray  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
    [('CHORD PATTERN & STRUMMING  ·  MAIN PROGRESSION', ['frames/b7_8TSla0VNVr8/c_heather_ch.png', 'frames/b7_8TSla0VNVr8/c_heather_str.png'])],
    note='Chords (main progression): C Em Am F Fm   Strumming: D--UDU, played 4 times for this chord   Capo on 5th (shown on the fretboard diagram)   No TAB panel in this video - only the fretboard chord-shape diagram.',
    out_path='out_gz/Conan-Gray-Heather.png',
)

make(
    'iF0PcNmg0BA',
    'HIGHER',
    'Creed  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
    [('TAB  ·  INTRO', ['frames/b7_iF0PcNmg0BA/c_intro.png']),
     ('TAB  ·  VERSE 1', ['frames/b7_iF0PcNmg0BA/c_verse1.png']),
     ('TAB  ·  PRECHORUS 1', ['frames/b7_iF0PcNmg0BA/c_pre1.png']),
     ('TAB  ·  CHORUS 1', ['frames/b7_iF0PcNmg0BA/c_chorus1.png']),
     ('TAB  ·  BRIDGE', ['frames/b7_iF0PcNmg0BA/c_bridge.png']),
     ('TAB  ·  CHORUS 3', ['frames/b7_iF0PcNmg0BA/c_chorus3.png'])],
    note='On-screen TAB sections: Intro, Verse 1, Prechorus 1, Chorus 1, Verse 2, Prechorus 2, Chorus 2, Prechorus 3, Break, Bridge, Interlude, Chorus 3   No chord-name panel and no strumming pattern are shown in this video - only the ASCII TAB (fret numbers) and the fretboard chord-shape diagram.',
    out_path='out_gz/Creed-Higher.png',
)

make(
    'yL94BVu9FGU',
    'ONE LAST BREATH',
    'Creed  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
    [('TAB  ·  INTRO', ['frames/b7_yL94BVu9FGU/c_intro.png']),
     ('TAB  ·  VERSE 1', ['frames/b7_yL94BVu9FGU/c_verse1.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS 1', ['frames/b7_yL94BVu9FGU/c_chorus1.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS 2', ['frames/b7_yL94BVu9FGU/c_chorus2.png']),
     ('CHORD PATTERN & STRUMMING  ·  BRIDGE', ['frames/b7_yL94BVu9FGU/c_bridge.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS 3', ['frames/b7_yL94BVu9FGU/c_chorus3.png'])],
    note='Chords: Chorus 1 and Quiet Chorus D F#11 Bm G  |  Chorus 2 and Chorus 3 D/A F#5 B5 G5 (repeat)  |  Bridge E5 Esu2 G D/A, A5 B5 G5 (repeat)   Strumming: D - - - D - - UDUD - - - DU on 1 + 2 + 3 + 4 + (change chords on the highlighted strum)   TAB panels are shown for Intro, Verse 1, Break, Verse 2 and Outro',
    out_path='out_gz/Creed-One-Last-Breath.png',
)

make(
    'IuJc3rIKxzc',
    'BAD MOON RISING',
    'Creedence Clearwater Revival  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
    [('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b7_IuJc3rIKxzc/c_verse.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b7_IuJc3rIKxzc/c_chorus.png'])],
    note='Chords: Verse D A G D -  |  Chorus G G D D / A G D -   Strumming: Verse D - D - - UDUDUDUDUDUDUDU (fret ring finger on the highlighted strums), Chorus D - D - - UDU on 1 + 2 + 3 + 4 +   No TAB panel in this video - only the fretboard chord-shape diagram.',
    out_path='out_gz/Creedence-Clearwater-Revival-Bad-Moon-Rising.png',
)

make(
    'Ee-UG7G4C3Y',
    'HAVE YOU EVER SEEN THE RAIN',
    'Creedence Clearwater Revival  ·  Guitar Cover  ·  Tabs + Chords  ·  GuitarZero2HeroExpress',
    [('CHORD PATTERN & STRUMMING  ·  INTRO', ['frames/b7_Ee-UG7G4C3Y/c_intro.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE', ['frames/b7_Ee-UG7G4C3Y/c_verse.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS', ['frames/b7_Ee-UG7G4C3Y/c_chorus.png'])],
    note='Chords: Intro Am F C G / C C  |  Verse C C C C / G G C C  |  Chorus F G C C/B Am Am7/G x2 / F G C C   Strumming: DUXUDUDU (change chords on the highlighted strum)   No TAB panel in this video - only the fretboard chord-shape diagram.',
    out_path='out_gz/Creedence-Clearwater-Revival-Have-You-Ever-Seen-The-Rain.png',
)
