# -*- coding: utf-8 -*-
"""Canonical artist normalisation + rock/genre judgement for GZ2H Express."""

# ---- artist name normalisation (parser output -> canonical) -----------------
ALIASES = {
    'REM': 'R.E.M.',
    'Lady gaga': 'Lady Gaga',
    'Goo Goo Dolls': 'The Goo Goo Dolls',
    'The Arctic Monkeys': 'Arctic Monkeys',
    'M\u00e5neskin': 'M\u00e5neskin',   # NFC fold of 'Maneskin' variants
    'Maneskin': 'M\u00e5neskin',
    'Pink': 'P!nk',
    'Me In Sunshine P!nk': 'P!nk',
    'Christmas Carol': 'Traditional',
    'Isaiah': 'Israel Kamakawiwo\u02bbole',
    'Israel IZ Kamakawiwo\u02bbole': 'Israel Kamakawiwo\u02bbole',
    'Israel IZ Kamakawiwo\u02bbol\u02bbole': 'Israel Kamakawiwo\u02bbole',
    'Joseph Vincent': 'Frank Valli',
    'Simon': 'Simon & Garfunkel',
    'MAX': 'MAX (German band)',
    'War Is Over John Lennon': 'John Lennon',
    'Aladdin Mena Massoud Naomi Scott': 'Mena Massoud & Naomi Scott',
    'Aladdin Zayn & Zhavia Ward': 'Zayn & Zhavia Ward',
    'Ellie The Last Of Us Part II': 'The Last Of Us Part II',
    'Ellie The Last Of Us Part 2': 'The Last Of Us Part II',
    'Joel The Last Of Us Part 2': 'The Last Of Us Part II',
    'The Last Of Us Part II': 'The Last Of Us Part II',
    'Marcus Mumford Major Lazer': 'Major Lazer ft. Marcus Mumford',
    'Fingerpicking - Queen': 'Queen',
    'Ed Sheeran +': 'Ed Sheeran',
    'The Beatles +': 'The Beatles',
    'Adele (Bob Dylan)': 'Bob Dylan',
    'The Arctic Monkeys': 'Arctic Monkeys',
    'Måneskin': 'M\u00e5neskin',
    'Seether & Amy Lee': 'Seether & Amy Lee',
    'Soundgarden Chris Cornell': 'Soundgarden & Chris Cornell',
    'Ed Sheeran Chance The Rapper PnB Rock': 'Ed Sheeran',
    'Ed Sheeran Bruno Mars Chris Stapleton': 'Ed Sheeran',
    'Ed Sheeran Taylor Swift': 'Ed Sheeran',
    'Ed Sheeran & Elton John': 'Ed Sheeran',
    'Ed Sheeran Justin Bieber': 'Ed Sheeran',
    'Taylor Swift Bon Iver': 'Taylor Swift',
    'Post Malone Swae Lee': 'Post Malone',
    'Dan + Shay Justin Bieber': 'Dan + Shay',
    'James Arthur Anne Marie': 'James Arthur',
    'James Arthur ft. Adam Lazarra': 'James Arthur',
    'JP Saxe Julia Michaels': 'Julia Michaels',
    'Justin Timberlake Anna Kendrick': 'Justin Timberlake',
    'Justin Timberlake Chris Stapleton': 'Justin Timberlake',
    'Jason Mraz Colbie Caillat': 'Jason Mraz & Colbie Caillat',
    'Khalid John Mayer': 'John Mayer',
    'Daniel Caesar Feat H.E.R': 'Daniel Caesar feat. H.E.R.',
    'Gotye Feat Kimbra': 'Gotye feat. Kimbra',
    'Gnash feat. Olivia O\'Brien': "Gnash feat. Olivia O'Brien",
    'Zayn Feat Sia': 'Zayn feat. Sia',
    'Zach Bryan Feat. Kacey Musgraves': 'Zach Bryan feat. Kacey Musgraves',
    'Ed Sheeran + ': 'Ed Sheeran',
    'Shawn Mendes Camila Cabello': 'Shawn Mendes & Camila Cabello',
    'Benny Blanco Halsey Khalid': 'Benny Blanco, Halsey & Khalid',
    'Ariana Grande & Justin Bieber': 'Ariana Grande & Justin Bieber',
    'Bruno Mars & Lady Gaga': 'Bruno Mars & Lady Gaga',
    'Lady Gaga & Bradley Cooper': 'Lady Gaga & Bradley Cooper',
    'Coldplay & The Chainsmokers': 'Coldplay',
    'Marshmello & Anne Marie': 'Marshmello & Anne-Marie',
    'Marshmello & Bastille': 'Marshmello & Bastille',
    'Marshmello YUNGBLUD': 'Yungblud',
    'Clean Bandit Zara Larsson': 'Clean Bandit & Zara Larsson',
    'Martin Garrix Dua Lipa': 'Martin Garrix & Dua Lipa',
    'The Chainsmokers Kelsea Ballerini': 'The Chainsmokers & Kelsea Ballerini',
    'Surf Mesa Madison Beer': 'Surf Mesa & Madison Beer',
    'Noah Cyrus PJ Harding': 'Noah Cyrus & PJ Harding',
    'Logic & Alessia Cara': 'Logic & Alessia Cara',
    'Lil Nas X Billy Ray Cyrus': 'Lil Nas X & Billy Ray Cyrus',
    'Luis Fonsi Feat Justin Bieber': 'Luis Fonsi feat. Justin Bieber',
    'The Mamas & The Papas': 'The Mamas & The Papas',
    'Daniel Caesar Feat H.E.R': 'Daniel Caesar feat. H.E.R.',
}

