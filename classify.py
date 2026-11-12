import json, re

rows = json.load(open('meta_all.json', encoding='utf-8'))

GUITAR = re.compile(r'guitar', re.I)
UKULELE = re.compile(r'ukulele|\buke\b|strumtober|30\s*day\s*uke|barre ?chord challenge', re.I)
ROCK_ARTISTS = re.compile(
    r"guns\s*n\s*roses|sweet child o'? ?mine|alice in chains|nirvana|metallica|"
    r"\bqueen\b|bee ?gees|fleetwood mac|pearl jam|oasis|radiohead|coldplay|"
    r"rage against|foo fighters|smashing pumpkins|red hot chili|led zeppelin|pink floyd|"
    r"deep purple|ac/?dc|aerosmith|green day|linkin park|jimi hendrix|the eagles|"
    r"creedence|ccr\b|\bstyx\b|foreigner|scorpions|\bjourney\b|toto|cheap trick|"
    r"nazareth|\bboston\b|dire straits|tom petty|bruce springsteen|neil young|bob dylan|"
    r"johnny cash|elvis|screaming trees|\btool\b|system of a down|megadeth|santana|"
    r"eric clapton|lynyrd skynyrd|doobie brothers|bon jovi|rush\b|\byes\b|genesis|"
    r"\babba\b|creed\b|black sabbath|the rolling stones|the police|\bcars\b|"
    r"van halen|\bkiss\b|arctic monkeys|smashing pumps|the strokes|white stripes|"
    r"rolling stones|creedence clearwater|dire straits|talking heads|ramones|"
    r"sex pistols|deep purple|jamiroquai|black keys|white stripes|fleetwood|"
    r"garbage\b|hoobastank|korn|limp bizkit|linkin park|system of a down|"
    r"rage|smashing|blur\b|oasis|travis\b|kaiser chiefs|star wars|pink floyd",
    re.I)

ROCK_SONGS = re.compile(
    r"sweet child o'? ?mine|hotel california|back in black|highway to hell|"
    r"smoke on the water|enter sandman|stairway to heaven|californication|"
    r"zombie\b|seven nation army|boys don'? t cry|come as you are|"
    r"purple rain|little wing|crazy little thing called love|we will rock you|"
    r"don'? t stop me now|another one bites the dust|november rain|"
    r"gimme gimme gimme|last kiss\b|the sound of silence|"
    r"killing in the name|back in black|welcome to the jungle|"
    r"roadhouse blues|midnight rider|crossroads|free bird|"
    r"iron man\b|enter sandman|sandman|master of puppeteer|"
    r"yesterday\b|come together|hey jude|let it be|wonderwall|"
    r"dreams\b|thunderstruck|highway to hell|tombstone|risk|"
    r"don't stop believin|hotel california|life in a northern town|"
    r"just like heaven|code of love|losing my religion|tubular bells|"
    r"baba o'riley|karma police|creep\b|paradise|cirice|stairway",
    re.I)

out = []
for r in rows:
    t = r['title']
    d = r['desc']
    blob = t + ' ' + d

    is_uke = bool(UKULELE.search(t)) and not GUITAR.search(t)
    is_gtr = bool(GUITAR.search(blob)) and not is_uke

    rock = bool(ROCK_ARTISTS.search(blob) or ROCK_SONGS.search(blob))
    tabs = bool(re.search(r'\btabs?\b', blob, re.I))

    out.append({**r,
                'inst': 'guitar' if is_gtr else ('ukulele' if is_uke else 'other'),
                'rock': rock,
                'tabs': tabs})

json.dump(out, open('classified.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

from collections import Counter
print(Counter(o['inst'] for o in out))
print('rock:', sum(1 for o in out if o['rock']))
print('guitar+rock:', sum(1 for o in out if o['inst'] == 'guitar' and o['rock']))
print('guitar+tabs:', sum(1 for o in out if o['inst'] == 'guitar' and o['tabs']))
