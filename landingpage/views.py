import json
from datetime import date

from django.conf import settings
from django.shortcuts import render

# Single source of truth for NAP and content. All values are TODO placeholders
# until the open questions in the spec (section 13) are answered.
SITE = {
    'name': 'Safa Makkah Polyclinic 2',
    'brand_name': 'Safa Makkah Polyclinic - 2',
    'city': 'Makkah',
    'country': 'Saudi Arabia',
    'country_code': 'SA',
    'street': 'TODO Street Address',
    'region': 'Makkah Province',
    'postal_code': '00000',
    'phone': '+966 00 000 0000',
    'phone_href': '+966000000000',
    'email': 'info@example.com',
    'geo': {'lat': '21.4225', 'lng': '39.8262'},
    'hours': [
        {'label': 'Saturday - Thursday', 'text': '9:00 AM - 11:00 PM',
         'days': ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'],
         'opens': '09:00', 'closes': '23:00'},
        {'label': 'Friday', 'text': '4:00 PM - 11:00 PM',
         'days': ['Friday'], 'opens': '16:00', 'closes': '23:00'},
    ],
    'gbp_url': 'https://www.google.com/maps?cid=TODO',
    'map_embed_url': 'https://www.google.com/maps?q=21.4225,39.8262&output=embed',
    'directions_url': 'https://www.google.com/maps/dir/?api=1&destination=21.4225,39.8262',
    'social': [
        {'name': 'Facebook', 'url': '#'},
        {'name': 'Instagram', 'url': '#'},
        {'name': 'X (Twitter)', 'url': '#'},
    ],
    'services': [
        {'name': 'General Medicine', 'text': 'TODO: describe general medicine and family doctor consultations at the clinic in Makkah.'},
        {'name': 'Pediatrics', 'text': 'TODO: describe pediatric care, vaccinations and child health checks in Makkah.'},
        {'name': 'Dentistry', 'text': 'TODO: describe dental check-ups, fillings and cosmetic dentistry in Makkah.'},
        {'name': 'Dermatology', 'text': 'TODO: describe skin, hair and nail treatments offered in Makkah.'},
        {'name': 'Obstetrics and Gynecology', 'text': 'TODO: describe womens health, antenatal and gynecology services in Makkah.'},
        {'name': 'Laboratory and Radiology', 'text': 'TODO: describe in-house lab tests and imaging services in Makkah.'},
    ],
    'doctors': [
        {'name': 'Dr. TODO Name One', 'specialty': 'General Medicine', 'bio': 'TODO: qualifications, experience and languages spoken.', 'photo': 'img/doctors/doctor-1-general-medicine.jpg'},
        {'name': 'Dr. TODO Name Two', 'specialty': 'Pediatrics', 'bio': 'TODO: qualifications, experience and languages spoken.', 'photo': 'img/doctors/doctor-2-pediatrics.jpg'},
        {'name': 'Dr. TODO Name Three', 'specialty': 'Dentistry', 'bio': 'TODO: qualifications, experience and languages spoken.', 'photo': 'img/doctors/doctor-3-dentistry.jpg'},
    ],
    'insurers': [
        {'name': 'TODO Insurer One'},
        {'name': 'TODO Insurer Two'},
        {'name': 'TODO Insurer Three'},
        {'name': 'TODO Insurer Four'},
    ],
    'packages': [
        {'name': 'Basic Health Check-up', 'items': ['Physical examination', 'Blood count', 'Blood sugar', 'Cholesterol'], 'price': 'TODO'},
        {'name': 'Comprehensive Check-up', 'items': ['Everything in Basic', 'Liver and kidney function', 'ECG', 'Chest X-ray'], 'price': 'TODO'},
        {'name': 'Executive Check-up', 'items': ['Everything in Comprehensive', 'Thyroid profile', 'Vitamin D and B12', 'Specialist consultation'], 'price': 'TODO'},
    ],
    'testimonials': [
        {'quote': 'TODO: real patient review goes here.', 'author': 'TODO Patient A'},
        {'quote': 'TODO: real patient review goes here.', 'author': 'TODO Patient B'},
        {'quote': 'TODO: real patient review goes here.', 'author': 'TODO Patient C'},
    ],
    'faq': [
        {'q': 'What are the clinic opening hours?', 'a': 'TODO: Safa Makkah Polyclinic 2 is open Saturday to Thursday and on Friday evenings. Confirm the exact hours in the footer and contact section before publishing.'},
        {'q': 'Do I need an appointment to see a doctor?', 'a': 'TODO: explain whether walk-ins are accepted and how patients can book by phone.'},
        {'q': 'Which insurance providers do you accept?', 'a': 'TODO: list accepted insurers and explain how claims and pre-approvals work at the clinic.'},
        {'q': 'Where is the clinic located in Makkah?', 'a': 'TODO: describe the location, nearby landmarks and parking so patients can find the clinic easily.'},
        {'q': 'Do you offer health check-up packages?', 'a': 'TODO: describe the available packages, what each includes and how long results take.'},
        {'q': 'Are Arabic and English speaking doctors available?', 'a': 'TODO: list the languages spoken by the medical team.'},
    ],
    'slides': [
        {'key': 'slide-1', 'file': 'family-healthcare-makkah',
         'alt': 'Trusted Family Healthcare in Makkah - polyclinic and family doctors at Safa Makkah Polyclinic 2'},
        {'key': 'slide-2', 'file': 'specialist-doctors-makkah',
         'alt': 'Experienced Doctors, Every Specialty - specialist doctors in Makkah at Safa Makkah Polyclinic 2'},
        {'key': 'slide-3', 'file': 'health-checkup-packages-makkah',
         'alt': 'Health Check-up Packages in Makkah - full body check-up at Safa Makkah Polyclinic 2'},
    ],
}

