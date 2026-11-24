# Spec: Single-Page Website, Safa Makkah Polyclinic 2

Status: draft for hand-off to a coding agent. **Do not treat this as implementation.** SEO is a first-class requirement.

## 1. Goal

One page (`index.html`) of stacked sections. Navbar links smooth-scroll to section anchors (`#about`, `#services`, ...). The page is assembled from a base template plus partials, one part per file. Audience: patients searching locally (Makkah, Saudi Arabia) for clinic services, in English and Arabic.

## 2. Stack and constraints

| Item | Decision |
|---|---|
| Templating | Django templates: `{% extends %}`, `{% block %}`, `{% include %}`, `{% static %}` |
| UI | Bootstrap 5 via CDN (navbar, carousel, grid, accordion, scrollspy) |
| Own assets | Plain CSS/JS in `static/`, no build step |
| Rendering | Server-rendered only. All content in the initial HTML response; no client-side content rendering |
| Django wiring | Existing project `SafaMakkah2`, app `landingpage`. Templates and static files live inside `landingpage/` (see section 3). Needs only: `landingpage` in `INSTALLED_APPS`, a render-only view for `/`, routes for `robots.txt` and `sitemap.xml`. No other backend logic |

## 3. Folder tree

```
SafaMakkah2/
├─ manage.py
├─ SafaMakkah2/            (settings.py: add "landingpage" to INSTALLED_APPS; urls.py includes landingpage.urls)
└─ landingpage/            (the single app; owns its own templates and static)
   ├─ views.py, urls.py    (render index, robots, sitemap)
   ├─ templates/
   │  ├─ base.html
   │  ├─ index.html
   │  ├─ robots.txt        (template, served as text/plain)
   │  ├─ sitemap.xml       (template, served as application/xml)
   │  └─ partials/
   │     ├─ navbar.html
   │     ├─ hero_carousel.html
   │     ├─ section_services.html
   │     ├─ section_doctors.html
   │     ├─ section_insurance.html
   │     ├─ section_packages.html
   │     ├─ section_about.html
   │     ├─ section_testimonials.html
   │     ├─ section_faq.html
   │     ├─ section_contact.html
   │     └─ footer.html
   └─ static/
      ├─ css/site.css
      ├─ js/site.js
      └─ img/
         ├─ carousel/   (3 slides x mobile/desktop x webp/avif/jpg)
         ├─ clinic/
         ├─ doctors/
         ├─ logo/
         └─ og/         (og-share-1200x630.jpg)
```

Templates and static live **inside `landingpage/`**, not at project root. They are discovered via `APP_DIRS: True` and the default `AppDirectoriesFinder`, so no `TEMPLATES["DIRS"]` or `STATICFILES_DIRS` entries are needed. Reference assets as `{% static 'css/site.css' %}`; include partials as `{% include "partials/navbar.html" %}`.

## 4. Extends / include diagram

```
index.html  ──extends──▶  base.html
                            ├─ {% block seo_* %}  (head, overridden by index.html)
                            ├─ include partials/navbar.html
                            ├─ {% block content %}  ◀── filled by index.html:
                            │     include partials/hero_carousel.html   (H1 sr-only sits directly before it)
                            │     include partials/section_services.html
                            │     include partials/section_doctors.html
                            │     include partials/section_insurance.html
                            │     include partials/section_packages.html
                            │     include partials/section_about.html
                            │     include partials/section_testimonials.html
                            │     include partials/section_faq.html
                            │     include partials/section_contact.html
                            ├─ include partials/footer.html
                            └─ {% block scripts %}  (deferred JS)
```

## 5. Blocks in `base.html` and what `index.html` must override

| Block | Location | index.html overrides with |
|---|---|---|
| `html_attrs` / `lang`, `dir` | `<html>` | `lang="en" dir="ltr"` (variable-driven, RTL-ready) |
| `title` | `<head>` | Title string (see 7.1) |
| `meta_description` | `<head>` | Description string |
| `meta_robots` | `<head>` | `index, follow` (default in base) |
| `canonical` | `<head>` | Absolute canonical URL |
| `hreflang` | `<head>` | en, ar, x-default links |
| `og_twitter` | `<head>` | OG + Twitter tags, 1200x630 image |
| `preloads` | `<head>` | Preload of slide-1 image (responsive) |
| `jsonld` | `<head>` | MedicalClinic, Physician[], FAQPage blocks |
| `extra_head` | `<head>` | Search Console verification meta, GA4 placeholder (async) |
| `content` | `<main>` | The section includes in order |
| `scripts` | before `</body>` | Deferred `site.js`; Bootstrap JS bundle `defer` |

