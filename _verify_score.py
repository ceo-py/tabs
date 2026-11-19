# -*- coding: utf-8 -*-
"""Final scoring pass: recompute rock/grunge/style metrics from the RAW title
lists stored by _verify_channels.py / _verify_new.py.

Metrics
  tabs       : video title indicates tablature
  rock_act   : title names a REAL rock/grunge/metal/alt/punk act
  rock_loose : rock_act OR a genre word (rock / metal / punk / grunge ...)
  grunge     : title names a 90s Seattle-grunge-scene act (strict)
  style      : title also indicates cover / lesson / playthrough (on-screen-tab format)

Also re-applies the PRIOR pass' exact regexes for an apples-to-apples diff.
"""
import json
import os
import re
import sys
import unicodedata


def norm(s):
    if not s:
        return ""
    out = []
    for ch in unicodedata.normalize("NFKC", s):
        cp = ord(ch)
        if 0x1D400 <= cp <= 0x1D7FF:
            out.append(chr(cp - 0x1D400 + 65))
        elif 0x1D7CE <= cp <= 0x1D7FF:
            out.append(chr(cp - 0x1D7CE + 48))
        elif 0x1F130 <= cp <= 0x1F189:
            out.append(chr(cp - 0x1F130 + 65))
        else:
            out.append(ch)
    return unicodedata.normalize("NFKC", "".join(out)).lower()


