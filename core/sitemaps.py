"""
Django sitemap definitions for Kailash Global Impex.
Exposes only canonical, public, indexable pages.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product


class StaticViewSitemap(Sitemap):
    """
    Sitemap for public static institutional and marketing pages.
    """
    protocol = 'https'

    PAGE_CONFIG = {
        'core:home': {'priority': 1.0, 'changefreq': 'weekly'},
        'core:about': {'priority': 0.8, 'changefreq': 'monthly'},
        'core:product_list': {'priority': 0.9, 'changefreq': 'weekly'},
        'core:our_approach': {'priority': 0.8, 'changefreq': 'monthly'},
        'core:certificates': {'priority': 0.7, 'changefreq': 'monthly'},
        'core:contact': {'priority': 0.8, 'changefreq': 'monthly'},
    }

    def items(self):
        return list(self.PAGE_CONFIG.keys())

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.PAGE_CONFIG.get(item, {}).get('priority', 0.8)

    def changefreq(self, item):
        return self.PAGE_CONFIG.get(item, {}).get('changefreq', 'monthly')


class ProductSitemap(Sitemap):
    """
    Dynamic sitemap for active, publicly cataloged commodity products.
    """
    protocol = 'https'
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return Product.objects.filter(is_active=True).order_by('display_order', 'name')

    def location(self, item):
        return reverse('core:product_detail', args=[item.slug])

    def lastmod(self, item):
        return item.updated_at


sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
}