`base.html` itself holds: doctype, skip link (`<a href="#main">`), `<header>` wrapping navbar include, `<main id="main">`, footer include, back-to-top button.

## 6. Sections, anchors, navbar mapping

Every section: `<section id="..." aria-labelledby="...">`, one H2, short placeholder body, `{# TODO: real copy #}` marker.

| Order | Partial | Anchor id | Navbar label (descriptive) | Heading (H2) |
|---|---|---|---|---|
| 0 | hero_carousel | `#top` (page start / logo link) | Logo -> top | none (H1 is hidden, before carousel) |
| 1 | section_services | `#services` | Medical Services | Our Medical Services in Makkah |
| 2 | section_doctors | `#doctors` | Our Doctors | Meet Our Doctors |
| 3 | section_insurance | `#insurance` | Insurance | Accepted Insurance Providers |
| 4 | section_packages | `#packages` | Health Packages | Health Check-up Packages |
| 5 | section_about | `#about` | About the Clinic | About Safa Makkah Polyclinic 2 |
| 6 | section_testimonials | `#testimonials` | Patient Reviews | What Our Patients Say |
| 7 | section_faq | `#faq` | FAQ | Frequently Asked Questions |
| 8 | section_contact | `#contact` | Contact and Location | Contact and Find Us |

### Scroll behavior

- Smooth scroll: CSS `html { scroll-behavior: smooth; }`. Animations are always on, even when the OS requests reduced motion (product decision; a user-facing opt-out is a possible future feature).
- Sticky navbar: `position: sticky; top: 0` (Bootstrap `sticky-top`). Sections use `scroll-margin-top` equal to navbar height (CSS variable) so headings are not covered.
- Scrollspy: Bootstrap scrollspy on `<body data-bs-spy="scroll" data-bs-target="#mainNav" data-bs-root-margin=...>`; active link gets `aria-current="true"`.
- Back-to-top: button appears after ~600px scroll, links to `#top`, min 48x48px, focusable, labelled.
- Anchor URLs are fragments only; no JS routing.

## 7. Per-file responsibilities and placeholder content

### 7.1 `base.html` and `index.html` (head and SEO)

| Tag | Rule |
|---|---|
| `<title>` | Pattern: `{Primary keyword} in Makkah \| Safa Makkah Polyclinic 2`. **<= 60 chars.** Placeholder: `Polyclinic in Makkah \| Safa Makkah Polyclinic 2` |
| meta description | Pattern: service list + city + CTA. **<= 155 chars.** Unique, human-readable |
| Primary keyword targets (to confirm, see section 13) | "polyclinic in Makkah", "clinic in Makkah", "doctors in Makkah"; secondary per service |
| canonical | Absolute, self-referencing, one per language version |
| robots meta | `index, follow, max-image-preview:large` |
| viewport | `width=device-width, initial-scale=1` |
| Open Graph | `og:type=website`, `og:title`, `og:description`, `og:url`, `og:image` (1200x630, absolute URL), `og:image:alt`, `og:locale` (+ `og:locale:alternate`), `og:site_name` |
| Twitter | `summary_large_image`, title, description, image, image alt |
| hreflang | `en`, `ar`, `x-default` (URL strategy: open question) |
| Verification | `<meta name="google-site-verification" content="TODO">` |
| Analytics | GA4 snippet placeholder, loaded `async`, in `extra_head`, behind a `GA_MEASUREMENT_ID` setting; no render-blocking |
| Performance hints | `preconnect` to Bootstrap CDN (and Google Fonts if used); `font-display: swap`; one small CSS file; JS `defer` |

### 7.2 `navbar.html`

Inside `<header>`/`<nav aria-label="Main">`. Layout follows the design mock `Nav.PNG`: logo + "Safa Makkah Polyclinic - 2" on the left; centered links **Home (`#top`), Doctors, Insurance, Packages, Services, Contact**; on the right an outlined white "العربية" language button and a teal-to-green gradient "Book / Enquire" button linking to `#contact`. About, Reviews and FAQ are not in the navbar (reachable by scrolling). Logo (links to `#top`, has alt), Bootstrap collapse for mobile (toggler with `aria-controls`, `aria-expanded`, `aria-label`), EN/AR toggle placeholder (a link/button with `hreflang` and `lang` attributes, non-functional until URL strategy decided; layout must survive `dir="rtl"`, use logical CSS properties e.g. `margin-inline-start`). Tap targets >= 48px. Navbar is edited only here.