# ------------------------------------------------------------------ artists
ACT_NAMES = [
    # 90s grunge / Seattle
    "nirvana", "pearl jam", "soundgarden", "alice in chains", "stone temple pilots",
    "mudhoney", "screaming trees", "melvins", "hole", "garbage", "candlebox",
    "mad season", "tadpole", "temple of the dog", "mother love bone", "hokum",
    "veruca salt", "sea level", "sponge", "flotsam", "l7", "7 year bitch",
    "quicksand", "green river", "skin yard", "the fray", "malice n forgery",
    "david gedge", "the smugglers", "the presidents", "night time flyers",
    "the posies", "vancouver", "the tremolo beer gut", "hairy mary",
    "the solution", "jerry cantrell", "layne staley", "kurt cobain",
    # 90s alt / post-grunge mainstream
    "smashing pumpkins", "foo fighters", "the offspring", "green day",
    "rage against the machine", "audioslave", "tool", "a perfect circle",
    "weezer", "third eye blind", "garbage band", "the cranberries",
    "red hot chili peppers", "rhcp", "oasis", "blur", "radiohead",
    "nine inch nails", "pearl jam band", "silverchair", "bush",
    "matchbox twenty", "third eye", "staind", "incubus", "deftones",
    "godsmack", "korn", "limp bizkit", "coal chamber", "seether",
    "nickelback", "disturbed", "evanescence", "creed", "papa roach",
    "linkin park", "limp bizkit band", "korn band", "system of a down",
    "audioslave band", "marilyn manson", "the used", "yellowcard",
    "new found glory", "good charlotte", "simple plan", "sum 41",
    "blink 182", "blink-182", "lit band", "the offspring band",
    "the starting line", "story of the year", "taking back sunday",
    "brand new", "glassjaw", "coheed", "afi", "the used band",
    "a day to remember", "all time low", "paramore", "panic at the disco",
    "fall out boy", "my chemical romance", "the starting line band",
    "marianas trench", "bayside", "the academy is", "muse", "placebo",
    "supergrass", "the verve", "ocean colour scene", "ocean color scene",
    "stereophonics", "feeder", "ash band", "elastica", "catatonia",
    "echobelly", "republica", "urusei yatsura", "buffalo tom", "superdrag",
    "marcy playground", "eve 6", "letters to cleo", "semisonic",
    "vertical horizon", "collective soul", "better than ezra", "big wreck",
    "alien ant farm", "or band", "sponge band", "live band", "toad the wet sprocket",
    "dishwalla", "fuel band", "spacehog", "the strokes", "the white stripes",
    "the killjoys", "royal blood", "arctic monkeys", "kaiser chiefs",
    "the fratellis", "the darkness", "superheavy", "the verve pipe",
    # classic / 70s-80s rock
    "led zeppelin", "led zep", "queen", "david bowie", "the doors",
    "the rolling stones", "rolling stones", "the beatles", "beatles",
    "jimi hendrix", "hendrix", "pink floyd", "the who", "the clash",
    "sex pistols", "ramones", "the damned", "buzzcocks", "cheap trick",
    "deep purple", "alice cooper", "kiss band", "van halen", "aerosmith",
    "motley crue", "mötley crüe", "bon jovi", "def leppard", "whitesnake",
    "scorpions", "gun n roses", "guns n roses", "guns n' roses",
    "ac dc", "black sabbath", "iron maiden", "judas priest", "metallica",
    "pantera", "sepultura", "slayer", "megadeth", "anthrax", "slipknot",
    "gojira", "doom band", "manowar", "motörhead", "motorhead", "zz top",
    "rammstein", "misfits", "creedence", "lynyrd skynyrd", "skynyrd",
    "foreigner band", "journey band", "boston band", "heart band",
    "poison band", "europe band", "the eagles", "eagles band", "fleetwood mac",
    "the cars", "blondie", "the police", "duran duran", "depeche mode",
    "the cure", "joy division", "new order", "siouxsie", "bauhaus",
    "the smashing pumpkins", "golden earring", "twisted sister", "twisted sisters",
    "van der graaf", "the kinks", "the turtles", "the byrds", "buffalo springfield",
    "creedence clearwater", "the band", "the velvet underground", "nirvana band",
    "the animals", "the yardbirds", "the troggs", "the move", "the troggs",
    # metal
    "trivium", "killswitch engage", "lamb of god", "children of bodom",
    "amon amarth", "behemoth", "emperor metal", "opeth", "dragonforce",
    "volbeat", "mushroomhead", "five finger death punch", "ghost band",
    "sleep token", "bad omens", "parkway drive", "northlane", "sikth",
    "protest the hero", "periphery", "meshuggah", "tesseract",
    "animals as leaders", "polyphia", "neck deep", "asking alexandria",
    "bullet for my valentine", "bring me the horizon", "baroness",
    "mastodon", "high on fire", "primitive man", "cavalcade",
    "suffocation", "dying fetus", "cannibal corpse", "morbid angel",
    "carcass", "napalm death", "amputation", "arch enemy", "nile",
    "evergrey", "symphony x", "stratovarius", "helloween", "blind guardian",
    "rage", "slash band", "guns n' roses", "motörhead band",
    # punk / hardcore
    "nofx", "pennywise", "bad religion", "social distortion", "rancid",
    "descendents", "descendents band", "the exploited", "the casuals",
    "the adicts", "screeching weasel", "face to face", "the queers",
    "dead kennedys", "crass", "black flag", "minor threat", "bad brains",
    "agnostic front", "cro-mags", "the dicks", "negative approach",
    "middle class", "the germ s", "the germs", "circle jerks", "x band",
    "agent orange", "jigsaw band", "tilt band", "unreal band", "bold band",
    "nervous breakdown", "the affects", "dr feelgood", "the fed up",
    "the selvedge", "spudboys", "tco", "diesel", "the aborted",
    "the clique", "the hateful", "no cure", "fuzzbox", "the bears",
    "therapies", "the queens of the stone age", "fu turds",
    # misc 90s / 00s alt
    "the wallflowers", "third eye blind band", "the toadies",
    "7 year bitch band", "the suicide machines", "the bodies",
    "the killers", "kaiser chiefs band", "the verve band", "the disconnect",
    "the seed", "the maccabees", "the wedding present", "the powder",
    "the view", "the music", "the corals", "the cribs", "the rakes",
    "the subways", "the cribs", "the shapes", "the brunettes",
    "russian roulette", "the tempest", "the joystick", "the departures",
    "the god machine", "the morning of", "the revs", "the vamps",
    "the others", "the ordinary boys", "the twang", "the rumble",
    "the ayat", "the hours", "the bell", "the music band",
    "twisted sister band", "cage the elephant", "echo park",
    "nothing more", "bad wolves", "royal blood band", "the struts",
    "the fratellis band", "the wombats", "the view band",
    # metalcore / djent / modern
    "architects band", "polar bears", "polbear", "northlane band",
    "bad omens band", "ghost band metal", "twenty one pilots",
    "the used band rock", "a day to remember band",
    # --- acts observed in the unmatched-title audit ---
    "teenage bottlerocket", "mxpx", "the casualties", "guttermouth",
    "the lillingtons", "off with their heads", "the chats", "rush",
    "the smiths", "daron malakian", "lindemann", "the warning",
    "alkaline trio", "dillinger four", "avenged sevenfold", "masked intruder",
    "rise against", "maneskin", "swingin' utters", "street dogs",
    "dire straits", "toto", "operation ivy", "against me!", "anti-flag",
    "pixies", "primus", "till lindemann", "subhumans band", "7 seconds",
    "dropkick murphys", "bloodhound gang", "goldfinger band", "lit band",
    "ghost metal band", "mudvayne", "emigrate", "chevelle",
    "the meffs", "the methadones", "dan vapid", "the linda lindas",
    "clutch band", "eric clapton", "talking heads", "soda stereo",
    "los jaivas", "lenny kravitz", "boy pablo", "sublime band",
    "burzum", "bouncing souls", "citizen fish", "the briefs", "the spits",
    "the dwarves", "rudimentary peni", "mindless self indulgence",
    "reagan youth", "alter bridge", "faith no more", "living colour",
    "hot water music", "hatebreed", "the riverdales", "glenn's army",
    "the vandals", "the unseen", "cock sparrer", "me first and the gimme gimmes",
    "millencolin", "coldplay", "the refreshments", "the mighty mighty bosstones",
    "the ataris", "jimmy eat world", "motion city soundtrack", "the bicycles",
    "less than jake", "the scorpios", "the brains", "the dambuilders",
    "stereophonics band", "superheaven", "hundreds", "the brittany band",
    "the war on drugs", "the black keys", "royal trux", "the warhorses",
    "the dangers", "the leaves", "the hellacopters", "the flaming lips",
    "electric six", "the white stripes band", "the strokes band",
    "the fratellis band", "kaiser chiefs band", "the kooks", "the coral",
    "the band of horses", "the shins", "death cab for cutie",
    "the mountain goats", "the dodos", "the decemberists", "of montreal",
    "bon iver", "the national", "interpol band", "the shins band",
    "the flaming lips band", "electric six band", "the white stripes 2",
    "queens of the stone age", "ac/dc", "guns n' roses band",
    "oasis band", "the clash band", "the damned band", "buzzcocks band",
    "the police band", "the cure band", "joy division band", "new order band",
    "the stooges", "the velvet underground band", "the doors band",
    "the band band", "the eagles band", "creedence band", "the byrds band",
    "the kinks band", "the turtles band", "the beach boys", "the eagles 2",
    "bob dylan", "neil young", "tom petty", "bruce Springsteen",
    "steve vai", "joe satriani", "eric johnson", "nuno bettencourt",
    "john mayall", "bb king", "santana band", "santana guitar",
    "dream theater", "avenged 7fold", "static-x", "p.o.d.", "fear factory",
    "nailbomb", "seven hours after violet", "paradise lost band",
    "drowning pool", "seven seconds band", "chic band", "gorillaz band",
    "vulfpeck", "john frusciante", "jamiroquai", "stevie ray vaughan",
    "chuck berry", "eric clapton guitar", "tatsuro yamashita",
    "ichika nito", "tom misch", "fanfarrabias", "steve lacy", "vulf",
    "guns n’ roses", "guns n’ roses band", "the wombats", "the wombats band",
    "the lilac cube", "the verve band", "the smiths band", "the police 2",
    # --- second audit round ---
    "ozzy osbourne", "ozzy osbourne band", "måneskin", "maneskin",
    "against me!", "off!", "kid dynamite", "the copyrights", "booze & glory",
    "chixdiggit", "chon", "earth, wind & fire", "earth wind & fire",
    "frenzal rhomb", "the jasons", "subhumans", "goldfinger", "lit band",
    "clutch", "sublime", "rob zombie", "santana", "kansas", "parliament",
    "kool & the gang", "los prisioneros", "tears for fears", "the replacements",
    "paint it black", "chancho en piedra", "the meffs", "the methadones",
    "7 seconds", "dropkick murphys", "against me", "the exies",
    "the briefs", "the spits", "the dwarves", "rudimentary peni",
    "billie talent", "311", "adolescents", "wasted youth", "tool", "rush",
    "blur", "lit", "ghost", "journey",
    "reagan youth", "mindless self indulgence", "the meffs band",
]

