import json, re

rows = json.load(open('classified.json', encoding='utf-8'))

# Instrument hints that imply a guitar (not ukulele) instructional video
GUITAR_HINT = re.compile(
    r'guitar|fretboard|fretting hand|pick(?:ing)?\b.*\b(?:up|down)\b|'
    r'barre ?chord|capo|power ?chord|open chord|'
    r'\btab(?:s|lature)?\b|chord diagram|chord chart|'
    r'strum(?:ming)? pattern',
    re.I)
UKULELE_HINT = re.compile(
    r'ukulele|\buke\b|\bu4e\b|'
    r'strumtober|30\s*day\s*uke|barre ?chord challenge|'
    r'uke ?should ?know|baritone ?uke|uke ?lockdown|'
    r'uke ?better ?not|30\s*day\s*uke\s*song',
    re.I)

NON_LESSON = re.compile(
    r"let's meet|meet in person|news|unboxing|review|studio tour|podcast|"
    r'challenge coming|coming soon|q&a|question|giveaway|subscribe|patreon|'
    r'equipment|gear|setup|tuner|clip-?on|anniversary|magazine|'
    r'how to host|concert|performance|cover\b|live\b|'
    r'music theory challenge|ear training|whiteboard|notation|'
    r'piano|keyboard|sax|percussion|cajon|drum',
    re.I)

ROCK_HINT = re.compile(
    r"guns\s*n\s*roses|sweet child o'? ?mine|alice in chains|nirvana|metallica|"
    r"\bqueen\b|bee ?gees|fleetwood mac|pearl jam|oasis|radiohead|coldplay|"
    r"rage against|foo fighters|smashing pumpkins|red hot chili|led zeppelin|pink floyd|"
    r"deep purple|ac/?dc|aerosmith|green day|linkin park|jimi hendrix|the eagles|"
    r"creedence|\bccr\b|\bstyx\b|foreigner|scorpions|\bjourney\b|toto|cheap trick|"
    r"nazareth|\bboston\b|dire straits|tom petty|bruce springsteen|neil young|bob dylan|"
    r"johnny cash|elvis|\btool\b|system of a down|megadeth|santana|"
    r"eric clapton|lynyrd skynyrd|doobie brothers|bon jovi|\brush\b|\byes\b|genesis|"
    r"\babba\b|\bcreed\b|black sabbath|rolling stones|the police|\bcars\b|"
    r"van halen|\bkiss\b|arctic monkeys|the strokes|white stripes|"
    r"ramones|sex pistols|jamiroquai|black keys|hoobastank|korn|limp bizkit|"
    r"blur\b|kaiser chiefs|talking heads|ramones|"
    r"hotel california|back in black|highway to hell|smoke on the water|"
    r"enter sandman|stairway to heaven|californication|seven nation army|"
    r"boys don'? t cry|come as you are|purple rain|little wing|"
    r"crazy little thing called love|we will rock you|november rain|"
    r"gimme gimme gimme|last kiss\b|don'? t stop me now|"
    r"another one bites the dust|welcome to the jungle|roadhouse blues|"
    r"midnight rider|free bird|iron man\b|master of puppeteer|"
    r"thunderstruck|tombstone|don'? t stop believin|little wing|"
    r"the sound of silence|killing in the name|life in a northern town|"
    r"just like heaven|code of love|losing my religion|tubular bells|"
    r"baba o'?riley|karma police|cirice|exit music for a film|"
    r"deja vu|ghostbusters|footloose|top gun|grease|"
    r"house of the rising sun|wild horses|man in the mirror|"
    r"take on me|rocky mountain highway|country roads|"
    r"california dreamin|surfin|wouldn'? t it be nice|"
    r"and i love her|yesterday\b|let it be|hey jude|come together|"
    r"wonderwall|dreams\b|boulevard of broken dreams|creep\b|"
    r"every breath you take|back in black|creep\b|"
    r"the rose\b|top of the world|dust in the wind|"
    r"heavy\b|metal\b|punk\b|grunge\b|alternative rock|hard rock|classic rock|"
    r"rock\b|indie rock|progressive rock",
    re.I)

for r in rows:
    blob = r['title'] + ' ' + (r['desc'] or '')
    title = r['title']

    uke = bool(UKULELE_HINT.search(blob))
    gtr = bool(GUITAR_HINT.search(blob))
    lesson = not NON_LESSON.search(title)

    if r['inst'] == 'guitar':
        inst = 'guitar'
    elif gtr and not uke and lesson:
        inst = 'guitar'
    elif uke and not gtr:
        inst = 'ukulele'
    else:
        inst = 'other'

    r['inst'] = inst
    r['rock'] = bool(ROCK_HINT.search(blob))
    r['is_lesson'] = lesson

json.dump(rows, open('classified.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

from collections import Counter
print(Counter(o['inst'] for o in rows))
print('guitar total:', sum(1 for o in rows if o['inst'] == 'guitar'))
print('guitar+rock:', sum(1 for o in rows if o['inst'] == 'guitar' and o['rock']))
print('guitar+rock+lesson:', sum(1 for o in rows if o['inst'] == 'guitar' and o['rock'] and o['is_lesson']))
print('guitar videos tab:', sum(1 for o in rows if o['inst'] == 'guitar' and o['tab'] == 'videos'))
print('guitar shorts tab:', sum(1 for o in rows if o['inst'] == 'guitar' and o['tab'] == 'shorts'))