### 7.3 `hero_carousel.html`

Rules in section 8. Placeholder: 3 slides with placeholder images.

### 7.4 Content sections

| Partial | H3 items | Min visible copy | Keyword guidance | Placeholder |
|---|---|---|---|---|
| about | optional (Our Mission, Our Facilities) | 150 words | clinic name, Makkah, established/licence | Lorem-style text + clinic photo |
| services | one H3 per service/department (>=6) | 40-60 words each | service + "in Makkah" | Service cards (icon, H3, text) |
| doctors | one H3 per doctor | 40 words each | specialty + Makkah | Photo, name, specialty, qualifications; `Physician` JSON-LD per doctor |
| insurance | one H3 per insurer or group (optional) | 80 words + list | "insurance accepted clinic Makkah" | Intro text, insurer logo/name grid (alt text per logo), how-to-claim note, TODO list of providers |
| packages | one H3 per package | 30 words + list | "health check-up package Makkah" | 3 package cards, prices TODO |
| testimonials | H3 optional per review | 3+ reviews | natural | Quote, name/initial, source. Real reviews only; no fabricated ratings markup |
| faq | one item per question (button label may be a heading level H3) | 6-8 Q&As, 40-80 words per answer | question-form queries | Bootstrap accordion; answers **always in DOM** (collapsed via CSS class, never removed or injected by JS) |
| contact | H3: Address, Phone, Hours | NAP + map | NAP | Address, phone, hours, embedded Google Map iframe (`loading="lazy"`, `title`), Google Business Profile link, directions link |

### 7.5 `footer.html`

`<footer>` with `<address>` containing NAP, opening hours, social links placeholders (`rel="noopener"`), GBP link, copyright. NAP text must be **identical** to contact section and JSON-LD (store once in a context/dict and render everywhere).

## 8. Carousel and H1 rules

1. Exactly one H1 per page. Visually hidden (`.visually-hidden`), placed **directly before** the carousel markup. One natural sentence: clinic name + primary keyword + city, e.g. "Safa Makkah Polyclinic 2: trusted polyclinic and family doctors in Makkah". No keyword stuffing.
2. No heading tags inside the carousel (headings are baked into images).
3. Each slide `<img>` alt = baked-in heading text + target keyword; identical to the slide's `aria-label`.
4. Slide 1: `<link rel="preload" as="image" imagesrcset imagesizes>` in head, `fetchpriority="high"`, **not** lazy (LCP element). Slides 2 and 3: `loading="lazy"`, `decoding="async"`.
5. Images: explicit `width`/`height` (reserve aspect ratio, no CLS), `<picture>` with AVIF/WebP sources + JPG fallback, separate mobile and desktop crops via `srcset`/`sizes` (suggest 768w and 1600w+), descriptive filenames (e.g. `polyclinic-makkah-family-medicine-desktop.webp`).
6. Behavior: autoplay (`data-bs-ride="carousel"`, ~5-6s), indicators, prev/next controls with visually-hidden labels, keyboard operable, pause on hover/focus; transitions stay on regardless of `prefers-reduced-motion`.
7. Do not rely on carousel content for keyword value; visible keyword text lives in the sections below (the services section directly follows the carousel, so its H2 and opening paragraph must carry the clinic name, Makkah and primary keywords naturally).
8. Heading hierarchy: one H1 (hidden), H2 per section, H3 for items; never skip levels; no headings used only for styling (use classes).

## 9. SEO requirements

| Area | Requirement |
|---|---|
| Semantic HTML | `header`, `nav`, `main`, `section`, `article` (per doctor/package/review/service card where self-contained), `footer`, `address` |
| JSON-LD | Separate `<script type="application/ld+json">` blocks in `jsonld` block: (a) `MedicalClinic` (+ `LocalBusiness`): name, url, address (PostalAddress), geo, telephone, openingHoursSpecification, logo, image, sameAs (GBP, socials), priceRange optional, areaServed, medicalSpecialty; (b) `Physician` per doctor (name, medicalSpecialty, image, worksFor); (c) `FAQPage` mirroring the visible FAQ text exactly. Data must match visible page |
| Local SEO | Consistent NAP in footer, contact, schema; embedded Google Map; Google Business Profile link |
| Social | OG + Twitter tags, 1200x630 share image |
| Indexing | Canonical, robots meta, `robots.txt` (Allow all, Sitemap line), `sitemap.xml` (home URL + language alternates, `lastmod`) |
| Multilingual | `hreflang` en/ar/x-default, `lang`/`dir` on `<html>`, URL strategy open (e.g. `/en/`, `/ar/`) |
| Images | Descriptive alt, width/height, lazy-load below the fold, modern formats |
| Core Web Vitals | LCP < 2.5s, CLS < 0.1, INP < 200ms; `font-display: swap`, defer JS, minimal CSS, preconnect CDNs |
| Links | Descriptive anchor text (no "click here") |
| FAQ | Accordion answers stay in the DOM |
| Mobile | Mobile-first, responsive, viewport meta, tap targets >= 48px |
| Accessibility | Alt text, aria labels, skip link, WCAG AA contrast, visible focus (animations deliberately ignore `prefers-reduced-motion`) |
| Analytics | Verification meta placeholder, GA4 placeholder, non-blocking |