PAGE = {
    'title': 'Polyclinic in Makkah | Safa Makkah Polyclinic 2',
    'description': 'Safa Makkah Polyclinic 2: doctors, dental, pediatrics and health check-ups in Makkah. Insurance accepted. Call or visit us today.',
    'h1': 'Safa Makkah Polyclinic 2: trusted polyclinic and family doctors in Makkah',
}


def _jsonld(data):
    # Escape "</" so the payload can never close the script tag.
    return json.dumps(data, ensure_ascii=False, indent=2).replace('</', '<\\/')


def _build_jsonld(base_url):
    s = SITE
    clinic = {
        '@context': 'https://schema.org',
        '@type': ['MedicalClinic', 'LocalBusiness'],
        '@id': f'{base_url}/#clinic',
        'name': s['name'],
        'url': f'{base_url}/',
        'logo': f'{base_url}/static/img/logo/safa-makkah-polyclinic-2-logo.svg',
        'image': f'{base_url}/static/img/og/og-share-1200x630.jpg',
        'telephone': s['phone'],
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': s['street'],
            'addressLocality': s['city'],
            'addressRegion': s['region'],
            'postalCode': s['postal_code'],
            'addressCountry': s['country_code'],
        },
        'geo': {'@type': 'GeoCoordinates', 'latitude': s['geo']['lat'], 'longitude': s['geo']['lng']},
        'openingHoursSpecification': [
            {'@type': 'OpeningHoursSpecification', 'dayOfWeek': h['days'], 'opens': h['opens'], 'closes': h['closes']}
            for h in s['hours']
        ],
        'areaServed': s['city'],
        'medicalSpecialty': [d['specialty'] for d in s['doctors']],
        'sameAs': [s['gbp_url']] + [x['url'] for x in s['social'] if x['url'] != '#'],
    }
    physicians = [
        {
            '@context': 'https://schema.org',
            '@type': 'Physician',
            'name': d['name'],
            'medicalSpecialty': d['specialty'],
            'image': f"{base_url}/static/{d['photo']}",
            'worksFor': {'@id': f'{base_url}/#clinic'},
        }
        for d in s['doctors']
    ]
    faq = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {'@type': 'Question', 'name': f['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': f['a']}}
            for f in s['faq']
        ],
    }
    return [_jsonld(clinic)] + [_jsonld(p) for p in physicians] + [_jsonld(faq)]


def index(request):
    base_url = settings.SITE_DOMAIN.rstrip('/')
    context = {
        'site': SITE,
        'page': PAGE,
        'base_url': base_url,
        'canonical_url': f'{base_url}/',
        'lang': 'en',
        'dir': 'ltr',
        'ga_id': settings.GA_MEASUREMENT_ID,
        'jsonld_blocks': _build_jsonld(base_url),
    }
    return render(request, 'index.html', context)


def robots_txt(request):
    base_url = settings.SITE_DOMAIN.rstrip('/')
    return render(request, 'robots.txt', {'base_url': base_url}, content_type='text/plain')


def sitemap_xml(request):
    base_url = settings.SITE_DOMAIN.rstrip('/')
    return render(request, 'sitemap.xml', {'base_url': base_url, 'lastmod': date.today().isoformat()},
                  content_type='application/xml')