# entries that are risky as bare words -> require word boundaries anyway, but
# we drop obvious generic words that are also common English
_GENERIC_RISK = {"the band", "the music", "the others", "the view", "the dance",
                 "or band", "live band", "fuel band", "ash band", "rage",
                 "holy", "heart band", "the view band", "the music band"}

# bare forms that are also common English words -> never match on their own
RISKY_BARE = {"air", "chic", "death", "heart", "boston", "europe",
              "poison", "foreigner", "the", "or", "live", "fuel", "ash",
              "rage", "holy", "vulf", "choc", "surf", "matchbox", "america"}


def _mk(names):
    parts = []
    for n in names:
        if n in _GENERIC_RISK:
            continue
        if n.endswith(" band"):
            base = n[:-5].strip()
            if len(base) < 4 or base in RISKY_BARE:
                continue
            n = base
        if n in RISKY_BARE:
            continue
        # lookarounds instead of \b so names ending in punctuation still work
        parts.append(r"(?<!\w)" + re.escape(n).replace(r"\ ", r"\s+") + r"(?!\w)")
    return re.compile("|".join(parts), re.I)

ROCK_ACT = _mk(ACT_NAMES)

# genre words (loose metric only)
GENRE_WORD = re.compile(
    r"\brock\b|\bmetal\b|\bpunk\b|\bgrunge\b|alternative rock|alt[- ]rock|"
    r"indie rock|hard rock|classic rock|rock'?n'? ?roll|rock and roll|"
    r"punk rock|hardcore"
)