### Content guidance (avoid thin content)

Total visible copy target: ~1,200+ words (EN). Per-section minimums in 7.4. Each section targets one keyword theme; vary phrasing, no repetition for its own sake. Arabic copy must be written natively, not machine-translated.

### Single-page caveat

Limits: one URL, one title/description, one primary ranking target, anchors are not separately indexable, long page can dilute topical focus. If rankings matter, plan future separate pages for key services (e.g. `/services/dental/`) and doctors, with their own titles and schema. Out of scope now.

## 10. Assets

| Asset | Placeholder now | Real file goes in |
|---|---|---|
| 3 carousel images | Solid-colour placeholders at final dimensions (e.g. 1600x600 desktop, 768x600 mobile), webp+jpg | `static/img/carousel/` |
| Clinic photo | Placeholder | `static/img/clinic/` |
| Doctor photos | Placeholder avatars | `static/img/doctors/` |
| Logo | Placeholder SVG/PNG | `static/img/logo/` |
| Share image | 1200x630 placeholder | `static/img/og/` |

## 11. Acceptance criteria

- [ ] Exactly one H1, present in raw HTML source (view-source), visually hidden, directly before the carousel
- [ ] Heading order H1 > H2 > H3 with no skipped levels; no heading tags in carousel
- [ ] All images have alt text; carousel alts carry heading text + keyword and equal slide `aria-label`
- [ ] Slide 1 preloaded, `fetchpriority="high"`, not lazy; slides 2-3 lazy
- [ ] All images have width/height; srcset/sizes and WebP/AVIF with fallback
- [ ] Title <= 60 chars; meta description <= 155 chars
- [ ] Canonical, robots meta, hreflang, OG, Twitter tags present
- [ ] Lighthouse SEO >= 95 (also target Performance/Accessibility/Best Practices >= 90)
- [ ] LCP < 2.5s, CLS < 0.1, INP < 200ms on mobile profile
- [ ] JSON-LD valid in Google Rich Results Test and Schema.org validator (MedicalClinic, Physician, FAQPage)
- [ ] NAP identical in footer, contact section, JSON-LD
- [ ] `/sitemap.xml` and `/robots.txt` reachable (200, correct content types)
- [ ] Passes mobile-friendly check; tap targets >= 48px; no horizontal scroll
- [ ] FAQ answers present in DOM when collapsed
- [ ] Navbar: sticky, collapses on mobile, smooth scroll with correct offset, scrollspy, back-to-top work; keyboard operable; skip link works
- [ ] Page renders correctly with `dir="rtl"` (layout check)
- [ ] Editing navbar (or footer) in one file updates the page; no duplicated markup
- [ ] No render-blocking third-party scripts; JS deferred

## 12. Out of scope

Backend logic, form processing (contact form is out; use tel/WhatsApp/map links), patient portal, CMS, extra pages, booking system, actual Arabic translation work.

## 13. Open questions

1. Production domain (for canonical, sitemap, OG, schema URLs)?
2. Arabic version URL strategy: `/en/` + `/ar/`, subdomain, or query/toggle on one URL? Is Arabic in v1?
3. Target keywords (EN and AR) and priority services?
4. Google Business Profile: exists/verified? URL and place ID?
5. Final NAP: address, geo coordinates, phone/WhatsApp, opening hours, languages?
6. Doctors list, specialties, licence info, and permission to publish photos?
7. Services and packages list, and whether prices are shown?
8. Real testimonials available (and consent)? Any ratings data?
9. Brand: logo, colours, fonts (Arabic font choice)?
10. Social profiles for `sameAs`?
11. GA4 / Search Console accounts and IDs?
12. Saudi MOH licence or regulatory disclaimers required in footer?
13. Hosting and static file serving (WhiteNoise, nginx, CDN)?
