#!/usr/bin/env python3
"""
Build a 64434-word candidate list for TwoWords (reference regeneration of the curation method).

Sources are resolved via src_path() from $TWOWORDS_SOURCES, then v2/, then the v1/ source tree
(kaggle/, claude/, cities/, wordnet/, norvig/, profanity.txt all live under data/words/v1/).

Output:
  curated-rebuilt-64434.txt

NOTE: this does NOT overwrite the committed curated-by-chris-words.txt, which was further
hand-curated after generation. Run this to reproduce the *method*, then diff to review drift.

Rules:
- 3-8 lowercase a-z, at least one vowel
- No stops, no cities (uk+world), no profanity, no common acronyms
- Singular preference (drop plural if singular exists)
- No irregular plurals (men/man etc.)
- Priority order: foods + conversational/tech first (alpha within), then fill with rest (alpha)
- Exactly 64434 or as many clean words as possible
"""
import csv
import os
import re
import sys
from pathlib import Path

REQUIRED = 64434

BASE = Path(__file__).resolve().parent

# The raw word sources (kaggle/, claude/, cities/, wordnet/, norvig/, profanity.txt) live in the
# v1 source tree, not here in v2. Resolve each source from the first root that has it:
#   1. $TWOWORDS_SOURCES (optional override)   2. v2/ (in case sources are copied alongside)   3. v1/
# This lets the script run from a clean checkout instead of crashing on a missing file.
SOURCE_ROOTS = []
if os.environ.get("TWOWORDS_SOURCES"):
    SOURCE_ROOTS.append(Path(os.environ["TWOWORDS_SOURCES"]))
SOURCE_ROOTS += [BASE, BASE.parent / "v1"]


def src_path(rel: str):
    """Return the first existing source file for `rel`, or None if no root has it."""
    for root in SOURCE_ROOTS:
        p = root / rel
        if p.exists():
            return p
    return None

STOPS = set("""the and for are but not you all can had her was one our out day get has him his how man new now old see two way who boy end did its let put say she too use dad mom off own may try ask big per act set yet far few that with this from which have were they will their been other there would more such when any these time than some what about state only into also them said under first made should after shall your most could then over each year work where years between those same many through upon must well very general before used because being part like united people during public section number even make court case system much three both water law life company service good without order great american while however york long high national right does city just here world another data business given know program little since present every house men report less back place total large take down small county second control might research office last point form board still children interest federal study area action value fact line found power states within school against""".split())

CITIES = set()
uk_cities = src_path("cities/uk_cities.txt")
if uk_cities:
    with open(uk_cities, errors="ignore") as f:
        for line in f:
            t = line.strip().lower()
            if t:
                CITIES.add(t)
world_cities = src_path("cities/world-cities.csv")
if world_cities:
    with open(world_cities, encoding="utf-8", errors="ignore") as f:
        rdr = csv.reader(f)
        next(rdr, None)
        for row in rdr:
            if row and row[0]:
                n = row[0].strip().lower()
                if 3 <= len(n) <= 8 and n.isalpha():
                    CITIES.add(n)

PROFS = set()
profanity = src_path("profanity.txt")
if profanity:
    with open(profanity, errors="ignore") as f:
        for line in f:
            t = line.strip().lower()
            if 3 <= len(t) <= 8:
                PROFS.add(t)

ACRO_LIST = [
    'aaa','abc','api','aws','cdn','cli','cpu','css','dns','faq','ftp','gpu','gui','html','http','https','ide','ios','ip','iso','jpg','json','jwt','lcd','led','mac','md5','mp3','mp4','npm','pdf','png','ram','rom','rss','sdk','sql','ssh','ssl','svg','tcp','udp','url','usb','utf','vpn','xml','yaml','yml','gif','wav','mov','avi','exe','zip','tar','rar','deb','rpm','apk','ipa','bin','dat','tmp','log','src','lib','dev','prod','test','ci','cd','pr','mr','ui','ux','ai','ml','llm','gpt','bert','rag','db','orm','mvc','spa','pwa','wasm','webgl','sftp','saml','oidc','csrf','xss','nosql','rtc','p2p','www','csv','md'
]
ACROS = set(ACRO_LIST)

VOWELS = set("aeiou")
PAT = re.compile(r"^[a-z]{3,8}$")