# strict 90s Seattle grunge scene
GRUNGE = re.compile(
    r"\bnirvana\b|\bpearl jam\b|\bsoundgarden\b|\balice in chains\b|"
    r"\bstone temple pilots\b|\bstp\b|\bmudhoney\b|\bscreaming trees\b|"
    r"\bmelvins\b|\bhokum\b|\bmad season\b|\btemple of the dog\b|"
    r"\bmother love bone\b|\bgreen river\b|\bskin yard\b|\btadpole\b|"
    r"\bthe fray\b|\bmalice n forgery\b|\bdavid gedge\b|\bhole\b|\bgarbage\b|"
    r"\bcandlebox\b|\bveruca salt\b|\bmary go round\b|\bsea level\b|"
    r"\bsponge\b|\bflotsam\b|\bquicksand\b|\b7 year bitch\b|\bthe smugglers\b|"
    r"\bshut up and dance\b|\bthe presidents\b|\bl7\b|\bgrunge\b|"
    r"\blayne taylor\b|\bthe solution\b"
)

# on-screen-tab format marker
STYLE = re.compile(
    r"cover|playthrough|play through|lesson|tutorial|play\s?along|play-along|"
    r"demonstration|performance|session|jam|riff|how to play|song lesson|"
    r"tabs on screen|on screen tabs|with tabs"
)

TAB = re.compile(
    r"\btabs?\b|\btabbing\b|\btabbed\b|\btablature\b|tabs?\s*\+|\+\s*tabs?\b|"
    r"on.?screen tabs?|screen tabs?|with tabs?\b|tabs? in (the )?video|"
    r"tab in descri|\bt\s*\|\s*\w|with guitar tab"
)

