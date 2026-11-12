"""Batch 6 card builder (GuitarZero2HeroExpress).

Append one entry per song to ENTRIES.  Run:
    py -3.14 b6_build.py            # builds only missing outputs
    py -3.14 b6_build.py --force    # rebuild everything
"""
import os
import sys

from b6_compose import make_card

ENTRIES = []


def add(video_id, title, artist, tag, sections, note, out_path):
    ENTRIES.append(dict(video_id=video_id, title=title.upper(), artist=artist,
                        tag=tag, sections=sections, note=note, out_path=out_path))


def _note_lines(note, width):
    """Mirror compose_lib.build so we can warn about overflow."""
    from PIL import ImageFont
    f = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 24)
    max_w = width - 112
    words, lines, cur = note.split(' '), [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if f.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _card_width(sections):
    gap, pad = 32, 56
    body_w = 0
    for label, paths in sections:
        from PIL import Image
        w = sum(Image.open(p).size[0] + 48 for p in paths) + gap * (len(paths) - 1)
        body_w = max(body_w, w)
    return max(1400, body_w + pad * 2)


# ---------------------------------------------------------------- Bruno Mars
add(
    'd-XxGbC1SKQ', 'Talking To The Moon', 'Bruno Mars', 'Tabs + Chords',
    [('CHORD PATTERN & STRUMMING  ·  INTRO',
      ['frames/b6_d-XxGbC1SKQ/c_intro.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE',
      ['frames/b6_d-XxGbC1SKQ/c_verse.png']),
     ('CHORD PATTERN & STRUMMING  ·  PRECHORUS',
      ['frames/b6_d-XxGbC1SKQ/c_prechorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS',
      ['frames/b6_d-XxGbC1SKQ/c_chorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  BRIDGE',
      ['frames/b6_d-XxGbC1SKQ/c_bridge.png'])],
    'Chords: Intro C C | Verse C E7 Am G F | Prechorus Dm G Dm G | '
    'Chorus F G Am F G Am F G C G/B Am G F G Am G D | Bridge Dm C Dm G   '
    'Strumming: D-D-D-D-D-D-D-DU (change chords on the highlighted strum).  '
    'No TAB notation panel appears - only a chord fingering diagram.',
    'out_gz/Bruno-Mars-Talking-To-The-Moon.png',
)

add(
    'P6syTu1Pv0M', "That's What I Like", 'Bruno Mars', 'Tabs + Chords',
    [('TAB  ·  PC RIFF', ['frames/b6_P6syTu1Pv0M/c_tab_pc.png']),
     ('TAB  ·  C RIFF', ['frames/b6_P6syTu1Pv0M/c_tab_c.png']),
     ('CHORD PATTERN & STRUMMING  ·  INTRO',
      ['frames/b6_P6syTu1Pv0M/c_intro.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE',
      ['frames/b6_P6syTu1Pv0M/c_verse.png']),
     ('CHORD PATTERN & STRUMMING  ·  PRECHORUS',
      ['frames/b6_P6syTu1Pv0M/c_prechorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS',
      ['frames/b6_P6syTu1Pv0M/c_chorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  BRIDGE',
      ['frames/b6_P6syTu1Pv0M/c_bridge.png'])],
    'Chords: Verse Bbm/Eb Bbm/Ab Fm7 Ab/Bb | Prechorus Bbm/Eb Bbm/Ab Fm7 PC Riff | '
    'Chorus Bbm/Eb Bbm/Ab Fm7 Ab/Bb / Bbm/Eb Bbm/Ab Fm7 C Riff   '
    'Strumming: D X D X XX (1+2+3+4+); chorus D-UX-D---D-D-DU',
    'out_gz/Bruno-Mars-Thats-What-I-Like.png',
)

add(
    '_C9O4AqPp-4', 'Die With A Smile', 'Bruno Mars & Lady Gaga', 'Tabs + Chords',
    [('TAB  ·  SOLO', ['frames/b6__C9O4AqPp-4/c_tab.png']),
     ('CHORD PATTERN & STRUMMING  ·  INTRO',
      ['frames/b6__C9O4AqPp-4/c_intro.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE',
      ['frames/b6__C9O4AqPp-4/c_verse.png']),
     ('CHORD PATTERN & STRUMMING  ·  PRECHORUS',
      ['frames/b6__C9O4AqPp-4/c_prechorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS',
      ['frames/b6__C9O4AqPp-4/c_chorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  BRIDGE',
      ['frames/b6__C9O4AqPp-4/c_bridge.png']),
     ('CHORD PATTERN & STRUMMING  ·  FINAL CHORUS',
      ['frames/b6__C9O4AqPp-4/c_final.png'])],
    'Chords: Intro AM7 AM7 DM7 DM7 | Verse AM7 AM7 DM7 DM7 (x2) | '
    'Prechorus DM7 DM7 AM7 AM7 / C#m7 C#m7 F#7sus4 F#7 | '
    'Chorus Bm7 Bm7/E C#m7 F#m / Bm7 Bm7/E A E/G# F#m C#m7 / Bm7 E5 | '
    'Bridge Bm7 Bm7/E C#m7 F#m | Final Chorus + Bm7 C#7 F#m B   '
    'Strumming: D-DUDU | D-DUDU',
    'out_gz/Bruno-Mars-Lady-Gaga-Die-With-A-Smile.png',
)

add(
    'QAGWrCHshbo', 'Fake Love', 'BTS', 'Tabs + Chords',
    [('TAB  ·  MAIN RIFF', ['frames/b6_QAGWrCHshbo/c_tab_main.png']),
     ('TAB  ·  FAKE LOVE RIFF', ['frames/b6_QAGWrCHshbo/c_tab_fake.png']),
     ('CHORD PATTERN & STRUMMING  ·  GENERAL PROGRESSION',
      ['frames/b6_QAGWrCHshbo/c_chords.png',
       'frames/b6_QAGWrCHshbo/c_strum.png'])],
    'Chords: | Bb | C | Dm | Dm |   Strumming: D-DUDUDUDU   '
    'TAB: MAIN RIFF (G -2- D -0-0 A -1- / G -2- D -0-0 A -3-3 / G -10- D -10-10 A -0- / G -8- D -9-9 A -0-) '
    'and FAKE LOVE RIFF (G -2-2-2-2- D -0-0 A -1- / G -5-5-5-5- D -0-0 A -3-3 / G -9-9-9-9- D -0- A -0- / G -9-9-5-5- D -0- A -0-)',
    'out_gz/BTS-Fake-Love.png',
)

add(
    '4iTqHXa_JuI', 'My Universe', 'BTS', 'Tabs + Chords',
    [('CHORD PATTERN & STRUMMING  ·  INTRO',
      ['frames/b6_4iTqHXa_JuI/c_intro.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE',
      ['frames/b6_4iTqHXa_JuI/c_verse.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS',
      ['frames/b6_4iTqHXa_JuI/c_chorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  BRIDGE',
      ['frames/b6_4iTqHXa_JuI/c_bridge.png'])],
    'Chords: Intro Fsus2 Am7 G / Fsus2 Am7 G Em / Fsus2 Am7 G (x2) | '
    'Verse Fsus2 Am7 Gadd11 Gadd11 | Chorus Fsus2 Am7 G / Fsus2 Am7 G Em | '
    'Bridge Fsus2 Am7 Gadd11 Gadd11   Strumming: D--U-UDU (verse & bridge); '
    'chorus D--UDUD--UD-D-DU (change chords on the highlighted strum)',
    'out_gz/BTS-My-Universe.png',
)

add(
    'LirohMsL65s', 'Glycerine', 'Bush', 'Tabs + Chords',
    [('CHORD PATTERN & STRUMMING  ·  INTRO',
      ['frames/b6_LirohMsL65s/c_intro.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE',
      ['frames/b6_LirohMsL65s/c_verse.png']),
     ('CHORD PATTERN & STRUMMING  ·  POST CHORUS',
      ['frames/b6_LirohMsL65s/c_post.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS',
      ['frames/b6_LirohMsL65s/c_chorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  BRIDGE',
      ['frames/b6_LirohMsL65s/c_bridge.png'])],
    'Chords: Intro F5 C5 D5 Bb5 | Verse F5 C5 D5 Bb5 | Post Chorus F5 C5 Bb5 | '
    'Chorus F5 C5 D5 Bb5 | Bridge D5 Bb5 D5 Bb5 / Bb5 Bb5   '
    'Strumming: D-D-D-D-D-D-DU (accent the highlighted strums); '
    'post chorus X-D-D-DUD-D-D-DU (change chords on the highlighted strum).  '
    'No TAB notation panel appears.',
    'out_gz/Bush-Glycerine.png',
)

add(
    'ebAKSXveXNw', 'Cigarette Daydreams', 'Cage The Elephant', 'Tabs + Chords',
    [('CHORD PATTERN & STRUMMING  ·  INTRO',
      ['frames/b6_ebAKSXveXNw/c_intro.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE',
      ['frames/b6_ebAKSXveXNw/c_verse.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS 1',
      ['frames/b6_ebAKSXveXNw/c_chorus1.png']),
     ('CHORD PATTERN & STRUMMING  ·  BRIDGE',
      ['frames/b6_ebAKSXveXNw/c_bridge.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS 3',
      ['frames/b6_ebAKSXveXNw/c_chorus3.png'])],
    'Chords: Intro D Dmaj7 Em G A | Verse D Dmaj7 Em G A / D Dmaj7 Bm G A / '
    'D Dmaj7 Bm Em (repeat x2) | Chorus Bm D G F#m (repeat x4) | '
    'Bridge Em A Em D A / Em A Em Bm G / A A   '
    'Strumming: D-D-D-D-D-D-DU; chorus D---D-U---U-D-DU',
    'out_gz/Cage-The-Elephant-Cigarette-Daydreams.png',
)

add(
    'NXU1dy4cMxo', 'Dancing On My Own', 'Calum Scott', 'Tabs + Chords',
    [('TAB  ·  INTRO', ['frames/b6_NXU1dy4cMxo/c_tab_intro.png']),
     ('TAB  ·  VERSE', ['frames/b6_NXU1dy4cMxo/c_tab_verse.png']),
     ('TAB  ·  PRECHORUS', ['frames/b6_NXU1dy4cMxo/c_tab_prechorus.png']),
     ('TAB  ·  CHORUS', ['frames/b6_NXU1dy4cMxo/c_tab_chorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE / INSTRUMENTAL',
      ['frames/b6_NXU1dy4cMxo/c_ch_verse.png',
       'frames/b6_NXU1dy4cMxo/c_str_verse.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS',
      ['frames/b6_NXU1dy4cMxo/c_ch_chorus.png',
       'frames/b6_NXU1dy4cMxo/c_str_chorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  OUTRO',
      ['frames/b6_NXU1dy4cMxo/c_ch_outro.png',
       'frames/b6_NXU1dy4cMxo/c_str_outro.png'])],
    'Chords: Verse/Instrumental C G F F | Chorus C G F F x2 / Am7 G F F x2 | '
    'Bridge F G Am7 G | Outro C G F F / Am7 G F   Strumming: D-DU-UDU   '
    'TAB: G 0-0-0-0 A -3 (intro/verse), G -1-1-1-0 A -1 (prechorus/chorus x2)',
    'out_gz/Calum-Scott-Dancing-On-My-Own.png',
)

add(
    'FLSVU2NkJNg', 'You Are The Reason', 'Calum Scott', 'Tabs + Chords',
    [('TAB  ·  INTRO/VERSE 1 PT.1', ['frames/b6_FLSVU2NkJNg/c_tab_intro.png']),
     ('TAB  ·  VERSE 1 PT.2', ['frames/b6_FLSVU2NkJNg/c_tab_verse2.png']),
     ('TAB  ·  BREAK', ['frames/b6_FLSVU2NkJNg/c_tab_chorus.png']),
     ('TAB  ·  BRIDGE', ['frames/b6_FLSVU2NkJNg/c_tab_bridge.png']),
     ('CHORD PATTERN & STRUMMING  ·  INTRO/VERSE PT.1',
      ['frames/b6_FLSVU2NkJNg/c_ch_intro.png',
       'frames/b6_FLSVU2NkJNg/c_str_intro.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE PT.2',
      ['frames/b6_FLSVU2NkJNg/c_ch_verse2.png',
       'frames/b6_FLSVU2NkJNg/c_str_verse2.png']),
     ('CHORD PATTERN & STRUMMING  ·  CHORUS',
      ['frames/b6_FLSVU2NkJNg/c_ch_chorus.png',
       'frames/b6_FLSVU2NkJNg/c_str_chorus.png']),
     ('CHORD PATTERN & STRUMMING  ·  BREAK',
      ['frames/b6_FLSVU2NkJNg/c_ch_break.png',
       'frames/b6_FLSVU2NkJNg/c_str_break.png']),
     ('CHORD PATTERN & STRUMMING  ·  BRIDGE',
      ['frames/b6_FLSVU2NkJNg/c_ch_bridge.png',
       'frames/b6_FLSVU2NkJNg/c_str_bridge.png'])],
    'Chords: Intro/Verse1 G G Em7 Em7 / Cadd9 D G G | Verse2 G G Em7 Em7 / '
    'Cadd9 D Em7 Em7 G/B | Chorus Cadd9 D Em7 Em7 / Cadd9 D G D / Em7 D/F# G G/B C Cm | '
    'Break G x4 | Bridge Cadd9 D Em7 D/F# G G/B x2   Strumming: DDDDDD',
    'out_gz/Calum-Scott-You-Are-The-Reason.png',
)

add(
    'gaNh8-2ozT0', 'Father & Son', 'Cat Stevens', 'Tabs + Chords',
    [('TAB  ·  INTRO', ['frames/b6_gaNh8-2ozT0/c_tab_intro.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE 1',
      ['frames/b6_gaNh8-2ozT0/c_verse1.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE 1 VAR.',
      ['frames/b6_gaNh8-2ozT0/c_verse1var.png']),
     ('TAB  ·  BREAK RIFF', ['frames/b6_gaNh8-2ozT0/c_tab_break.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE 2',
      ['frames/b6_gaNh8-2ozT0/c_verse2.png']),
     ('TAB  ·  SOLO', ['frames/b6_gaNh8-2ozT0/c_tab_solo.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE 3',
      ['frames/b6_gaNh8-2ozT0/c_verse3.png']),
     ('CHORD PATTERN & STRUMMING  ·  VERSE 4',
      ['frames/b6_gaNh8-2ozT0/c_verse4.png'])],
    'Chords: Verse1 G D C Am7 / G Em Am7 D | Verse1 Var G D C Am7 / G Em D Riff | '
    'Verse2 G Bm C Am7 / G Em Am7 D / G Bm C Am7 / G Em D G G / D C Riff | '
    'Verse3 G D C Am7 / G Em Am7 D | Verse4 G Bm C Am7 / G Em D G G / D C G   '
    'Strumming: D---D-DU',
    'out_gz/Cat-Stevens-Father-Son.png',
)

add(
    'W3H68yxA3Dg', 'Attention', 'Charlie Puth', 'Tabs + Chords',
    [('TAB  ·  MAIN RIFF', ['frames/b6_W3H68yxA3Dg/c_tab.png']),
     ('CHORD PATTERN & STRUMMING  ·  GENERAL PROGRESSION',
      ['frames/b6_W3H68yxA3Dg/c_chords.png',
       'frames/b6_W3H68yxA3Dg/c_strum.png'])],
    'Chords: | Am | G | Em | F |   Strumming: D--UX-D---D-D-D-DU '
    '(played once for each chord)   TAB: main riff over Am, G, Em7, F',
    'out_gz/Charlie-Puth-Attention.png',
)


def main():
    force = '--force' in sys.argv
    for e in ENTRIES:
        missing = [p for _, paths in e['sections'] for p in paths
                   if not os.path.exists(p)]
        if missing:
            print('MISSING crops for', e['out_path'], missing)
            continue
        w = _card_width(e['sections'])
        lines = _note_lines(e['note'], w)
        if len(lines) > 2:
            print('NOTE TOO LONG (%d lines) for %s -> %r' % (len(lines), e['out_path'], lines))
            continue
        if os.path.exists(e['out_path']) and not force:
            print('skip (exists)', e['out_path'])
            continue
        make_card(
            e['video_id'], e['title'],
            '%s  ·  Guitar Cover  ·  %s  ·  GuitarZero2HeroExpress' % (e['artist'], e['tag']),
            e['sections'], note=e['note'], out_path=e['out_path'],
        )


main()
