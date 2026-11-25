from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from landingpage.models import PageSeo, Slide
from landingpage.views import PAGE

SRC = Path(__file__).resolve().parents[2] / 'static' / 'img' / 'carousel'

SLIDES = [
    {'slug': 'family-healthcare-makkah',
     'alt': 'Comprehensive Healthcare Under One Roof - multi-specialty consultations, laboratory, imaging and pharmacy at Safa Makkah Polyclinic 2 in Makkah',
     'alt_ar': 'رعاية صحية شاملة تحت سقف واحد - استشارات متعددة التخصصات ومختبر وأشعة وصيدلية في عيادات صفا مكة بمكة المكرمة'},
    {'slug': 'iqama-baladiya-medical-center-makkah',
     'alt': 'Iqama and Baladiya Medical Center - complete medical fitness services in Makkah at Safa Makkah Polyclinic 2',
     'alt_ar': 'مركز الإقامة والبلدية الطبي - خدمات الفحوصات الطبية الشاملة في مكة المكرمة لدى عيادات صفا مكة'},
    {'slug': 'senior-doctors-makkah',
     'alt': 'Well Experienced Senior Doctors with 20+ years of experience - orthopedics, internal medicine, dental care and general practice in Makkah',
     'alt_ar': 'أطباء استشاريون ذوو خبرة عالية - جراحة العظام والطب الباطني وطب الأسنان والرعاية الطبية العامة في مكة المكرمة'},
]


class Command(BaseCommand):
    help = 'Create the home page SEO row and the three launch slides (skips slides that already exist).'

    def handle(self, *args, **options):
        page, _ = PageSeo.objects.get_or_create(key='home', defaults={
            'path': '/', 'title': PAGE['title'], 'description': PAGE['description'], 'h1': PAGE['h1'],
        })
        for order, data in enumerate(SLIDES, start=1):
            slug = data['slug']
            if Slide.objects.filter(slug=slug).exists():
                self.stdout.write(f'skip {slug}')
                continue
            slide = Slide(page=page, order=order, slug=slug, alt=data['alt'], alt_ar=data['alt_ar'])
            for field, suffix in (('desktop_image', '-desktop'), ('mobile_image', '-mobile'),
                                  ('desktop_image_ar', '-ar-desktop'), ('mobile_image_ar', '-ar-mobile')):
                src = SRC / f'{slug}{suffix}.jpg'
                getattr(slide, field).save(f'{slug}{suffix}.jpg', ContentFile(src.read_bytes()), save=False)
            slide.save()
            self.stdout.write(f'added {slug}')
