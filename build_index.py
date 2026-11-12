import os, glob, re
from PIL import Image

CARDS = [
    ('Eagles-Hotel-California-Short.png', 'VAiS4VW7Eyc', 'Hotel California', 'The Eagles', 'Short'),
    ('Hotel-California.png', '0AFmPkjl9Gc', 'Hotel California', 'The Eagles', 'Long'),
    ('Sweet-Child-O-Mine.png', 'TIpQb2yaKYY', "Sweet Child O' Mine", "Guns N' Roses", 'Long'),
    ('Queen-Crazy-Little-Thing-Called-Love.png', 'PInjnaAQ54Y',
     'Crazy Little Thing Called Love', 'Queen', 'Short'),
    ('CCR-Bad-Moon-Rising-Jam-Along.png', 'O-sPPp1Qbbc', 'Bad Moon Rising (Jam-Along)',
     'Creedence Clearwater Revival', 'Short'),
    ('CCR-Bad-Moon-Rising-Easy-Chords.png', 'M8rVBAJhcLI', 'Bad Moon Rising (Easy Chords)',
     'Creedence Clearwater Revival', 'Long'),
    ('CCR-Bad-Moon-Rising-Challenge.png', 'dK27UjMr1UI', 'Bad Moon Rising (CCR Challenge)',
     'Creedence Clearwater Revival', 'Long'),
    ('CCR-Have-You-Ever-Seen-The-Rain.png', 'bYOD1FQ9sgc', 'Have You Ever Seen the Rain',
     'Creedence Clearwater Revival', 'Long'),
    ('CCR-Have-You-Ever-Seen-The-Rain-Short.png', 'olBBttZ9dxk', 'Have You Ever Seen the Rain',
     'Creedence Clearwater Revival', 'Short'),
    ('CCR-Down-on-the-Corner.png', 'tFfQAG50H2g', 'Down on the Corner',
     'Creedence Clearwater Revival', 'Long'),
    ('CCR-Proud-Mary.png', 'e-XedYIyKC0', 'Proud Mary', 'Creedence Clearwater Revival', 'Long'),
    ('White-Stripes-Were-Going-To-Be-Friends.png', '9pH9cccg6t8', "We're Going To Be Friends",
     'The White Stripes', 'Long'),
    ('Coldplay-Yellow.png', 'MfIguC1c2hQ', 'Yellow', 'Coldplay', 'Long'),
    ('Coldplay-Yellow-Short-2023.png', 'dYdX16QX84c', 'Yellow', 'Coldplay', 'Short'),
    ('Coldplay-Yellow-Short-2023b.png', 'Jo4tMXg6wmI', 'Yellow', 'Coldplay', 'Short'),
    ('Coldplay-Yellow-Short-2024.png', '4TnTv2t5dQU', 'Yellow', 'Coldplay', 'Short'),
    ('Coldplay-Viva-La-Vida.png', 'qrtWlngUm0c', 'Viva La Vida', 'Coldplay', 'Short'),
    ('Pearl-Jam-Last-Kiss.png', 'yRApqkc050s', 'Last Kiss', 'Pearl Jam', 'Short'),
    ('REM-Losing-My-Religion.png', 'KIFZsklFIfE', 'Losing My Religion', 'R.E.M.', 'Short'),
    ('Elvis-Love-Me-Tender.png', 'vqZuzVZgHW8', 'Love Me Tender', 'Elvis Presley', 'Short'),
    ('Johnny-Cash-I-Walk-The-Line.png', 'gQXGVDNC-ic', 'I Walk the Line', 'Johnny Cash', 'Short'),
    ('John-Denver-Take-Me-Home-Country-Roads.png', '2_Bc3Pb-BYw',
     'Take Me Home, Country Roads', 'John Denver', 'Short'),
]

lines = []
lines.append('# Рок китарни уроци — карти с табове и strumming pattern\n')
lines.append('Канал: https://www.youtube.com/@BernadetteTeachesMusic  ')
lines.append('Всяка карта съдържа извадени директно от видеото акордни диаграми, ')
lines.append('chord pattern и strumming pattern, плюс линк към видеото.\n')
lines.append('## Карти (%d)\n' % len(CARDS))
lines.append('| # | Песен | Изпълнител | Формат | Карта | Видео |')
lines.append('|---|---|---|---|---|---|')
for i, (png, vid, song, artist, kind) in enumerate(CARDS, 1):
    ok = 'OK' if os.path.exists(os.path.join('out', png)) else 'MISSING'
    lines.append('| %d | %s | %s | %s | `out/%s` (%s) | [link](https://www.youtube.com/watch?v=%s) |'
                 % (i, song, artist, kind, png, ok, vid))

missing = [c[0] for c in CARDS if not os.path.exists(os.path.join('out', c[0]))]
lines.append('\n**Липсващи карти:** %s' % (', '.join(missing) if missing else 'няма — всичките %d са готови' % len(CARDS)))

sizes = []
for png, vid, song, artist, kind in CARDS:
    p = os.path.join('out', png)
    if os.path.exists(p):
        im = Image.open(p)
        sizes.append((song, artist, im.size))

lines.append('\n## Размери на картите\n')
lines.append('| Песен | Изпълнител | Размер |')
lines.append('|---|---|---|')
for song, artist, sz in sizes:
    lines.append('| %s | %s | %dx%d |' % (song, artist, sz[0], sz[1]))

open('ROCK-CARDS-INDEX.md', 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines[:12]))
print('...')
print('written ROCK-CARDS-INDEX.md ; missing:', missing)
