# Plan: load carousel slides and page SEO from the database

## Context
Slides (image files, alt text) live in `SITE['slides']` in `landingpage/views.py`, and the title, meta description and hidden H1 live in `PAGE`. Editing any of them needs a code change and a deploy. Decision from the user: move **carousel + page SEO** into Django models managed in admin, with **admin uploading two originals per language and the AVIF/WebP/JPG variants auto-generated**, and **Arabic fields added now** (unused until the Arabic page exists). Everything else in `SITE` (services, doctors, FAQ, NAP, hours) stays as is.

Facts checked: Django 6.0.6, SQLite, Pillow 12.2.0 installed with AVIF and WebP support (no new dependency). `landingpage/models.py` and `admin.py` are empty. No `MEDIA_*` settings yet. The page is server-rendered, so SEO is unaffected as long as the same HTML is emitted (H1 before carousel, alt = aria-label, slide 1 preloaded and `fetchpriority="high"`, others lazy).

## Models (`landingpage/models.py`)
- `PageSeo` (one row per page, so more pages can be added later): `key` (unique slug such as `home`, `about`), `path` (URL path, e.g. `/`, used for canonical and sitemap), `title`, `description`, `h1`, plus `title_ar`, `description_ar`, `h1_ar` (blank), `robots` (default `index,follow`), `is_published` (controls sitemap inclusion). Admin allows adding rows; the `home` row cannot be deleted. Length hints in `help_text` (title <= 60, description <= 160).
- Each page view loads its own row with a shared helper `get_page_seo(key)` that falls back to the `PAGE` dict for `home`. `sitemap_xml` later loops over published `PageSeo` rows instead of a hard-coded URL.
- `Slide` is linked to a page: `page` = ForeignKey to `PageSeo` (`related_name='slides'`, `on_delete=CASCADE`). Each page shows only its own active slides, so `index` uses `page.slides.filter(is_active=True)`. In admin, `SlideAdmin` shows and filters by page. `slug` uniqueness is global (it names the generated files); `order` applies within a page.
- `Slide`: `order` (PositiveSmallInteger, ordering), `is_active`, `slug` (stem, unique, e.g. `family-healthcare-makkah`), `alt`, `alt_ar`, originals `desktop_image`, `mobile_image`, `desktop_image_ar`, `mobile_image_ar` (ImageField, `upload_to='carousel/originals/'`, Arabic ones optional). Generated files are not model fields; paths are derived from `slug`.
- `Slide.save()` calls a helper that writes variants to `MEDIA_ROOT/carousel/<slug>[-ar]-<desktop|mobile>.<avif|webp|jpg>`: desktop resized to 1600 px wide, mobile to 768 px wide (same sizes as now), JPG q85, WebP q80, AVIF q55. Regenerate only when the original changed; delete stale variants on slug change or delete.
- `Slide.clean()` validates aspect ratios (desktop ~1600:602, mobile ~768:922, Arabic mobile may differ) so the fixed CSS `aspect-ratio` and `width/height` attributes stay correct. Properties `desktop_url('avif'|...)`, `mobile_url(...)` for templates.

Put image processing in `landingpage/imaging.py` (pure function `make_variants(src, dest_stem, width)`), not in the model, to keep models readable.

## Wiring
- `settings.py`: add `MEDIA_URL = 'media/'`, `MEDIA_ROOT = BASE_DIR / 'media'`.
- `SafaMakkah2/urls.py`: serve media with `static()` only when `DEBUG`. Production needs the web server to serve `/media/` (note in spec).
- `.gitignore`: add `media/`.
- `landingpage/admin.py`: `SlideAdmin` (list_display page/order/slug/is_active/thumbnail, `list_filter` page, `list_editable` order and is_active, `ordering`), `PageSeoAdmin` (list_display key/path/title/is_published; `home` not deletable).
- `landingpage/views.py`: remove `slides` from `SITE`; `PAGE` becomes the fallback. `index` builds `page = PageSeo.objects.filter(key='home').first()` (falling back to the `PAGE` dict) and `slides = page.slides.filter(is_active=True)` when the row exists, so the site never renders with an empty title or H1. One query each, no per-request image work.
- `templates/partials/hero_carousel.html`: loop over `slides` instead of `site.slides`; replace the `{% static 'img/carousel/' %}{{ slide.file }}-...` URLs with `slide.desktop_url`/`mobile_url`; skip the whole partial if there are no active slides.
- `templates/index.html`: the slide-1 AVIF preload uses the first active slide's URLs; H1 and meta already read `page.*`, so unchanged.
- Migration `0001_initial` plus a management command `seed_carousel` that creates the `home` PageSeo row and the three current slides linked to it from today's values (alt/alt_ar/title/description/h1). Originals for the seed are the existing JPGs in `static/img/carousel/` (desktop and mobile, en and ar), copied into `media/` and re-run through `make_variants`.
- After seed is verified, delete the 36 files under `landingpage/static/img/carousel/`.
- Update spec `.claude/docs/spec/01-single-page-website-spec.md` (data source for slides and SEO, media serving note).

## Not changing
- CSS, JS, JSON-LD, all other sections, the always-on animation behaviour. No Arabic page yet. No caching layer (two cheap queries).

## Risks to handle
- AVIF encoding is slow-ish on save; acceptable for admin use.
- Replacing an image must delete old variants; renaming `slug` must move/delete them.
- Uploaded wrong-ratio images are rejected in `clean()` with a clear message rather than distorting the hero.

## Verification
1. `py manage.py makemigrations landingpage`, `migrate`, `seed_carousel`, `check`.
2. Test client: `/` returns 200; exactly one `<h1>` immediately before the carousel; every carousel `<img>` has `alt` equal to its slide's `aria-label`; slide 1 has `fetchpriority="high"` and a matching preload, slides 2 and 3 are `loading="lazy"`; JSON-LD still parses.
3. Admin (`createsuperuser`, run server): add a slide with two uploads, confirm the 6 variant files appear under `media/carousel/`, reorder with `order`, untick `is_active` and see it vanish, change the H1 and see it on the page; upload a wrong-ratio image and see the validation error; delete all slides and confirm the page still renders without a carousel.
4. Headless Chrome: carousel visually identical to today on desktop (1600) and mobile (768), progress line and controls working.
5. Confirm served image bytes load from `/media/carousel/...` with correct types (avif/webp/jpg).
