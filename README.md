# SEO Geniuses Philippines

Independent static website for https://seogeniusesphilippines.com. Uses the owner's existing visual layout with independently written copy targeting SEO Philippines. The positioning describes SEO provision from the Philippines without restricting the client's market.

## Build and check

```sh
python -m pip install -r requirements.txt
python build.py --base-url https://erwinmehehe.github.io/seogeniusesphilippines
python check.py
python originality.py
python -m http.server 8787 --directory dist
```

For a local preview, use `python build.py --base-url http://localhost:8787` before starting the server. The `dist` folder contains deployable static files; no PHP or database is required.

Once the custom domain resolves to GitHub Pages, build with `python build.py --indexable`. Only this mode enables indexing and creates CNAME. The GitHub workflow automatically selects this mode when Pages reports the canonical domain as its configured URL.

## Content and assets

- `source/content.py`: distinct service pages and practical guides.
- `build.py`: layout, homepage, company pages, policy copy and metadata.
- `source/pricing-content.html`: independently written pricing explanations; the existing USD 700, 1,000 and 1,500 starting amounts are preserved. `source/measurement.html`: original reporting guidance instead of a duplicate portfolio. The genuine portfolio remains on SEO Outsourcing Philippines.
- `assets/`: duplicated base layout, brand-specific styles and small navigation/filter script.
- `brand/`: original G monogram, outlined wordmarks, favicon, touch icon and social image. Vector files need no external font. `make_brand.py` is the optional Windows authoring script; its generated files are committed, so deployment does not need fonts or Pillow.

## Enquiries

The form posts natively to FormSubmit and uses the existing authorised inbox, info@seooutsourcingphilippines.com. The recipient is disclosed on the contact page and in the privacy policy. The subject identifies SEO Geniuses Philippines. No new mailbox or analytics property is assumed.

FormSubmit activation may be required for each new origin. After deployment, submit a test, activate the form from the inbox if requested, complete its CAPTCHA and confirm both email receipt and return to `/quote-request-sent/`. A static form configuration check cannot establish inbox delivery.

## Domain setup

GitHub Pages can first serve the project preview. To move to the domain, set the Pages custom domain to `seogeniusesphilippines.com`, replace conflicting website A/AAAA records with GitHub Pages records, and point `www` by CNAME to `erwinmehehe.github.io`. Keep MX, SPF, DKIM, DMARC and other email records intact. Enable HTTPS when the certificate is ready, then rerun the workflow.

Do not copy the old site's Search Console verification or GA4 identifier. Add verified settings for the new brand separately.

## Copy separation

`python originality.py` compares substantial main-content blocks and sentences with a hashed reference of 116 SEO Outsourcing Philippines source pages. CI rejects exact matches after punctuation and case normalisation. The check permits short standard navigation labels, service names and factual price amounts; it does not claim internet-wide uniqueness.
