"""Validate the built pages, native form, original copy and price amounts."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
import json,re
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist'
pages=list(OUT.rglob('index.html'));errors=[];titles=[];descriptions=[]
home=BeautifulSoup((OUT/'index.html').read_text(encoding='utf-8'),'html.parser')
assert 'SEO Philippines' in home.title.get_text()
assert home.h1.get_text(' ',strip=True)=='Find the problem. Fix the page.'
assert not home.select('svg.chart,.chart,.dash,.hero-agenda')
assert 'Illustrative' not in home.main.get_text(' ',strip=True)
assert home.select_one('.studio-hero-actions a[href$="/contact/"]')
assert home.select_one('.studio-hero-actions a[href="https://calendly.com/discovery-call-with-erwin"]')
assert 'for philippine businesses' not in home.get_text(' ',strip=True).lower()
base=urlsplit(home.select_one('.brand')['href']);prefix=base.path.rstrip('/')
for file in pages:
    soup=BeautifulSoup(file.read_text(encoding='utf-8'),'html.parser')
    title=soup.title.get_text();titles.append(title)
    desc=soup.select_one('meta[name="description"]')['content'];descriptions.append(desc)
    if len(soup.select('h1'))!=1:errors.append(f'{file}: H1 count')
    if len(soup.select('link[rel="canonical"]'))!=1:errors.append(f'{file}: canonical count')
    if not soup.select_one('link[rel="canonical"]')['href'].startswith('https://seogeniusesphilippines.com/'):errors.append(f'{file}: wrong canonical')
    for s in soup.select('script[type="application/ld+json"]'):json.loads(s.string)
    for node in soup.select('[href],[src]'):
        url=node.get('href',node.get('src',''));parts=urlsplit(url)
        if parts.scheme in ['data','mailto','tel'] or url.startswith('#'):continue
        if parts.netloc and parts.netloc!=base.netloc:continue
        path=unquote(parts.path)
        if prefix and path.startswith(prefix):path=path[len(prefix):]
        target=OUT/path.lstrip('/')
        if path and not (target.is_file() or (target/'index.html').is_file()):errors.append(f'{file.relative_to(OUT)} missing target {url[:140]}')
    for cta in soup.select('a.btn,button'):
        if re.search('[→↗➜➔]',cta.get_text()):errors.append(f'{file}: CTA arrow')
    if soup.select('.eyebrow,.kicker,.overline'):errors.append(f'{file}: heading label')
if len(titles)!=len(set(titles)):errors.append('Duplicate titles')
if len(descriptions)!=len(set(descriptions)):errors.append('Duplicate descriptions')
if len(pages)!=25:errors.append(f'Expected 25 pages; got {len(pages)}')
contact=BeautifulSoup((OUT/'contact/index.html').read_text(encoding='utf-8'),'html.parser')
form=contact.select_one('#contact-form')
assert form['action']=='https://formsubmit.co/info@seooutsourcingphilippines.com'
assert form['method']=='post' and not form.has_attr('novalidate')
assert not form.select('[disabled]') and form.select_one('[name="_next"]')
assert form.select_one('[name="email"][required]') and form.select_one('[name="consent"][required]')
assert form.select_one('[name="_honey"]')
pricing=BeautifulSoup((OUT/'pricing/index.html').read_text(encoding='utf-8'),'html.parser')
assert [n.get_text(' ',strip=True).split()[0] for n in pricing.select('.price')]==['$700','$1,000','$1,500']
assert not BeautifulSoup((OUT/'results/index.html').read_text(encoding='utf-8'),'html.parser').select('.work-card')
assert 'markd' not in (OUT/'results/index.html').read_text(encoding='utf-8').lower()
assert 'G-Y6B0JEJRZ4' not in (OUT/'index.html').read_text(encoding='utf-8')
if errors:raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} pages, unique metadata, internal links/assets, structured data, quote-form configuration and unchanged price amounts.')
