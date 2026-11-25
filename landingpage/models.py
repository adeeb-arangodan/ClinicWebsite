from types import SimpleNamespace

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from . import imaging

# Upload field -> (file suffix, kind, generated width in px, expected width/height ratio or None)
VARIANT_FIELDS = {
    'desktop_image': ('', 'desktop', 1600, 1600 / 602),
    'mobile_image': ('', 'mobile', 768, 768 / 922),
    'desktop_image_ar': ('-ar', 'desktop', 1600, 1600 / 602),
    'mobile_image_ar': ('-ar', 'mobile', 768, None),  # Arabic mobile artwork has its own ratio
}
RATIO_TOLERANCE = 0.02


class PageSeo(models.Model):
    key = models.SlugField(unique=True, help_text='Internal name, e.g. "home". The home page uses "home".')
    path = models.CharField(max_length=200, default='/', help_text='URL path, e.g. "/".')
    title = models.CharField(max_length=120, help_text='Browser/search title. Aim for 60 characters or fewer.')
    description = models.CharField(max_length=300, help_text='Meta description. Aim for 160 characters or fewer.')
    h1 = models.CharField('H1 (hidden)', max_length=200)
    title_ar = models.CharField(max_length=120, blank=True)
    description_ar = models.CharField(max_length=300, blank=True)
    h1_ar = models.CharField('H1 (Arabic)', max_length=200, blank=True)
    robots = models.CharField(max_length=40, default='index,follow')
    is_published = models.BooleanField(default=True, help_text='Unpublished pages are left out of the sitemap.')

    class Meta:
        ordering = ['key']
        verbose_name = 'page SEO'
        verbose_name_plural = 'page SEO'

    def __str__(self):
        return f'{self.key} ({self.path})'


class Slide(models.Model):
    page = models.ForeignKey(PageSeo, on_delete=models.CASCADE, related_name='slides')
    order = models.PositiveSmallIntegerField(default=0, help_text='Lower numbers show first.')
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, help_text='Names the generated files, e.g. "family-healthcare-makkah". Keep it descriptive for SEO.')
    alt = models.CharField(max_length=300, help_text='Describe the text in the image: it is the alt text and the slide label.')
    alt_ar = models.CharField(max_length=300, blank=True)
    desktop_image = models.ImageField(upload_to='carousel/originals/', help_text='About 1600 x 602.')
    mobile_image = models.ImageField(upload_to='carousel/originals/', help_text='About 768 x 922.')
    desktop_image_ar = models.ImageField(upload_to='carousel/originals/', blank=True)
    mobile_image_ar = models.ImageField(upload_to='carousel/originals/', blank=True)

    class Meta:
        ordering = ['page', 'order', 'id']

    def __str__(self):
        return self.slug

    @staticmethod
    def _stem(slug, suffix, kind):
        return settings.MEDIA_ROOT / 'carousel' / f'{slug}{suffix}-{kind}'

    def _urls(self, suffix, kind):
        base = f'{settings.MEDIA_URL}carousel/{self.slug}{suffix}-{kind}'
        return SimpleNamespace(**{ext: f'{base}.{ext}' for ext in imaging.FORMATS})

    # Template access: slide.desktop.avif, slide.mobile.jpg, ...
    @property
    def desktop(self):
        return self._urls('', 'desktop')

    @property
    def mobile(self):
        return self._urls('', 'mobile')

    @property
    def desktop_ar(self):
        return self._urls('-ar', 'desktop')

    @property
    def mobile_ar(self):
        return self._urls('-ar', 'mobile')

    def clean(self):
        errors = {}
        for field, (_, _, _, ratio) in VARIANT_FIELDS.items():
            f = getattr(self, field)
            if not f or not ratio:
                continue
            width, height = get_image_dimensions(f)
            if width and abs(width / height - ratio) / ratio > RATIO_TOLERANCE:
                errors[field] = f'Wrong shape ({width} x {height}). Expected a width/height ratio of about {ratio:.2f}.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        old = Slide.objects.filter(pk=self.pk).first() if self.pk else None
        super().save(*args, **kwargs)
        if old and old.slug != self.slug:
            self._remove_variants(old.slug)
        for field, (suffix, kind, width, _) in VARIANT_FIELDS.items():
            f = getattr(self, field)
            stem = self._stem(self.slug, suffix, kind)
            if not f:
                imaging.remove_variants(stem)
                continue
            changed = old is None or getattr(old, field).name != f.name or old.slug != self.slug
            if changed or not imaging.variants_exist(stem):
                imaging.make_variants(f.path, stem, width)

    @classmethod
    def _remove_variants(cls, slug):
        for suffix, kind, _, _ in VARIANT_FIELDS.values():
            imaging.remove_variants(cls._stem(slug, suffix, kind))


@receiver(post_delete, sender=Slide)
def _delete_slide_files(sender, instance, **kwargs):
    sender._remove_variants(instance.slug)
