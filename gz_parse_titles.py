import json, re, collections, io, sys

sys.stdout.reconfigure(encoding='utf-8')

def parse_title(t):
    """Extract (song, artist, extra) from a channel title."""
    t = t.strip()
    # strip trailing pipe sections
    if '|' in t:
        head = t.split('|')[0].strip()
    else:
        head = t
    head = head.replace('🎸', '').strip()
    song = None; artist = None; extra = []
    # Pattern A: <song> Guitar Cover [Acoustic] [-] <artist> [+ ...]
    m = re.match(r'^(.*?)\s+Guitar\s+Cover\s+(?:Acoustic\s+)?(?:-\s*)?(.*)$', head, re.I)
    if m:
        song = m.group(1).strip(); artist_part = m.group(2).strip()
    else:
        # Pattern B: <song> Cover ... <artist>
        m = re.match(r'^(.*?)\s+Cover\s+(?:Acoustic\s+)?(?:-\s*)?(.*)$', head, re.I)
        if m:
            song = m.group(1).strip(); artist_part = m.group(2).strip()
        else:
            m = re.match(r'^(.*?)\s+Guitar\s+Backing\s+Track\s+-\s*(.*)$', head, re.I)
            if m:
                song = m.group(1).strip(); artist_part = m.group(2).strip()
            else:
                return None, None, head
    # artist_part: cut off at ' + ' or ' & ' markers
    artist_part = re.split(r'\s+\+\s+', artist_part)[0]
    artist_part = re.sub(r'\s*\(.*?\)\s*', ' ', artist_part)
    artist_part = re.sub(r'\s*[-–—]\s*$', '', artist_part).strip()
    artist_part = re.sub(r'\s+', ' ', artist_part)
    return song, artist_part or None, head

def main():
    artists = collections.Counter()
    rows = []
    for line in io.open('gz_videos.txt', encoding='utf-8-sig'):
        line = line.rstrip('\n')
        if not line.strip():
            continue
        vid, title = line.split('\t', 1)
        song, artist, head = parse_title(title)
        rows.append((vid, title, song, artist))
        if artist:
            artists[artist] += 1
    print("total rows:", len(rows))
    print("distinct artists:", len(artists))
    print("rows with artist:", sum(artists.values()))
    print("rows missing artist:")
    for vid, title, song, artist in rows:
        if not artist:
            print("   ", vid, "|", title)
    json.dump([{'id': r[0], 'title': r[1], 'song': r[2], 'artist': r[3]} for r in rows],
              io.open('gz_parsed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print()
    print("=== ARTIST COUNTS ===")
    for a, c in sorted(artists.items(), key=lambda x: (-x[1], x[0].lower())):
        print(f"{c}\t{a}")

main()
