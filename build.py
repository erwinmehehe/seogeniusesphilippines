"""Build the independent SEO Geniuses Philippines static website."""
import argparse, copy, html, json, re, shutil, hashlib
from pathlib import Path
from xml.sax.saxutils import escape
from bs4 import BeautifulSoup
from source.content import SERVICES, GUIDES

ROOT=Path(__file__).resolve().parent
BRAND='SEO Geniuses Philippines'
DOMAIN='https://seogeniusesphilippines.com'
INBOX='info@seooutsourcingphilippines.com'
CALL='https://calendly.com/discovery-call-with-erwin'
parser=argparse.ArgumentParser()
parser.add_argument('--base-url',default=DOMAIN,help='Deployment origin including any project path')
parser.add_argument('--indexable',action='store_true',help='Only use for the canonical production domain')
args=parser.parse_args()
if args.indexable and args.base_url.rstrip('/')!=DOMAIN:
    parser.error('Only the canonical domain may be indexable')
BASE=args.base_url.rstrip('/')
OUT=ROOT/'dist'
OUT.mkdir(exist_ok=True)
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
shutil.copytree(ROOT/'brand',OUT/'brand',dirs_exist_ok=True)

def link(path): return '/'+path.strip('/')+'/' if path else '/'
def cta(label='Get a Quote',href='/contact/',outline=False):
    return f'<a class="btn{" outline" if outline else ""}" href="{html.escape(href)}">{label}</a>'
def opening(heading,intro):
    return f'<section class="page-hero"><div class="container"><h1>{heading}</h1><p>{intro}</p></div></section>'
def editorial(sections):
    return ''.join(f'<h2>{h}</h2><p>{p}</p>' for h,p in sections)
def close(heading='Put your next SEO project in writing.'):
    return '<section class="cta-band"><div class="container"><h2>'+heading+'</h2><p>Share the URL, the audience you want to reach and what needs to change. We will prepare a proposed scope.</p>'+cta()+'</div></section>'

nav='<a href="/services/">Services</a><a href="/results/">Portfolio</a><a href="/pricing/">Pricing</a><a href="/about/">About</a>'
brand='<a class="brand" aria-label="SEO Geniuses Philippines home" href="/"><img class="brand-symbol" src="/brand/mark.svg" width="42" height="42" alt=""/><span><span class="brand-name">SEO Geniuses</span><span class="brand-sub">Philippines</span></span></a>'
header=f'<a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="container header-inner">{brand}<nav class="main-nav" aria-label="Main navigation">{nav}</nav><div class="shell-actions">{cta()}<a class="btn outline" href="{CALL}" target="_blank" rel="noopener noreferrer">Book a call</a></div><button type="button" class="menu-toggle" data-menu-button aria-controls="mobile-navigation" aria-expanded="false" aria-label="Toggle navigation">Menu</button></div><nav class="mobile-nav" id="mobile-navigation" data-mobile-nav aria-label="Mobile navigation" hidden>{nav}{cta()}<a href="{CALL}" target="_blank" rel="noopener noreferrer">Book a discovery call</a></nav></header>'
footer=f'<footer class="site-footer"><div class="container"><div class="footer-grid"><div>{brand}<p>Search strategy, website optimisation and SEO implementation from the Philippines.</p><a class="contact-email" href="mailto:{INBOX}">{INBOX}</a></div><div><h3>Services</h3><a href="/services/technical-seo/">Technical SEO</a><a href="/services/local-seo/">Local SEO</a><a href="/services/ecommerce-seo/">Ecommerce SEO</a><a href="/services/white-label-seo/">White-label SEO</a></div><div><h3>Company</h3><a href="/about/">About</a><a href="/results/">Portfolio</a><a href="/pricing/">Pricing</a><a href="/contact/">Get a Quote</a></div><div><h3>Resources</h3><a href="/blog/">SEO guides</a><a href="/privacy-policy/">Privacy policy</a><a href="/terms-of-service/">Terms of service</a><a href="/cookie-policy/">Cookie policy</a></div></div><div class="footer-bottom"><span>© 2026 {BRAND}.</span></div></div></footer><a class="shell-fixed-call" href="{CALL}" target="_blank" rel="noopener noreferrer">Book a Discovery Call</a>'
pages={}