# ---- rock / non-rock judgement (by canonical artist) -----------------------
ROCK_ARTISTS = {
    # hard rock / classic rock / glam
    'AC/DC', 'Aerosmith', 'Alice In Chains', 'Audioslave', 'Boston', 'Bush',
    'Chuck Berry', 'Extreme', 'Foo Fighters', 'Gin Blossoms', 'Greta Van Fleet',
    'Hinder', 'Kansas', 'Kings Of Leon', 'Lynyrd Skynyrd', 'Måneskin',
    'Men At Work', 'Metallica', 'Pink Floyd', 'Poison', 'Powderfinger',
    'Queen', 'Rage Against The Machine', 'Santana', 'Stone Sour',
    'Stone Temple Pilots', 'The Band', 'The Beach Boys', 'The Calling',
    'Tom Petty', 'Toto', 'Van Morrison', 'Eddie Vedder',
    # punk / pop-punk / emo / alt
    'Avril Lavigne', 'Blink-182', 'Collective Soul', 'Dashboard Confessional',
    'Fall Out Boy', 'Franz Ferdinand', 'Green Day', 'My Chemical Romance',
    'Mod Sun', 'Panic! At The Disco', 'Paramore', 'Plain White T\'s',
    'Silverstein', 'Sum 41', 'The Offspring', 'Yungblud', '5SOS',
    'Machine Gun Kelly', 'Måneskin',
    # metal / hard rock / post-grunge / nu-metal
    'Bring Me The Horizon', 'Hoobastank', 'Limp Bizkit', 'Nickelback',
    'Papa Roach', 'Seether & Amy Lee', 'Slipknot', '3 Doors Down',
    'Lifehouse', 'Fuel', 'Greta Van Fleet',
    # grunge / alternative / indie / post-Britpop
    'Arctic Monkeys', 'Coldplay', 'The 1975', 'The Cranberries',
    'The Killers', 'The Smashing Pumpkins', 'The Verve', 'Death Cab For Cutie',
    'Imagine Dragons', 'Nirvana', 'No Doubt', 'Oasis', 'Pearl Jam',
    'Pixies', 'Radiohead', 'Red Hot Chili Peppers', 'Snow Patrol',
    'The Police', 'Twenty One Pilots', 'The Fray', 'Linkin Park',
    'Cage The Elephant', 'Incubus', 'Train', 'Matchbox Twenty', 'Maroon 5',
    'Secondhand Serenade', 'The Red Jumpsuit Apparatus', 'Dashboard Confessional',
    'The Goo Goo Dolls', 'Greta Van Fleet', 'Wheatus', 'Weezer',
    # blues rock / southern rock / roots rock
    'Ben E. King', 'Creedence Clearwater Revival', 'Creed', 'Crowded House',
    'Danny Vera', 'Don McLean', 'Eric Clapton', 'James Bay', 'John Mayer',
    'Bob Dylan', 'Neil Young', 'Simon & Garfunkel', 'Jeff Buckley',
    'Jim Croce', 'John Prine', 'Leonard Cohen', 'Hozier', 'Dave Matthews Band',
    '4 Non Blondes',
    # solo / other rock identities
    'David Bowie', 'George Harrison', 'John Lennon', 'Sting', 'Elvis Presley',
    'Chris Cornell', 'Chris Isaak', 'Soundgarden & Chris Cornell',
    'Fleetwood Mac', 'Tears For Fears',
    'The Animals', 'Bon Jovi',
    # classic rock bands that must never be missed
    'The Beatles', 'The Rolling Stones', 'U2', 'R.E.M.', 'INXS',
    'Three Days Grace', 'Alanis Morissette', 'America', 'Keane',
    'The Neighbourhood', 'The Mamas & The Papas', 'Edwin McCain',
    'Tracy Chapman', 'Yungblud & Marshmello',
}

