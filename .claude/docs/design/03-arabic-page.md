# Plan: Arabic version at /ar/ (navbar + carousel Arabic, language button toggles)

## Context
The navbar has a placeholder "العربية" link (`href="#"`). The user wants: clicking it shows the page in Arabic, with the **navbar and the carousel images in Arabic**, and the button then reads **"English"** (switching back). Decisions from the user: **separate URL `/ar/`** (server-rendered, SEO-friendly, hreflang) and **the sections below the carousel stay English for now** (Arabic text not supplied yet).

Already in place: Arabic carousel artwork for all 3 slides (`Slide.*_image_ar`, generated to `media/carousel/<slug>-ar-{desktop,mobile}.*`), `Slide.alt_ar`, `Slide.desktop_ar/mobile_ar` URL properties, `PageSeo.title_ar/description_ar/h1_ar`, `base.html` already takes `lang` and `dir`, `hero_carousel.html` renders from a `slides` context list, `get_page_seo(key)` in `landingpage/views.py`.

## Changes
1. **Routing** (`landingpage/urls.py`): add `path('ar/', views.index, {'lang': 'ar'}, name='index_ar')`; `index(request, lang='en')`.
2. **Localised data** (`landingpage/views.py`):
   - `UI` dict with `en`/`ar` strings for the navbar (Home, Doctors, Insurance, Packages, Services, Contact, Book / Enquire), brand name, skip link, carousel aria-label, Previous/Next, toggle label and href (`العربية` -> `/ar/`, `English` -> `/`). Arabic draft: الرئيسية، الأطباء، التأمين، الباقات، الخدمات، اتصل بنا، احجز / استفسر. The Arabic copy needs a native-speaker review.
   - `get_page_seo(key, lang)` returns a localised object (title/description/h1) using the `_ar` fields with English fallback when blank; slides become a list of `SimpleNamespace(alt, desktop, mobile)` using `alt_ar`/`desktop_ar`/`mobile_ar` for Arabic, falling back to English when an Arabic image is missing. Templates then need no per-language branching for slides.
   - Context adds `lang`, `dir` (`rtl` for ar), `ui`, `url_en`, `url_ar`, and `canonical_url` per language.
3. **Templates**:
   - `base.html`: use `bootstrap.rtl.min.css` when `dir == 'rtl'` (same CDN, version 5.3.3); translate the skip link via `ui`.
   - `partials/navbar.html`: labels from `ui`; language toggle uses `ui.toggle_label`, `ui.toggle_href`, `lang`/`hreflang` of the target language; brand name Arabic on `/ar/`.
   - `partials/hero_carousel.html`: aria-labels/Prev/Next from `ui`; add `hero-img-ar` class on `/ar/` for the Arabic mobile ratio.
   - `index.html`: real hreflang links (`en` -> `/`, `ar` -> `/ar/`, `x-default` -> `/`), `og:locale` swapped per language, canonical per language, slide-1 preload uses the localised slide.
   - `sitemap.xml`: two `<url>` entries (`/` and `/ar/`), each with the full hreflang set.
4. **CSS** (`static/css/site.css`): `@media (max-width: 767.98px) { .hero-img-ar { aspect-ratio: 768 / 960; } }`. Check RTL for: carousel prev/next chevron direction, indicator pill centring, navbar spacing (`mx-lg-auto`, gaps), back-to-top corner (already `inset-inline-end`). Fix only what looks wrong.
5. **Data**: extend `seed_carousel` (or a small `seed_arabic_seo` step) to fill blank `title_ar/description_ar/h1_ar` on the `home` row with draft Arabic text, never overwriting existing values; editable in admin afterwards.
6. **Docs**: update spec section 13 and the hreflang notes in `.claude/docs/spec/01-single-page-website-spec.md`.

## Not changing
- Section partials below the carousel (stay English), JSON-LD (English for now), models/migrations (Arabic fields already exist), footer content beyond the skip link and chrome text. No language cookie or auto-redirect (the URL is the language; crawlers must reach both).

## Verification
1. `py manage.py check`; test client: `/` and `/ar/` both 200.
2. `/ar/`: `<html lang="ar" dir="rtl">`, one H1 (Arabic) before the carousel, Arabic navbar labels, toggle reads "English" with `href="/"`; `/` toggle reads "العربية" with `href="/ar/"`.
3. `/ar/` slide `<img>` sources are the `-ar-` files and alt equals aria-label; slide 1 preload points at the Arabic AVIF; all `/media/` URLs return 200.
4. hreflang/canonical correct on both pages; sitemap lists both URLs; JSON-LD still parses.
5. Headless Chrome screenshots of `/ar/` at 1600 and 390 px widths (navbar, carousel, controls, progress line) and `/` unchanged; fix any RTL issues found. Then the user checks in their own browser.
