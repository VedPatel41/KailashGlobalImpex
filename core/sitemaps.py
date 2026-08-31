"""
Django sitemap definitions for Kailash Global Impex.
Exposes only canonical, public, indexable pages on https://vedop.fun.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product


class CanonicalSite:
    """Production canonical site reference for sitemap URL generation."""
    domain = 'vedop.fun'
    name = 'Kailash Global Impex'


class CanonicalSitemap(Sitemap):
    """
    Base sitemap enforcing HTTPS protocol and production canonical domain (vedop.fun).
    """
    protocol = 'https'

    def get_urls(self, page=1, site=None, protocol=None):
        return super().get_urls(page=page, site=CanonicalSite(), protocol='https')


class StaticViewSitemap(CanonicalSitemap):
    """
    Sitemap for public static institutional and marketing pages.
    """
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


class ProductSitemap(CanonicalSitemap):
    """
    Dynamic sitemap for active, publicly cataloged commodity products.
    """
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