# ---- the PRIOR pass' exact regexes (copied from _yt_final.py) for comparison ----
PRIOR_GRUNGE = re.compile(
    r"(nirvana|pearl jam|soundgarden|alice in chains|stone temple pilots|"
    r"mudhoney|screaming trees|melvins|dinosaur jr|hokum|mad season|"
    r"the fray|grunge|hole|garbage|veruca salt|mary go round)"
)
PRIOR_ROCK = re.compile(
    r"(nirvana|pearl jam|soundgarden|alice in chains|stone temple pilots|led zeppelin|"
    r"queen|david bowie|the doors|red hot chili peppers|r\.?e\.?m\.?|foo fighters|green day|"
    r"blink-?182|sum 41|simple plan|offspring|slipknot|metallica|iron maiden|black sabbath|"
    r"ac/?dc|motley crue|gun n roses|guns n roses|aerosmith|bon jovi|def leppard|scorpions|"
    r"whitesnake|van halen|oasis|blur|pulp|travis|keane|coldplay|lana del rey|the killers|"
    r"arctic monkeys|kaiser chiefs|the strokes|white stripes|royal blood|smashing pumpkins|"
    r"radiohead|fleetwood mac|eagles|creed|third eye blind|matchbox twenty|staind|incubus|"
    r"goo goo dolls|silverchair|korn|deftones|rage against the machine|system of a down|"
    r"audioslave|disturbed|evanescence|seether|nickelback|theory of a deadman|smash mouth|"
    r"golden earring|twisted sister|bad religion|ramones|descendents|misfits|sex pistols|"
    r"the damned|cheap trick|husker du|the dandy Warhols|sea level|"
    r"blink-182|bad religion|rancid|social distortion|offspring|"
    r"\brock\b|\bmetal\b|\bpunk\b|\bgrunge\b|alternative rock|alt rock|indie rock|hard rock|classic rock)"
)


def score(channel):
    vids = channel.get("videos") or []
    rows = []
    for v in vids:
        t = v.get("t") or ""
        n = norm(t)
        rows.append({
            "t": t, "url": v.get("url"), "id": v.get("id"),
            "tab": bool(TAB.search(n)),
            "rock_act": bool(ROCK_ACT.search(n)),
            "genre": bool(GENRE_WORD.search(n)),
            "grunge": bool(GRUNGE.search(n)),
            "style": bool(STYLE.search(n)),
            "rock_prior": bool(PRIOR_ROCK.search(n)),
            "grunge_prior": bool(PRIOR_GRUNGE.search(n)),
        })
    tabs = [r for r in rows if r["tab"]]
    return {
        "label": channel.get("label") or channel.get("channel"),
        "channel": channel.get("channel"),
        "channel_id": channel.get("channel_id"),
        "uploader_id": channel.get("uploader_id"),
        "channel_url": channel.get("channel_url"),
        "subs": channel.get("subs"),
        "total": channel.get("total"),
        "tabs": len(tabs),
        "rock_act": sum(1 for r in tabs if r["rock_act"]),
        "rock_loose": sum(1 for r in tabs if r["rock_act"] or r["genre"]),
        "grunge": sum(1 for r in tabs if r["grunge"]),
        "grunge_prior": sum(1 for r in tabs if r["grunge_prior"]),
        "rock_prior": sum(1 for r in tabs if r["rock_prior"]),
        "style": sum(1 for r in tabs if r["style"]),
        "rock_style": sum(1 for r in tabs if r["rock_act"] and r["style"]),
        "grunge_style": sum(1 for r in tabs if r["grunge"] and r["style"]),
        "rock_titles": [r["t"] for r in tabs if r["rock_act"] or r["genre"]],
        "grunge_titles": [r["t"] for r in tabs if r["grunge"]],
        "prior_only_titles": [r["t"] for r in tabs if r["rock_prior"] and not (r["rock_act"] or r["genre"])],
        "mine_only_titles": [r["t"] for r in tabs if (r["rock_act"] or r["genre"]) and not r["rock_prior"]],
    }


def main():
    files = sys.argv[1:] or ["_verify_channels.json", "_verify_new.json"]
    out = {}
    for f in files:
        if not os.path.exists(f):
            print("missing %s" % f)
            continue
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        for cid, ch in data.items():
            s = score(ch)
            s["src_file"] = f
            out[cid] = s
    with open("_verify_scores.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    rows = sorted(out.values(), key=lambda d: -d["rock_loose"])
    print("%-34s %-5s %-6s %-6s %-6s %-5s %-5s %-6s %-8s %s"
          % ("channel", "loose", "act", "priorR", "grunge", "grungeP", "tabs", "total", "subs", "handle"))
    for d in rows:
        print("%-34s %-5s %-6s %-6s %-6s %-5s %-5s %-6s %-8s %s"
              % (str(d["label"])[:34], d["rock_loose"], d["rock_act"], d["rock_prior"],
                 d["grunge"], d["grunge_prior"], d["tabs"], d["total"], d["subs"],
                 d.get("uploader_id")))


if __name__ == "__main__":
    main()
