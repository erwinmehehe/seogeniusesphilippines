"""Verify every published HTML page forwards only to the approved destination."""
from pathlib import Path
from bs4 import BeautifulSoup

OUT = Path(__file__).resolve().parent / 'dist'
TARGET = 'https://seooutsourcingphilippines.com/'
pages = list(OUT.rglob('*.html'))
assert len(pages) >= 25 and (OUT / '404.html').is_file()
for page in pages:
    soup = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
    assert soup.select_one('meta[http-equiv="refresh"]')['content'] == '0;url=' + TARGET, page
    assert soup.select_one('link[rel="canonical"]')['href'] == TARGET, page
    assert soup.select_one('meta[name="robots"]')['content'] == 'noindex,follow', page
    assert soup.a['href'] == TARGET and not soup.select('form,.genius-project'), page
    assert 'window.location.replace("' + TARGET + '")' in soup.script.string, page
assert (OUT / 'CNAME').read_text().strip() == 'seogeniusesphilippines.com'
assert not (OUT / 'sitemap.xml').exists()
print(f'PASS: all {len(pages)} HTML pages redirect to the fixed HTTPS destination.')