def page(path,title,description,body,kind='WebPage'):
    canonical=DOMAIN+link(path)
    graph=[{'@type':'Organization','@id':DOMAIN+'/#organization','name':BRAND,'url':DOMAIN+'/', 'logo':DOMAIN+'/brand/logo-dark.svg'},
           {'@type':'WebSite','@id':DOMAIN+'/#website','name':BRAND,'url':DOMAIN+'/'},
           {'@type':kind,'@id':canonical+'#page','name':title,'description':description,'url':canonical,'inLanguage':'en','publisher':{'@id':DOMAIN+'/#organization'}}]
    if kind=='Service':graph[-1].update(provider={'@id':DOMAIN+'/#organization'})
    robots='index,follow,max-image-preview:large' if args.indexable and path!='quote-request-sent' else 'noindex,follow'
    fulltitle=title if BRAND in title else title+' | '+BRAND
    markup=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>{html.escape(fulltitle)}</title><meta name="description" content="{html.escape(description)}"/><meta name="robots" content="{robots}"/><meta name="theme-color" content="#101518"/><link rel="canonical" href="{canonical}"/><meta property="og:type" content="website"/><meta property="og:site_name" content="{BRAND}"/><meta property="og:title" content="{html.escape(fulltitle)}"/><meta property="og:description" content="{html.escape(description)}"/><meta property="og:url" content="{canonical}"/><meta property="og:image" content="{DOMAIN}/brand/social-card.png"/><meta name="twitter:card" content="summary_large_image"/><link rel="icon" href="/brand/mark.svg" type="image/svg+xml"/><link rel="icon" href="/brand/favicon.ico" sizes="any"/><link rel="apple-touch-icon" href="/brand/apple-touch-icon.png"/><link rel="stylesheet" href="/assets/site.css"/><link rel="stylesheet" href="/assets/page-shell.css"/><link rel="stylesheet" href="/assets/inner-pages.css"/><link rel="stylesheet" href="/assets/brand.css"/><script type="application/ld+json">{json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False)}</script><script defer src="/assets/site.js"></script></head><body>{header}{body}{footer}</body></html>'''
    # Rewrite only actual local URL attributes, never embedded data URLs or schemas.
    markup=re.sub(r'((?:href|src|action)=["\x27])/(?!/)',lambda m:m[1]+BASE+'/',markup)
    soup=BeautifulSoup(markup,'html.parser')
    if path in ('','results'):
        css=soup.new_tag('link',rel='stylesheet',href=BASE+'/assets/home.css')
        soup.head.append(css)
    for a in soup.select('nav a[href]'):
        if a['href']==BASE+link(path):a['aria-current']='page'
    # New styles and behaviour must not depend on an older browser/CDN cache.
    for resource in soup.select('link[rel="stylesheet"][href],script[src]'):
        attr='href' if resource.name=='link' else 'src'
        prefix=BASE+'/assets/'
        if resource[attr].startswith(prefix):
            asset=ROOT/'assets'/resource[attr][len(prefix):].split('?')[0]
            if asset.is_file():
                version=hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
                resource[attr]=resource[attr].split('?')[0]+'?v='+version
    out=OUT/path/'index.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(str(soup)+'\n',encoding='utf-8')
    pages[path]=(title,description)

service_rows=''.join(f'<a class="service-tile" href="/services/{slug}/"><h2>{data["heading"]}</h2><p>{data["summary"]}</p></a>' for slug,data in SERVICES.items())
PROJECTS=json.loads((ROOT/'source/portfolio.json').read_text(encoding='utf-8'))
def portfolio_cards(projects):
    cards=[]
    for project in projects:
        logo=(f'<img src="{html.escape(project["logo"])}" alt="" loading="lazy" width="160" height="64"/>' if project['logo'] else '')
        rows=''.join('<tr><td>'+html.escape(query)+'</td><td>'+html.escape(rank)+'</td></tr>' for query,rank in project['keywords'])
        cards.append('<article class="genius-project"><div class="genius-project-logo">'+logo+'</div><h3>'+html.escape(project['name'])+'</h3><p>'+html.escape(project['market'])+'</p><details><summary>Recorded search positions</summary><table><caption class="sr-only">'+html.escape(project['name'])+' search positions</caption><thead><tr><th>Query</th><th>Position</th></tr></thead><tbody>'+rows+'</tbody></table></details></article>')
    return '<div class="genius-project-grid">'+''.join(cards)+'</div>'
portfolio_intro='<p class="portfolio-context">Selected websites from our SEO work across Australia and the United States. The figures below are recorded keyword positions, not traffic or revenue claims.</p>'
portfolio_note='<p class="portfolio-date">Search positions captured on 9 November 2026, using the relevant Australian or US Google results. Rankings are historical observations and can change.</p>'
home_portfolio='<section class="studio-wrap studio-portfolio" id="portfolio"><div class="studio-heading"><h2>Websites we’ve<br/>worked on.</h2><div>'+portfolio_intro+'<a href="/results/">Explore the portfolio</a></div></div>'+portfolio_cards(PROJECTS)+portfolio_note+'</section>'
home=(ROOT/'source/home.html').read_text(encoding='utf-8').replace('{{HERO}}',(ROOT/'source/hero.html').read_text(encoding='utf-8')).replace('{{PORTFOLIO}}',home_portfolio).replace('{{SERVICES}}',service_rows).replace('{{CLOSE}}',close())
page('', 'SEO Philippines | SEO Geniuses Philippines','SEO Philippines: search strategy, technical diagnosis, content planning and website implementation. Explore SEO expertise from the Philippines and request a quote.',home)
page('services','SEO Services Philippines','Explore technical, on-page, local and ecommerce SEO, keyword research, content and reporting from the Philippines.','<main id="main" class="inner-design">'+opening('SEO services','Choose the work your website needs, from a focused technical project to ongoing content and search support.')+'<section class="container service-catalog">'+service_rows+'</section>'+close()+'</main>')
for slug,data in SERVICES.items():
    related=''.join(f'<p><a href="/services/{x}/">{SERVICES[x]["heading"]}</a></p>' for x in data['related'])
    body='<main id="main">'+opening(data['heading'],data['intro'])+'<section class="section"><div class="container editorial-layout"><article class="article">'+editorial(data['sections'])+'</article><aside class="sidebar"><div class="side-box"><h3>Discuss this service</h3><p>Send your website and the work you need covered.</p>'+cta(href='/contact/?service='+slug)+'</div><div class="side-box"><h3>Related services</h3>'+related+'</div></aside></div></section>'+close()+'</main>'
    page('services/'+slug,data['title'],data['intro'],body,'Service')

about=[('SEO work you can review','SEO Geniuses Philippines provides technical SEO, on-page improvements, local search, ecommerce SEO, content and reporting. Work is available as a defined project or ongoing support, with the scope agreed for your website.'),('A proposal before implementation','We ask about your services, customers and website before preparing a quote. The proposal identifies the work included, the information and access needed, and tasks that require your developer or approval.'),('Your business keeps control','You retain ownership of your website and business accounts. Access should be granted through named users with suitable permissions. Client information and factual claims need your review before publication.'),('Research follows your audience','A provider’s location does not define your customer base. Project research uses the market and language agreed in the brief. Technical recommendations respond to the website platform and the pages involved.'),('A practical first step','Send your website and the issue you want addressed. If the requirement is a single technical fix or content project, the quote can reflect that rather than assuming you need a monthly plan.')]
page('about','About SEO Geniuses Philippines','Learn how SEO Geniuses Philippines scopes, delivers and reports on SEO projects for businesses.','<main id="main">'+opening('About SEO Geniuses Philippines','Technical SEO, content and local search support, with the work agreed before it begins.')+'<section class="section"><article class="container policy-copy">'+editorial(about)+'</article></section>'+close()+'</main>')

# Original copy for this brand; existing price amounts are retained.
page('pricing','SEO Pricing Philippines','Review monthly SEO starting fees and the questions a project proposal should answer. USD pricing for defined research, implementation and reporting work.',(ROOT/'source/pricing-content.html').read_text(encoding='utf-8'))
page('results','SEO Project Portfolio | SEO Geniuses Philippines','Browse websites from our SEO portfolio, with recorded search queries and positions for Australian and US projects.', '<main id="main" class="portfolio-page">'+opening('SEO project portfolio', 'Explore the websites, markets and search terms in our recorded project work.')+'<section class="container">'+portfolio_intro+portfolio_cards(PROJECTS)+portfolio_note+'</section>'+close()+'</main>')

contact=BeautifulSoup((ROOT/'source/contact.html').read_text(encoding='utf-8'),'html.parser').main
contact.h1.string='Get a quote for your website.'
contact.select_one('.quote-intro > p').string='Tell us what you sell, where your customers are and which SEO tasks you need help with.'
form=contact.select_one('form')
form['action']='https://formsubmit.co/'+INBOX
form.attrs.pop('novalidate',None)
audience=form.select_one('[name="audience"]')
for option in audience.select('option'):
    option.attrs.pop('selected',None)
    if option.get('value')=='business':option['selected']=''
service=form.select_one('[name="service"]')
if service:
    service.clear()
    choices=[('', 'Not sure yet')]+[(slug,data['heading']) for slug,data in SERVICES.items()]
    for value,label in choices:
        option=BeautifulSoup('<option></option>','html.parser').option
        option['value']=value;option.string=label;service.append(option)
for field in form.select('[disabled]'):field.attrs.pop('disabled',None)
honeypot=form.select_one('[name="phone_confirm"]')
if honeypot:honeypot['name']='_honey'
for name,value in [('_subject','SEO Geniuses Philippines — quote request'),('_template','table'),('_next',BASE+'/quote-request-sent/')]:
    field=BeautifulSoup('<input type="hidden"/>','html.parser').input
    field['name']=name;field['value']=value;form.append(field)
note=BeautifulSoup(f'<p class="small">Enquiries are processed by <a href="https://formsubmit.co/privacy.pdf" target="_blank" rel="noopener noreferrer">FormSubmit</a> and emailed to {INBOX}. Do not include passwords or confidential account information.</p>','html.parser').p
form.append(note)
page('contact','Contact SEO Geniuses Philippines','Request a quote for SEO services in the Philippines. Share your website, target market and the work you need.',str(contact))
page('quote-request-sent','Quote request submitted','Your quote request has been submitted.','<main id="main">'+opening('Thank you for your enquiry.','Your request has been submitted. We will review the details and reply by email.')+'<section class="container genius-section">'+cta('Back to home','/')+'</section></main>')

guide_rows=''.join(f'<article class="post-card"><h3><a href="/blog/{slug}/">{g["title"]}</a></h3><p>{g["intro"]}</p></article>' for slug,g in GUIDES.items())
page('blog','SEO Planning and Implementation Guides','Practical guides to choosing SEO services, reviewing proposals and improving local search information.','<main id="main">'+opening('SEO guides','Practical checks for business owners reviewing their website and SEO options.')+'<section class="section"><div class="container guide-list">'+guide_rows+'</div></section></main>')
for slug,g in GUIDES.items():
    page('blog/'+slug,g['title'],g['intro'],'<main id="main">'+opening(g['title'],g['intro'])+'<section class="section"><article class="container policy-copy">'+editorial(g['sections'])+'<p>Read the <a href="https://developers.google.com/search/docs/fundamentals/seo-starter-guide">Google Search Central SEO Starter Guide</a> for further guidance.</p></article></section>'+close()+'</main>')

policies={
'privacy-policy':('Privacy policy','How website enquiries are handled.',[
('Information you provide','We receive the contact and project details you enter in the enquiry form. A website address and optional business information help us understand the assignment. Keep account credentials and sensitive personal records out of this form.'),
('How enquiry information is used',f'Information is used to respond to your enquiry and prepare a proposal. Enquiries are delivered to {INBOX}. Sending a request does not subscribe you to marketing.'),
('External services','GitHub Pages hosts the website. FormSubmit processes quote requests and emails their contents. Its spam checks may use CAPTCHA. Calendly handles information you provide when booking a call. Their privacy policies apply to those services.'),
('Analytics','This website does not currently install an analytics or advertising tracker. Hosting and form providers may process technical request information to operate their services and prevent abuse.'),
('Questions and requests',f'Contact <a href="mailto:{INBOX}">{INBOX}</a> with privacy questions or a request concerning enquiry information you provided.')]),
'terms-of-service':('Terms of service','Website information and service enquiries.',[
('Service agreements','Submitting an enquiry does not create a service agreement. A written proposal confirms the scope, fees, payment arrangements, responsibilities, review process and cancellation terms before work begins.'),
('Published prices','Monthly prices are starting prices in US dollars. The final quote depends on the work agreed. Any external charges must be identified in the agreed fee breakdown.'),
('Search performance','SEO assignments specify the work to be performed. A proposal does not promise a particular search position, traffic count or sales figure. Reports should identify the dates, data sources and assumptions used to interpret changes.'),
('Information and access','Provide only information you are entitled to share. Website and account access are arranged separately using appropriate permissions. Do not send credentials through the enquiry form.'),
('External services','Links to external websites and booking services are governed by their own terms. Website information may be updated as services or platform requirements change.')]),
'cookie-policy':('Cookie policy','Cookies and external services.',[
('This website','The static website does not install advertising or analytics cookies. Your browser and hosting provider may process technical information needed to load pages.'),
('Quote requests','Submitting the quote form opens FormSubmit, which may use cookies and CAPTCHA for spam protection. Read its privacy policy before submitting sensitive information.'),
('Bookings','Discovery-call links open Calendly. Cookies and information supplied there are covered by Calendly’s policies.'),
('Browser controls','Use the privacy controls in your browser to review stored cookies and choose which to allow. Restrictions can interrupt a third-party booking or form submission.')])}
for slug,(title,intro,sections) in policies.items():
    page(slug,title,intro,'<main id="main">'+opening(title,intro)+'<section class="section"><article class="container policy-copy">'+editorial(sections)+'</article></section></main>')

error=OUT/'404.html'
error_soup=BeautifulSoup((OUT/'quote-request-sent/index.html').read_text(encoding='utf-8'),'html.parser')
error_soup.title.string='Page not found | '+BRAND
error_soup.h1.string='Page not found.'
error_soup.select_one('main p').string='The page may have moved. Use the navigation or return to the homepage.'
error_soup.select_one('link[rel="canonical"]').decompose()
error_soup.select_one('meta[name="robots"]')['content']='noindex,nofollow'
for node in error_soup.select('script[type="application/ld+json"],meta[property^="og:"]'):node.decompose()
error.write_text(str(error_soup),encoding='utf-8')
(OUT/'.nojekyll').touch()
if args.indexable:
    (OUT/'CNAME').write_text('seogeniusesphilippines.com\n',encoding='utf-8')
    robots='User-agent: *\nAllow: /\nSitemap: '+DOMAIN+'/sitemap.xml\n'
else:
    (OUT/'CNAME').unlink(missing_ok=True)
    robots='User-agent: *\nDisallow: /\n'
(OUT/'robots.txt').write_text(robots,encoding='utf-8')
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape(DOMAIN+link(path))+'</loc></url>' for path in sorted(pages) if path!='quote-request-sent')+'</urlset>',encoding='utf-8')
print(f'Built {len(pages)} pages for {BASE}. Indexable: {args.indexable}.')
