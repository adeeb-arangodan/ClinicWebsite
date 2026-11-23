# Implementation Plan: Single-Page Website, Safa Makkah Polyclinic 2

Spec: `.claude/docs/spec/01-single-page-website-spec.md` (section numbers below refer to it).

## Current repo state

- `landingpage` app exists (startapp stub) but is not in `INSTALLED_APPS`.
- `SafaMakkah2/urls.py` has only `admin/`; `landingpage/views.py` is empty.
- Stray empty `landingpage/templates/landingpage/index.html` exists. The spec wants `landingpage/templates/index.html`, so remove it.
- `APP_DIRS=True`; Pillow 12.2 is installed (used for placeholder images).

## Rules for the executing agent

- Run with execution permissions on (a previous hand-off was blocked by plan mode).
- Open questions (spec section 13) stay as clearly marked TODO placeholders. Do not invent real clinic data.
- Do not commit to git. Do not build anything listed as out of scope (spec section 12).

## Phases

### 1. Wiring (spec 2, 3)
- [ ] Add `landingpage` to `INSTALLED_APPS`
- [ ] Include `landingpage.urls` in `SafaMakkah2/urls.py`
- [ ] Add TODO settings: `SITE_DOMAIN`, `GA_MEASUREMENT_ID`
- [ ] Delete the stray `templates/landingpage/index.html`
- [ ] Create `landingpage/templates/partials/` and `landingpage/static/{css,js,img/{carousel,clinic,doctors,logo,og}}`

### 2. Views and context (spec 2, 9)
- [ ] `landingpage/views.py` and `urls.py`: `/`, `/robots.txt` (text/plain), `/sitemap.xml` (application/xml)
- [ ] One `SITE` dict (NAP, hours, geo, doctors, services, FAQ, insurers), all TODO values. Footer, contact section and JSON-LD all render from it (single source of truth for NAP)
- [ ] Build JSON-LD with `json.dumps`, escaping `</`

### 3. `base.html` and `index.html` (spec 5, 7.1)
- [ ] Blocks: `title`, `meta_description`, `meta_robots`, `canonical`, `hreflang`, `og_twitter`, `preloads`, `jsonld`, `extra_head`, `content`, `scripts`
- [ ] Skip link, `<header>`, `<main id="main">`, footer include, back-to-top button, `lang`/`dir` variables
- [ ] Bootstrap 5 CDN (pinned version), preconnect, deferred JS, GA4 placeholder `async`
- [ ] `index.html`: override SEO blocks, hidden H1 directly before carousel include, then includes in spec 6 order: services, doctors, insurance, packages, about, testimonials, faq, contact (no intro section)

### 4. Navbar and carousel (spec 6, 7.2, 7.3, 8)
- [ ] Sticky navbar, anchor links per spec 6 table, mobile collapse with aria attributes, EN/AR toggle placeholder, RTL-safe, scrollspy, tap targets >= 48px
- [ ] Carousel: 3 slides, no heading tags, alt equals aria-label (baked-in heading + keyword), autoplay, indicators, prev/next, keyboard operable, reduced-motion respected
- [ ] Slide 1: preload in head, `fetchpriority="high"`, not lazy. Slides 2-3: `loading="lazy"`
- [ ] `<picture>` with AVIF/WebP/JPG, mobile and desktop `srcset`/`sizes`, explicit width/height, descriptive filenames

### 5. Sections and footer (spec 7.4, 7.5)
- [ ] Each section partial: anchor id, `aria-labelledby`, one H2, H3 items, placeholder copy meeting per-section minimum, TODO marker
- [ ] FAQ: Bootstrap accordion, answers always in the DOM
- [ ] Insurance: insurer logo/name grid with alt text
- [ ] Contact: lazy Google Map iframe with `title`, Google Business Profile link, directions link
- [ ] Footer: `<address>` NAP, hours, social placeholders

### 6. Structured data (spec 9)
- [ ] Separate `ld+json` blocks: MedicalClinic/LocalBusiness, Physician per doctor, FAQPage mirroring the visible FAQ exactly

### 7. Static assets (spec 10)
- [ ] `site.css`: logical properties for RTL, navbar-height CSS variable driving `scroll-margin-top`, smooth scroll, `prefers-reduced-motion`
- [ ] `site.js`: back-to-top only
- [ ] Placeholder images via Pillow: carousel 1600x600 and 768x600 (jpg, webp, avif if encodable), clinic photo, doctor avatars, SVG logo, `og-share-1200x630.jpg`

### 8. Verification (spec 11)
- [ ] `py manage.py check`
- [ ] Dev server: `/`, `/robots.txt`, `/sitemap.xml` return 200 with correct content types
- [ ] Raw HTML: exactly one `<h1>`, no skipped heading levels, alt on every image, title <= 60 and description <= 155 chars, NAP identical in footer, contact and JSON-LD
- [ ] Manual check with `dir="rtl"`
- [ ] Manual, once real content and a public URL exist: Lighthouse SEO >= 95, Rich Results Test, mobile-friendly test, Core Web Vitals

## Report back

The agent reports which section 11 items pass, which need external tools or real content, and any deviations from the spec.
