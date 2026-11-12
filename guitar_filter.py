import json, re

rows = json.load(open('classified.json', encoding='utf-8'))

# A "song lesson" = an actual song being taught, with chords/tabs/strumming
LESSON_NOISE = re.compile(
    r"news|unboxing|review|studio tour|podcast|vlog|cover\b|live\b|"
    r"news|challenge coming|coming soon|q&a|giveaway|patreon|"
    r"equipment|gear|setup|tuner|clip-?on|anniversary|magazine|"
    r"concert|performance|how to host|news|"
    r"music theory challenge|ear training|whiteboard|notation|"
    r"device went viral|roadie|tuner|"
    r"chuck|how to|quick|hiii|meet |news|live music|"
    r"happy birthday|silent night|jingle bells|rudolph|feliz|"
    r"christmas|you are my sunshine|rockin' around|deck the halls|"
    r"last christmas|blue christmas|"
    r"bars|baritone|sax|cajon|drum|piano|keyboard",
    re.I)

# videos that teach an actual named song
SONG = re.compile(r'\bby\b.*\b|\bcover\b', re.I)

out = []
for r in rows:
    if r['inst'] != 'guitar':
        continue
    t = r['title']
    clean = not LESSON_NOISE.search(t)
    # genuine song tutorial heuristic
    song_lesson = bool(clean and (SONG.search(t) or re.search(r'(?i)how to play|tutorial', t)))
    out.append({**r, 'song_lesson': song_lesson, 'clean': clean})

json.dump(out, open('guitar_only.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('guitar videos:', len(out))
print('clean titles:', sum(1 for r in out if r['clean']))
print('song lessons:', sum(1 for r in out if r['song_lesson']))
print('song lessons + rock:', sum(1 for r in out if r['song_lesson'] and r['rock']))
print()
print('=== SONG LESSONS + ROCK ===')
for r in sorted([x for x in out if x['song_lesson'] and x['rock']], key=lambda x: (x['tab'], x['date'] or '')):
    print('%s %s %s | %s' % (r['tab'][:4], r['date'] or '?', r['id'], r['title'][:95]))
