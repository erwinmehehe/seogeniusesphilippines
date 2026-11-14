"""Build the independent SEO Geniuses Philippines static website."""
import argparse, copy, html, json, re, shutil
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
def close(heading='Tell us what your website needs.'):
    return '<section class="cta-band"><div class="container"><h2>'+heading+'</h2><p>Send your website, target market and the work you want help with.</p>'+cta()+'</div></section>'

nav='<a href="/services/">Services</a><a href="/results/">Our work</a><a href="/pricing/">Pricing</a><a href="/about/">About</a>'
brand='<a class="brand" aria-label="SEO Geniuses Philippines home" href="/"><img class="brand-symbol" src="/brand/mark.svg" width="42" height="42" alt=""/><span><span class="brand-name">SEO Geniuses</span><span class="brand-sub">Philippines</span></span></a>'
header=f'<a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="container header-inner">{brand}<nav class="main-nav" aria-label="Main navigation">{nav}</nav><div class="shell-actions">{cta()}<a class="btn outline" href="{CALL}" target="_blank" rel="noopener noreferrer">Book a call</a></div><button type="button" class="menu-toggle" data-menu-button aria-controls="mobile-navigation" aria-expanded="false" aria-label="Toggle navigation">Menu</button></div><nav class="mobile-nav" id="mobile-navigation" data-mobile-nav aria-label="Mobile navigation" hidden>{nav}{cta()}<a href="{CALL}" target="_blank" rel="noopener noreferrer">Book a discovery call</a></nav></header>'
footer=f'<footer class="site-footer"><div class="container"><div class="footer-grid"><div>{brand}<p>SEO services for businesses in the Philippines.</p><a class="contact-email" href="mailto:{INBOX}">{INBOX}</a></div><div><h3>Services</h3><a href="/services/technical-seo/">Technical SEO</a><a href="/services/local-seo/">Local SEO</a><a href="/services/ecommerce-seo/">Ecommerce SEO</a><a href="/services/white-label-seo/">White-label SEO</a></div><div><h3>Company</h3><a href="/about/">About</a><a href="/results/">Our work</a><a href="/pricing/">Pricing</a><a href="/contact/">Get a Quote</a></div><div><h3>Resources</h3><a href="/blog/">SEO guides</a><a href="/privacy-policy/">Privacy policy</a><a href="/terms-of-service/">Terms of service</a><a href="/cookie-policy/">Cookie policy</a></div></div><div class="footer-bottom"><span>© 2026 {BRAND}.</span></div></div></footer><a class="shell-fixed-call" href="{CALL}" target="_blank" rel="noopener noreferrer">Book a Discovery Call</a>'
pages={}

