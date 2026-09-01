from django.http import HttpResponsePermanentRedirect


class LegacyDomainRedirectMiddleware:
    """
    SEO Domain Migration Middleware.

    Permanently redirects (HTTP 301) all incoming requests from legacy domains
    ('vedop.fun' and 'www.vedop.fun') to the equivalent URL on the new canonical
    production domain ('https://kailashglobalimpex.com'), preserving full path
    and query string parameters.

    Render & SEO Safety:
    - Strictly acts ONLY when the incoming Host header matches 'vedop.fun' or 'www.vedop.fun'.
    - NEVER redirects 'kailashglobalimpex.com', 'www.kailashglobalimpex.com', or 'onrender.com'.
    - NEVER creates application-level redirects between www and apex.
    - Prevents redirect loops with reverse proxy or DNS routing.
    """

    TARGET_DOMAIN = "https://kailashglobalimpex.com"
    LEGACY_HOSTS = ("vedop.fun", "www.vedop.fun")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0].lower()

        if host in self.LEGACY_HOSTS:
            target_url = f"{self.TARGET_DOMAIN}{request.get_full_path()}"
            return HttpResponsePermanentRedirect(target_url)

        return self.get_response(request)
