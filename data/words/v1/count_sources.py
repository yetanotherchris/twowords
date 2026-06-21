#!/usr/bin/env python3
import re
import csv
import sys

STOPS = set("""the and for are but not you all can had her was one our out day get has him his how man new now old see two way who boy end did its let put say she too use dad mom off own may try ask big per act set yet far few that with this from which have were they will their been other there would more such when any these time than some what about state only into also them said under first made should after shall your most could then over each year work where years between those same many through upon must well very general before used because being part like united people during public section number even make court case system much three both water law life company service good without order great american while however york long high national right does city just here world another data business given know program little since present every house men report less back place total large take down small county second control might research office last point form board still children interest federal study area action value fact line found power states within school against""".split())

CITIES = set()
for line in open('cities/uk_cities.txt'):
    t = line.lower().strip()
    if t: CITIES.add(t)
with open('cities/world-cities.csv', encoding='utf-8', errors='ignore') as f:
    rdr = csv.reader(f)
    next(rdr, None)
    for row in rdr:
        if row and row[0]:
            n = row[0].lower().strip()
            if 3 <= len(n) <= 8 and n.isalpha():
                CITIES.add(n)

PROFS = set(w.lower().strip() for w in open('profanity.txt') if 3 <= len(w.strip()) <= 8)

PS1 = open('build-final.ps1', encoding='utf-8').read()

ACROS = set()
m = re.search(r'\$acroList = @\((.*?)\)\s*\$acro =', PS1, re.DOTALL)
if m:
    for it in re.findall(r"'([^']+)'", m.group(1)):
        t = it.lower().strip()
        if 3 <= len(t) <= 8:
            ACROS.add(t)
print(f'acros 3-8: {len(ACROS)}', file=sys.stderr)

def has_vowel(w):
    return bool(re.search(r'[aeiou]', w))

def good(w):
    if not w or len(w) < 3 or len(w) > 8:
        return False
    if not w.isalpha():
        return False
    if not has_vowel(w):
        return False
    if w in STOPS or w in CITIES or w in PROFS or w in ACROS:
        return False
    return True

kag = [l.strip().lower() for l in open('kaggle/common_clean.txt') if l.strip()]
foods = [l.strip().lower() for l in open('claude/food_dishes_final.txt') if l.strip()]

m2 = re.search(r'\$convRaw = @\((.*?)\)\s*\$conv =', PS1, re.DOTALL)
conv_raw = [x.lower() for x in re.findall(r"'([^']+)'", m2.group(1))] if m2 else []

wn = []
for fn in ['wordnet/wordnet_nouns_filtered.txt', 'wordnet/wordnet_verbs_filtered.txt', 'wordnet/wordnet_adjectives_filtered.txt']:
    wn += [l.strip().lower() for l in open(fn) if l.strip()]

nor = [l.strip().lower() for l in open('norvig/norvig-words-filtered.txt') if l.strip()]

print('=== RAW ===')
print(f'kaggle/common_clean.txt: {len(kag)}')
print(f'claude/food_dishes_final.txt: {len(foods)}')
print(f'conv (from build-final.ps1): {len(conv_raw)}')
print(f'wordnet total: {len(wn)}')
print(f'norvig: {len(nor)}')

def apply(name, src):
    g = [w for w in src if good(w)]
    print(f'{name}: after all basic = {len(g)}')
    return set(g)

sk = apply('kaggle', kag)
sf = apply('food', foods)
sc = apply('conv', conv_raw)
sw = apply('wordnet', wn)
sn = apply('norvig', nor)

print()
c = sk | sf | sc | sw
print(f'UNIQUE (k+f+c+wn) pre-plural: {len(c)}')

to_rm = set()
for w in list(c):
    if w.endswith('s') and len(w) > 3 and w[:-1] in c:
        to_rm.add(w)
    if w.endswith('es') and len(w) > 3 and w[:-2] in c:
        to_rm.add(w)
    if w.endswith('ies') and len(w) > 4 and (w[:-3] + 'y') in c:
        to_rm.add(w)
final = c - to_rm
print(f'AFTER plural-if-singular: {len(final)}')

print()
cn = sk | sf | sc | sw | sn
to_rmn = set()
for w in list(cn):
    if w.endswith('s') and len(w) > 3 and w[:-1] in cn: to_rmn.add(w)
    if w.endswith('es') and len(w) > 3 and w[:-2] in cn: to_rmn.add(w)
    if w.endswith('ies') and len(w) > 4 and (w[:-3]+'y') in cn: to_rmn.add(w)
print(f'WITH norvig after all filters: {len(cn - to_rmn)}')
