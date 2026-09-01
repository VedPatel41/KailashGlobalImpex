from django.http import HttpResponsePermanentRedirect
from django.conf import settings


class DomainMigrationMiddleware:
    """
    SEO Domain Migration & Canonical Host Redirect Middleware.
    
    1. Permanently redirects (HTTP 301) all legacy domain requests (e.g. vedop.fun, www.vedop.fun)
       to their exact matching path on https://kailashglobalimpex.com.
    2. Permanently redirects (HTTP 301) alternative hosts (e.g. www.kailashglobalimpex.com)
       to the canonical preferred host (https://kailashglobalimpex.com) to eliminate duplicate content issues.
    3. Preserves all query parameters and path structures for seamless 301 link equity transfer.
    4. Automatically bypasses local development and internal testing hosts (localhost, 127.0.0.1, testserver).
    """

    CANONICAL_HOST = 'kailashglobalimpex.com'
    LEGACY_OR_ALIAS_HOSTS = {
        'vedop.fun',
        'www.vedop.fun',
        'www.kailashglobalimpex.com',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()

        if host in self.LEGACY_OR_ALIAS_HOSTS:
            canonical_url = f"https://{self.CANONICAL_HOST}{request.get_full_path()}"
            return HttpResponsePermanentRedirect(canonical_url)

        return self.get_response(request)
