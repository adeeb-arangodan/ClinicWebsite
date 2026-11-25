from pathlib import Path

from PIL import Image

# Extension -> (Pillow format, save options)
FORMATS = {
    'avif': ('AVIF', {'quality': 55}),
    'webp': ('WEBP', {'quality': 80}),
    'jpg': ('JPEG', {'quality': 85}),
}


def make_variants(src, dest_stem, width):
    """Write <dest_stem>.avif/.webp/.jpg from src, resized to `width` px wide."""
    dest_stem = Path(dest_stem)
    dest_stem.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert('RGB')
        if im.width != width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        for ext, (fmt, opts) in FORMATS.items():
            im.save(f'{dest_stem}.{ext}', fmt, **opts)


def remove_variants(dest_stem):
    for ext in FORMATS:
        Path(f'{dest_stem}.{ext}').unlink(missing_ok=True)


def variants_exist(dest_stem):
    return all(Path(f'{dest_stem}.{ext}').exists() for ext in FORMATS)