def test_good(w: str) -> bool:
    if not w or not PAT.match(w):
        return False
    if not any(v in w for v in VOWELS):
        return False
    if w in STOPS or w in CITIES or w in PROFS or w in ACROS:
        return False
    return True

print("Loading sources...")

kag = []
p = src_path("kaggle/common_clean.txt")
if p:
    with open(p, encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip().lower()
            if test_good(w):
                kag.append(w)
    print(f"  kaggle: {len(kag)}")

foods = []
p = src_path("claude/food_dishes_final.txt")
if p:
    with open(p, encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip().lower()
            if test_good(w):
                foods.append(w)
    foods = sorted(set(foods))
    print(f"  foods: {len(foods)}")

conv_raw = [
    'wifi','bluetooth','yapping','yap','meme','vibe','vibes','ghost','flex','troll','spam','ping','zoom','tweet',
    'post','like','share','stream','chat','app','bug','crash','sync','cache','cloud','login','logout','update',
    'swipe','scroll','tap','click','drag','drop','snap','selfie','story','reel','clip','filter','hashtag','emoji',
    'gif','mood','cringe','sus','cap','bet','slay','lit','fire','dope','sick','sigma','drip','glow','hype','fomo',
    'jomo','stan','shade','salty','savage','roast','burn','ratio','mid','main','character','npc','alpha','beta',
    'omega','goat','based','cope','seethe','lfg','dub','fr','frfr','ong','af','fyi','tldr','imo','imho','idk','idc',
    'smh','wtf','wth','brb','afk','irl','fwiw','nsfw','sfw','ama','eli5','op','yolo','tiktok','insta','snapchat',
    'reddit','discord','slack','teams','meet','skype','facetime','airdrop','airplay','hotspot','vpn','dns','ip','mac',
    'gui','cli','api','sdk','ide','fix','patch','release','deploy','commit','push','pull','merge','branch','fork',
    'clone','repo','git','npm','yarn','pip','cargo','docker','pod','helm','aws','gcp','azure','lambda','s3','cdn',
    'ssl','tls','http','https','tcp','udp','ssh','ftp','jwt','oauth','sql','nosql','db','orm','react','vue','svelte',
    'angular','astro','next','nuxt','vite','webpack','babel','ts','js','jsx','tsx','css','scss','sass','html','xml',
    'json','yaml','yml','toml','md','csv','log','kafka','rabbit','redis','spark','flink','node','python','rust',
    'java','kotlin','swift','go','ruby','php','shell','bash','zsh','fish','make','cmake','gradle','maven','nginx',
    'haproxy','fastapi','flask','django','rails','spring','express','laravel','electron','flutter','ios','android',
    'linux','macos','windows','unix','async','await','promise','thread','lock','queue','stack','heap','array','list',
    'map','set','hash','tree','graph','vector','matrix','token','embed','prompt','agent','tool','chunk','index',
    'faiss','duckdb','pandas','numpy','torch','jax','keras','llm','gpt','bert','diffusion','stable','genai','rag',
    'ml','ai','web','net','site','link','feed','live','text','dm','tag','heart','save','view','play','pause','stop',
    'skip','search','find','open','close','edit','delete','add','hot','cold','fast','slow','good','bad','nice','cool',
    'fun','sad','happy','mad','tired','bored','busy','free','easy','hard','simple','clean','fresh','sweet','sour',
    'spicy','loud','quiet','bright','dark','light','heavy','soft','wet','dry','warm','young','rich','poor','high',
    'low','long','short','wide','deep','full','empty','true','false','yes','no','ok','fine','great','best','worst',
    'first','last','next','top','bottom','left','right','center','front','back','edge','line','point','icon','image',
    'photo','pic','video','audio','sound','music','song','beat','voice','talk','speak','say','tell','ask','answer',
    'question','reply','comment','status','broadcast','podcast','radio','tv','netflix','youtube','messenger','webrtc',
    'p2p','mesh','server','client','host','backup','restore','upgrade','install','uninstall','download','upload',
    'cookie','session','signup','signin','auth','secret','password','pass','pin','encrypt','decrypt','hash','sign',
    'verify','cert','proxy','firewall','router','switch','modem','display','screen','touch','mouse','trackpad',
    'keyboard','type','input','output','file','folder','dir','path','url','page','tab','window','dialog','popup',
    'menu','button','avatar','pdf','zip','tar','exe','app','bin','dat','tmp','temp','src','build','dist','lib','test',
    'docs','readme','license','todo','fixme','hack','wip','done','ship','ci','cd','dev','prod','stage','local',
    'remote','origin','main','master','develop','feature','bugfix','hotfix','tag','commit','rebase','cherry','pick',
    'stash','reset','revert','amend','squash','draft','pr','mr','issue','epic','story','task','ticket','sprint',
    'backlog','roadmap','milestone','deadline','eta','asap','oc','tl','dr','w','l','tax','ohio','chad','doomer',
    'zoomer','boomer','millennial','sksksk',
]
conv = sorted(set(w for w in conv_raw if test_good(w)))
print(f"  conv: {len(conv)}")

wn = []
for fn in ("wordnet/wordnet_nouns_filtered.txt", "wordnet/wordnet_verbs_filtered.txt", "wordnet/wordnet_adjectives_filtered.txt"):
    p = src_path(fn)
    if p:
        with open(p, encoding="utf-8", errors="ignore") as f:
            for line in f:
                w = line.strip().lower()
                if test_good(w):
                    wn.append(w)
wn = sorted(set(wn))
print(f"  wordnet: {len(wn)}")

nor = []
p = src_path("norvig/norvig_clean.txt")
if p:
    with open(p, encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip().lower()
            if w:
                nor.append(w)
    print(f"  norvig (pre-cleaned): {len(nor)}")
else:
    # Fall back to the unfiltered Norvig list and apply the same quality filter.
    p = src_path("norvig/norvig-words-filtered.txt")
    if p:
        with open(p, encoding="utf-8", errors="ignore") as f:
            for line in f:
                w = line.strip().lower()
                if test_good(w):
                    nor.append(w)
        nor = sorted(set(nor))
        print(f"  norvig (filtered fallback): {len(nor)}")
    else:
        print("  norvig source not found, skipping")

# Combine
cands = sorted(set(kag + foods + conv + wn + nor))
print(f"Candidates after filters (pre-plural): {len(cands)}")

if len(cands) < REQUIRED:
    print(f"WARNING: only {len(cands)} candidates available (need {REQUIRED})")

# Plural removal
to_remove = set()
for w in cands:
    if w.endswith("s") and len(w) > 3:
        r = w[:-1]
        if r in cands:
            to_remove.add(w)
    if w.endswith("es") and len(w) > 3:
        r = w[:-2]
        if r in cands:
            to_remove.add(w)
    if w.endswith("ies") and len(w) > 4:
        r = w[:-3] + "y"
        if r in cands:
            to_remove.add(w)
    if w.endswith("ves") and len(w) > 4:
        r1 = w[:-3] + "f"
        r2 = w[:-3] + "fe"
        if (r1 in cands) or (r2 in cands):
            to_remove.add(w)

irreg = {
    "men": "man", "women": "woman", "children": "child",
    "mice": "mouse", "lice": "louse", "geese": "goose",
    "teeth": "tooth", "feet": "foot", "people": "person", "oxen": "ox"
}
for pl, sg in irreg.items():
    if sg in cands and pl in cands:
        to_remove.add(pl)

# Additional inflection stripping: verbs (-ed, -ing) and adjectives/adverbs (-er, -est, -ly)
# Prefer the base form when it exists in the pool.
# Handles common patterns including e-drop (rewire/rewired/rewiring, wire/wired/wiring).
inflected_removed = 0
for w in list(cands):
    if w in to_remove:
        continue
    base = None
    if w.endswith("ed") and len(w) > 4:
        b = w[:-2]
        for cand in (b, w[:-1], b[:-1] if len(b) > 1 and b[-1] == b[-2] else None):
            if cand and cand in cands:
                base = cand
                break
    elif w.endswith("ing") and len(w) > 5:
        b = w[:-3]
        for cand in (b, b + "e", b[:-1] if len(b) > 1 and b[-1] == b[-2] else None):
            if cand and cand in cands:
                base = cand
                break
    elif w.endswith("er") and len(w) > 4:
        b = w[:-2]
        for cand in (b, (b[:-1] + "y") if b.endswith("i") and len(b) > 1 else None,
                     b[:-1] if len(b) > 1 and b[-1] == b[-2] else None):
            if cand and cand in cands:
                base = cand
                break
    elif w.endswith("est") and len(w) > 5:
        b = w[:-3]
        for cand in (b, (b[:-1] + "y") if b.endswith("i") and len(b) > 1 else None,
                     b[:-1] if len(b) > 1 and b[-1] == b[-2] else None):
            if cand and cand in cands:
                base = cand
                break
    elif w.endswith("ly") and len(w) > 4:
        b = w[:-2]
        for cand in (b, (b[:-1] + "y") if b.endswith("i") and len(b) > 1 else None):
            if cand and cand in cands:
                base = cand
                break

    if base:
        to_remove.add(w)
        inflected_removed += 1

final = [w for w in cands if w not in to_remove]
final.sort()
print(f"After singular + inflection removal (removed {inflected_removed} inflected forms): {len(final)}")

# Priority block: foods + conv
priority = sorted(set(foods + conv))
rest = [w for w in final if w not in priority]

lst = priority[:]
need = REQUIRED - len(lst)
if need > 0:
    lst.extend(rest[:need])
lst = lst[:REQUIRED]

# Final safety pass on the selected list
to_remove2 = set()
lset = set(lst)
for w in lst:
    if w.endswith("s") and len(w) > 3:
        r = w[:-1]
        if r in lset:
            to_remove2.add(w)
    if w.endswith("es") and len(w) > 3:
        r = w[:-2]
        if r in lset:
            to_remove2.add(w)
    if w.endswith("ies") and len(w) > 4:
        r = w[:-3] + "y"
        if r in lset:
            to_remove2.add(w)
    if w.endswith("ves") and len(w) > 4:
        r1 = w[:-3] + "f"
        r2 = w[:-3] + "fe"
        if (r1 in lset) or (r2 in lset):
            to_remove2.add(w)
for pl, sg in irreg.items():
    if sg in lset and pl in lset:
        to_remove2.add(pl)

lst = [w for w in lst if w not in to_remove2][:REQUIRED]

# If still short after safety pass, fill more from the remaining clean pool
if len(lst) < REQUIRED:
    already = set(lst)
    more = [w for w in final if w not in already and w not in to_remove2]
    lst.extend(more[:REQUIRED - len(lst)])

# Do NOT sort the whole list — priority block must stay at the front.
# (priority was already sorted internally, rest came from sorted final)

print(f"Final count: {len(lst)}")

# Write to a distinct rebuild file. We deliberately do NOT overwrite the committed
# curated-by-chris-words.txt: that list was further hand-curated after generation, so this
# script reproduces the *method*, not the exact bytes. Diff the two to review drift.
out1 = BASE / "curated-rebuilt-64434.txt"
with open(out1, "w", encoding="utf-8") as f:
    for w in lst:
        f.write(w + "\n")

print(f"Written {out1.name}")
print("(Committed source of truth is curated-by-chris-words.txt; compare with `diff` to review drift.)")

# Validation output
print("=== First 20 (priority foods/conv should be first) ===")
for w in lst[:20]:
    print(w)

print("=== Last 5 ===")
for w in lst[-5:]:
    print(w)

print("=== Checking for remaining s/p pairs ===")
pairs = []
fset = set(lst)
for w in lst:
    if w.endswith("s") and len(w) > 3:
        b = w[:-1]
        if b in fset:
            pairs.append(f"{b}/{w}")
    if w.endswith("es") and len(w) > 3:
        b = w[:-2]
        if b in fset:
            pairs.append(f"{b}/{w}")
    if w.endswith("ies") and len(w) > 4:
        b = w[:-3] + "y"
        if b in fset:
            pairs.append(f"{b}/{w}")
    if w.endswith("ves") and len(w) > 4:
        b1 = w[:-3] + "f"
        b2 = w[:-3] + "fe"
        if b1 in fset or b2 in fset:
            pairs.append(w)
for pl, sg in irreg.items():
    if sg in fset and pl in fset:
        pairs.append(f"{sg}/{pl}")
pairs = sorted(set(pairs))
print(f"Plural/singular pairs: {len(pairs)}")
if pairs:
    print("Examples:", pairs[:10])
else:
    print("Good: zero pairs")

print("=== Priority samples present ===")
samples = ["adobo", "aioli", "wifi", "meme", "vibe", "rizz", "react", "node", "python"]
print([s for s in samples if s in fset])

print(f"\nDone. Required={REQUIRED}  Got={len(lst)}  Short={max(0, REQUIRED - len(lst))}")
if len(lst) < REQUIRED:
    print("NOTE: Not enough clean words available from current sources after filters.")
