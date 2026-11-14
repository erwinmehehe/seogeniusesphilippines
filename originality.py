"""Check substantial text blocks against a frozen SEO Outsourcing reference.

This compares main-content blocks of eight or more words and sentences of ten
or more words, ignoring punctuation and case. Standard short labels, service
names and factual prices are not treated as copied prose. This is a bounded
cross-site regression check, not an internet-wide originality guarantee.
"""
import argparse, hashlib, json, re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
SELECTOR='main p,main li,main label,main td,main th,main h2,main h3'
def norm(text):return ' '.join(re.findall(r'[a-z0-9]+',text.lower()))
def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def passages(folder):
    for file in folder.rglob('index.html'):
        soup=BeautifulSoup(file.read_text(encoding='utf-8'),'html.parser')
        for node in soup.select(SELECTOR):
            text=node.get_text(' ',strip=True)
            clean=norm(text)
            if len(clean.split())>=8:yield file,'block',clean
            for sentence in re.split(r'(?<=[.!?])\s+',text):
                clean=norm(sentence)
                if len(clean.split())>=10:yield file,'sentence',clean

parser=argparse.ArgumentParser()
parser.add_argument('--reference',type=Path,help='Refresh reference fingerprints from the existing site checkout')
args=parser.parse_args()
snapshot=ROOT/'quality/seo-outsourcing-copy-reference.json'
if args.reference:
    if not (args.reference/'index.html').is_file():parser.error('Reference must be the existing standalone site directory')
    fingerprints={kind:set() for kind in ['block','sentence']}
    for _,kind,text in passages(args.reference):fingerprints[kind].add(digest(text))
    snapshot.parent.mkdir(exist_ok=True)
    snapshot.write_text(json.dumps({'reference':'seooutsourcingph standalone site, 5833b69','pages':len(list(args.reference.rglob('index.html'))),'fingerprints':{k:sorted(v) for k,v in fingerprints.items()}},indent=2)+'\n',encoding='utf-8')
    print('Recorded reference fingerprints; no reference copy is republished.')
reference=json.loads(snapshot.read_text(encoding='utf-8'))
known={k:set(v) for k,v in reference['fingerprints'].items()}
matches=[]
for file,kind,text in passages(ROOT/'dist'):
    if digest(text) in known[kind]:matches.append(f'{file.relative_to(ROOT/"dist")}: copied {kind}: {text[:160]}')
if matches:raise SystemExit('\n'.join(sorted(set(matches))))
print(f'PASS: no matching substantial body blocks or sentences against {reference["pages"]} SEO Outsourcing Philippines pages.')
