from django.utils import timezone
from .models import Product

CANONICAL_DOMAIN = 'https://kailashglobalimpex.com'


def company_context(request):
    """
    Global context processor supplying authentic corporate identity,
    verified contact channels, canonical SEO domains, and navigation items.
    """
    try:
        global_products = Product.objects.filter(is_active=True).order_by('display_order', 'name')
    except Exception:
        global_products = []

    # Guaranteed canonical production URL pointing to https://kailashglobalimpex.com
    canonical_url = f"{CANONICAL_DOMAIN}{request.path}"

    return {
        'COMPANY_NAME': 'Kailash Global Impex',
        'COMPANY_TAGLINE': 'Connecting Markets, Delivering Excellence',
        'COMPANY_EMAIL': 'info@kailashglobalimpex.com',
        'COMPANY_PHONES': [
            {'display': '+91 9773140138', 'clean': '+919773140138', 'is_primary': True},
            {'display': '+91 73833 11112', 'clean': '+917383311112', 'is_primary': False},
        ],
        'COMPANY_ADDRESS': 'Visnagar, Mehsana, Gujarat, India - 384315',
        'COMPANY_CITY': 'Visnagar',
        'COMPANY_DISTRICT': 'Mehsana',
        'COMPANY_STATE': 'Gujarat',
        'COMPANY_COUNTRY': 'India',
        'COMPANY_PINCODE': '384315',
        'COMPANY_INSTAGRAM': 'https://www.instagram.com/kailashglobalimpex/',
        'COMPANY_LINKEDIN': 'https://www.linkedin.com/company/kailash-global-impex/',
        'GLOBAL_PRODUCTS': global_products,
        'LEADERSHIP_PARTNERS': [
            {
                'name': 'Henil Patel',
                'title': 'Partner',
                'image_webp': 'images/founders/henil-patel.webp',
                'image_png': 'images/founders/henil-patel.png',
            },
            {
                'name': 'Nihar Patel',
                'title': 'Partner',
                'image_webp': 'images/founders/nihar-patel.webp',
                'image_jpeg': 'images/founders/nihar-patel.jpeg',
            },
        ],
        'CURRENT_YEAR': timezone.now().year,
        'SITE_DOMAIN': request.build_absolute_uri('/')[:-1],
        'CANONICAL_DOMAIN': CANONICAL_DOMAIN,
        'canonical_url': canonical_url,
    }

