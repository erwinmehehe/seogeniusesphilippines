"""Replace built public HTML with secure, fixed-destination browser redirects.

The editable website source remains intact. GitHub Pages provides TLS and its
HTTP-to-HTTPS redirect; static Pages cannot issue a cross-domain HTTP 301.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
TARGET = 'https://seooutsourcingphilippines.com/'
pages = list(OUT.rglob('*.html'))
if len(pages) < 25:
    raise SystemExit('Build and validate the preserved website first.')
markup = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="{TARGET}">
<meta http-equiv="refresh" content="0;url={TARGET}">
<title>SEO Outsourcing Philippines</title>
<script>window.location.replace({json.dumps(TARGET)});</script>
</head><body><p>Continue to <a href="{TARGET}">SEO Outsourcing Philippines</a>.</p></body></html>
'''
for page in pages:
    page.write_text(markup, encoding='utf-8')
(OUT / 'CNAME').write_text('seogeniusesphilippines.com\n', encoding='utf-8')
(OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\n', encoding='utf-8')
(OUT / 'sitemap.xml').unlink(missing_ok=True)
print(f'Prepared {len(pages)} fixed-destination redirect pages, including 404 fallback.')