def page(path,title,description,body,kind='WebPage'):
    canonical=DOMAIN+link(path)
    graph=[{'@type':'Organization','@id':DOMAIN+'/#organization','name':BRAND,'url':DOMAIN+'/', 'logo':DOMAIN+'/brand/logo-dark.svg'},
           {'@type':'WebSite','@id':DOMAIN+'/#website','name':BRAND,'url':DOMAIN+'/'},
           {'@type':kind,'@id':canonical+'#page','name':title,'description':description,'url':canonical,'inLanguage':'en','publisher':{'@id':DOMAIN+'/#organization'}}]
    if kind=='Service':graph[-1].update(provider={'@id':DOMAIN+'/#organization'},areaServed={'@type':'Country','name':'Philippines'})
    robots='index,follow,max-image-preview:large' if args.indexable and path!='quote-request-sent' else 'noindex,follow'
    fulltitle=title if BRAND in title else title+' | '+BRAND
    markup=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>{html.escape(fulltitle)}</title><meta name="description" content="{html.escape(description)}"/><meta name="robots" content="{robots}"/><meta name="theme-color" content="#101518"/><link rel="canonical" href="{canonical}"/><meta property="og:type" content="website"/><meta property="og:site_name" content="{BRAND}"/><meta property="og:title" content="{html.escape(fulltitle)}"/><meta property="og:description" content="{html.escape(description)}"/><meta property="og:url" content="{canonical}"/><meta property="og:image" content="{DOMAIN}/brand/social-card.png"/><meta name="twitter:card" content="summary_large_image"/><link rel="icon" href="/brand/mark.svg" type="image/svg+xml"/><link rel="icon" href="/brand/favicon.ico" sizes="any"/><link rel="apple-touch-icon" href="/brand/apple-touch-icon.png"/><link rel="stylesheet" href="/assets/site.css"/><link rel="stylesheet" href="/assets/page-shell.css"/><link rel="stylesheet" href="/assets/inner-pages.css"/><link rel="stylesheet" href="/assets/brand.css"/><script type="application/ld+json">{json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False)}</script><script defer src="/assets/site.js"></script></head><body>{header}{body}{footer}</body></html>'''
    # Rewrite only actual local URL attributes, never embedded data URLs or schemas.
    markup=re.sub(r'((?:href|src|action)=["\x27])/(?!/)',lambda m:m[1]+BASE+'/',markup)
    soup=BeautifulSoup(markup,'html.parser')
    for a in soup.select('nav a[href]'):
        if a['href']==BASE+link(path):a['aria-current']='page'
    out=OUT/path/'index.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(str(soup)+'\n',encoding='utf-8')
    pages[path]=(title,description)

service_rows=''.join(f'<a class="service-tile" href="/services/{slug}/"><h2>{data["heading"]}</h2><p>{data["summary"]}</p></a>' for slug,data in SERVICES.items())
home='''<main id="main" class="inner-design"><section class="genius-hero container"><div><h1>SEO services in<br/>the Philippines.</h1><p>Make your services easier to find in search. Get help with the technical issues, pages and content that stand between your website and your customers.</p><div class="btn-row">'''+cta()+cta('Explore our work','/results/',True)+'''</div></div><div class="hero-agenda"><h2>Work on what your website needs.</h2><div><h3>Technical foundations</h3><p>Help search engines find and understand your important pages.</p></div><div><h3>Pages that answer customers</h3><p>Explain your services clearly and connect related information.</p></div><div><h3>Progress you can review</h3><p>See completed work, search performance and the next priorities.</p></div></div></section>
<section class="container genius-intro"><h2>Start with the website you have.</h2><div><p>You may need a technical problem fixed, service pages rewritten or ongoing help with SEO. We review the website and your priorities before proposing the work.</p><p>For Philippine businesses, that can mean local search and Google Business Profile work, clearer service pages or product and category improvements for an online store. The scope follows what you sell and where your customers are.</p></div></section>
<section class="container genius-section"><div class="genius-section-heading"><h2>SEO services</h2><p>Choose a focused project or combine services in a monthly plan.</p></div><div class="service-catalog">'''+service_rows+'''</div></section>
<section class="container genius-section"><div class="genius-intro"><h2>Know what you are paying for.</h2><div><p>Your quote sets out the work, responsibilities and delivery schedule. Tasks that need your developer or approval are identified before implementation.</p><p>Monthly starting prices are published in US dollars. The final price depends on the work agreed for your website.</p>'''+cta('View pricing','/pricing/',True)+'''</div></div></section>
<section class="container genius-section"><h2>How the work starts</h2><div class="working-steps"><div><h3>Send your website</h3><p>Include the services you sell, target market and the problems you want addressed.</p></div><div><h3>Review the proposal</h3><p>Check the deliverables, price, access requirements and implementation responsibilities.</p></div><div><h3>Review the completed work</h3><p>See the pages and tasks completed, performance observations and remaining priorities.</p></div></div></section>
<section class="container genius-section"><h2>Before you choose an SEO provider</h2><div class="faq-list"><details><summary>Can you guarantee a number-one ranking?</summary><p>No. Search results depend on competition, website conditions and search-engine changes. We define the work and report performance without promising a position or revenue figure.</p></details><details><summary>Do you work with small businesses?</summary><p>Send your website and the work you need. A focused project may be more appropriate than ongoing support when the requirement is limited.</p></details><details><summary>Can you help with local and ecommerce SEO?</summary><p>Yes. Local work can cover your Business Profile and service-area pages. Ecommerce work can cover category structure, product pages and technical controls. The proposal specifies what is included.</p></details><details><summary>How will I know what has changed?</summary><p>Reports identify completed tasks and affected pages. Where access is available, they can include Search Console, analytics and configured enquiry or purchase data.</p></details></div></section>'''+close()+'</main>'
page('', 'SEO Philippines | SEO Geniuses Philippines','SEO services in the Philippines: technical SEO, local search, ecommerce, content and reporting. Review our work, compare starting prices and get a quote.',home)
page('services','SEO Services Philippines','Explore technical, on-page, local and ecommerce SEO, keyword research, content and reporting for Philippine businesses.','<main id="main" class="inner-design">'+opening('SEO services','Choose the work your website needs, from a focused technical project to ongoing content and search support.')+'<section class="container service-catalog">'+service_rows+'</section>'+close()+'</main>')
for slug,data in SERVICES.items():
    related=''.join(f'<p><a href="/services/{x}/">{SERVICES[x]["heading"]}</a></p>' for x in data['related'])
    body='<main id="main">'+opening(data['heading'],data['intro'])+'<section class="section"><div class="container editorial-layout"><article class="article">'+editorial(data['sections'])+'</article><aside class="sidebar"><div class="side-box"><h3>Discuss this service</h3><p>Send your website and the work you need covered.</p>'+cta(href='/contact/?service='+slug)+'</div><div class="side-box"><h3>Related services</h3>'+related+'</div></aside></div></section>'+close()+'</main>'
    page('services/'+slug,data['title'],data['intro'],body,'Service')

about=[('SEO work you can review','SEO Geniuses Philippines provides technical SEO, on-page improvements, local search, ecommerce SEO, content and reporting. Work is available as a defined project or ongoing support, with the scope agreed for your website.'),('A proposal before implementation','We ask about your services, customers and website before preparing a quote. The proposal identifies the work included, the information and access needed, and tasks that require your developer or approval.'),('Your business keeps control','You retain ownership of your website and business accounts. Access should be granted through named users with suitable permissions. Client information and factual claims need your review before publication.'),('Evidence with context','The portfolio contains supplied SEO ranking observations from prior project work. Those observations retain their original market and date. They are examples of search visibility, not promises about future rankings, enquiries or revenue.'),('A practical first step','Send your website and the issue you want addressed. If the requirement is a single technical fix or content project, the quote can reflect that rather than assuming you need a monthly plan.')]
page('about','About SEO Geniuses Philippines','Learn how SEO Geniuses Philippines scopes, delivers and reports on SEO projects for businesses.','<main id="main">'+opening('About SEO Geniuses Philippines','Technical SEO, content and local search support, with the work agreed before it begins.')+'<section class="section"><article class="container policy-copy">'+editorial(about)+'</article></section>'+close()+'</main>')

# Preserve the actual prices and supplied portfolio observations, not new claims.
for slug,title,description in [('pricing','SEO Pricing Philippines','Compare monthly SEO starting prices in US dollars. Your quote confirms the services, responsibilities and delivery schedule.'),('results','SEO Portfolio','Review supplied keyword-ranking observations for healthcare, professional services, retail and trade websites.')]:
    main=BeautifulSoup((ROOT/f'source/{slug}.html').read_text(encoding='utf-8'),'html.parser').main
    for a in main.select('a[href="/for-agencies/"]'):a['href']='/services/white-label-seo/'
    for a in main.select('a[href="/assets/resources/seo_pilot_scope_brief.csv"]'):a.decompose()
    page(slug,title,description,str(main))

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
page('blog','SEO Guides for Philippine Businesses','Practical guides to choosing SEO services, reviewing proposals and improving local search information.','<main id="main">'+opening('SEO guides','Practical checks for business owners reviewing their website and SEO options.')+'<section class="section"><div class="container guide-list">'+guide_rows+'</div></section></main>')
for slug,g in GUIDES.items():
    page('blog/'+slug,g['title'],g['intro'],'<main id="main">'+opening(g['title'],g['intro'])+'<section class="section"><article class="container policy-copy">'+editorial(g['sections'])+'<p>Read the <a href="https://developers.google.com/search/docs/fundamentals/seo-starter-guide">Google Search Central SEO Starter Guide</a> for further guidance.</p></article></section>'+close()+'</main>')

policies={
'privacy-policy':('Privacy policy','How website enquiries are handled.',[
('Information you provide','The quote form asks for your name, email address, website and details of the work requested. Additional business and project details are optional. Do not submit passwords, patient records or confidential client information.'),
('How enquiry information is used',f'Information is used to respond to your enquiry and prepare a proposal. Enquiries are delivered to {INBOX}. Sending a request does not subscribe you to marketing.'),
('External services','GitHub Pages hosts the website. FormSubmit processes quote requests and emails their contents. Its spam checks may use CAPTCHA. Calendly handles information you provide when booking a call. Their privacy policies apply to those services.'),
('Analytics','This website does not currently install an analytics or advertising tracker. Hosting and form providers may process technical request information to operate their services and prevent abuse.'),
('Questions and requests',f'Contact <a href="mailto:{INBOX}">{INBOX}</a> with privacy questions or a request concerning enquiry information you provided.')]),
'terms-of-service':('Terms of service','Website information and service enquiries.',[
('Service agreements','Submitting an enquiry does not create a service agreement. A written proposal confirms the scope, fees, payment arrangements, responsibilities, review process and cancellation terms before work begins.'),
('Published prices','Monthly prices are starting prices in US dollars. The final quote depends on the work agreed. Third-party costs are included only when stated in the proposal.'),
('Search performance','Search positions and traffic can change. Portfolio rankings are supplied, dated observations, not guarantees of a position, traffic level, lead volume or revenue. Past observations do not predict future performance.'),
('Information and access','Provide only information you are entitled to share. Website and account access are arranged separately using appropriate permissions. Do not send credentials through the enquiry form.'),
('External services','Links to external websites and booking services are governed by their own terms. Website information may be updated as services or platform requirements change.')]),
'cookie-policy':('Cookie policy','Cookies and external services.',[
('This website','The static website does not install advertising or analytics cookies. Your browser and hosting provider may process technical information needed to load pages.'),
('Quote requests','Submitting the quote form opens FormSubmit, which may use cookies and CAPTCHA for spam protection. Read its privacy policy before submitting sensitive information.'),
('Bookings','Discovery-call links open Calendly. Cookies and information supplied there are covered by Calendly’s policies.'),
('Browser controls','You can inspect, block or delete cookies through your browser settings. Blocking cookies used by external form or booking services may affect those services.')])}
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