# borderline calls that we explicitly decided (surfaced in NOTES)
BORDERLINE_ROCK = {
    'John Mayer', 'Coldplay', 'Maroon 5', 'Matchbox Twenty', 'Hozier',
    'Bob Dylan', 'Neil Young', 'Jeff Buckley', 'Jim Croce', 'John Prine',
    'Leonard Cohen', 'Secondhand Serenade', 'Machine Gun Kelly',
    'Train', 'Snow Patrol', 'The Police', 'The 1975',
    'The Goo Goo Dolls', 'The Cranberries', '4 Non Blondes', 'Ben E. King',
    'Crowded House', 'Don McLean', 'Bon Jovi', 'Tears For Fears',
    'John Lennon',
    'The Beatles', 'The Rolling Stones', 'U2', 'R.E.M.', 'INXS',
    'Alanis Morissette', 'America', 'Keane', 'The Neighbourhood',
    'The Mamas & The Papas', 'Edwin McCain', 'Tracy Chapman', 'Three Days Grace',
}

BORDERLINE_NON_ROCK = {
    'Elton John', 'Billy Joel', 'Phil Collins', 'Randy Newman', 'Neil Diamond',
    'Brenda Lee', 'Bobby Helms', 'Johnny Cash', 'Bob Marley', 'The Temptations',
    'George Michael', 'Stephen Sanchez', 'Kodaline', 'Bon Iver',
    'Sixpence None The Richer', 'Bing Crosby', 'Cat Stevens',
    'Yungblud & Marshmello',
}


def normalise_artist(a):
    if a is None:
        return None
    import unicodedata
    a = ' '.join(a.split())
    a = unicodedata.normalize('NFC', a)
    if a in ALIASES:
        return ALIASES[a]
    # fold okina / apostrophe variants so "Kamakawiwo'ole" == "Kamakawiwo'ole"
    folded = a.replace('\u02bb', "'").replace('\u2019', "'").replace('\u02bc', "'")
    for k, v in ALIASES.items():
        kf = k.replace('\u02bb', "'").replace('\u2019', "'").replace('\u02bc', "'")
        if folded == kf:
            return v
    return a


def is_rock(artist):
    if artist is None:
        return False
    return artist in ROCK_ARTISTS
