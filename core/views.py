import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils import timezone
from django.contrib.sitemaps.views import sitemap as django_sitemap_view
from .models import Product, Inquiry, Certificate
from .forms import InquiryForm
from .sitemaps import sitemaps

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP address from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def home(request):
    """Homepage with hero, authentic products, approach, trade visual, and inquiry CTA."""
    products = Product.objects.filter(is_active=True).order_by('display_order', 'name')
    form = InquiryForm()
    context = {
        'page_title': 'Kailash Global Impex | B2B Agricultural Export Enterprise India',
        'meta_description': 'Kailash Global Impex is an international B2B agricultural export enterprise based in Visnagar, Gujarat, India. Sourcing and exporting Raw Tobacco Leaf and Moringa Leaf Powder.',
        'products': products,
        'form': form,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """About page detailing corporate profile, vision, mission, and leadership partners."""
    context = {
        'page_title': 'About Us | Kailash Global Impex — Agricultural Exporter Gujarat India',
        'meta_description': 'Learn about Kailash Global Impex, our Indian agricultural sourcing foundations in Visnagar, Gujarat, and our leadership partners Henil Patel and Nihar Patel.',
    }
    return render(request, 'core/about.html', context)


def product_list(request):
    """Product catalog page."""
    products = Product.objects.filter(is_active=True).order_by('display_order', 'name')
    context = {
        'page_title': 'Agricultural Export Products | Kailash Global Impex',
        'meta_description': 'Explore export-grade agricultural commodities from India by Kailash Global Impex: Premium Raw Tobacco Leaf and Pure Moringa Leaf Powder for commercial buyers.',
        'products': products,
    }
    return render(request, 'core/product_list.html', context)


def product_detail(request, slug):
    """Product detail page with authentic sourcing and specification guidelines."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    other_products = Product.objects.filter(is_active=True).exclude(id=product.id)
    
    meta_desc = product.short_description
    if not meta_desc or len(meta_desc) < 30:
        meta_desc = f'{product.name} ({product.botanical_name or "Agricultural Commodity"}) exported from India by Kailash Global Impex. Sourced to buyer specifications and commercial grading.'
    
    context = {
        'product': product,
        'other_products': other_products,
        'page_title': f'{product.name} Export from India | Kailash Global Impex',
        'meta_description': meta_desc,
    }
    return render(request, 'core/product_detail.html', context)


def our_approach(request):
    """Our Approach page highlighting the 3-pillar philosophy: Source Right, Match Requirements, Deliver Reliably."""
    context = {
        'page_title': 'Our Sourcing Approach | Kailash Global Impex',
        'meta_description': 'Source Right. Match Requirements. Deliver Reliably. Discover the 3-pillar agricultural sourcing and export methodology of Kailash Global Impex.',
    }
    return render(request, 'core/our_approach.html', context)


def certificates(request):
    """Quality & Compliance page with intentional Coming Soon state or active certs."""
    active_certificates = Certificate.objects.filter(is_active=True).order_by('-created_at')
    context = {
        'page_title': 'Quality Standards & Compliance | Kailash Global Impex',
        'meta_description': 'Export quality standards, destination compliance documentation, and agricultural certification guidelines at Kailash Global Impex.',
        'certificates': active_certificates,
        'has_certificates': active_certificates.exists(),
    }
    return render(request, 'core/certificates.html', context)


def contact(request):
    """Contact page with verified communication channels and full inquiry form."""
    product_param = request.GET.get('product', '').strip()
    initial_data = {}
    
    slug_map = {
        'raw-tobacco-leaf': 'Raw Tobacco Leaf',
        'tobacco': 'Raw Tobacco Leaf',
        'moringa-leaf-powder': 'Moringa Leaf Powder',
        'moringa': 'Moringa Leaf Powder',
    }
    
    if product_param:
        if product_param in slug_map:
            initial_data['product'] = slug_map[product_param]
        elif product_param in [c[0] for c in Inquiry.PRODUCT_CHOICES]:
            initial_data['product'] = product_param

    form = InquiryForm(initial=initial_data)
    context = {
        'page_title': 'Contact Trade Desk | Kailash Global Impex Visnagar Gujarat',
        'meta_description': 'Contact Kailash Global Impex in Visnagar, Gujarat, India. Submit commercial trade inquiries for bulk agricultural commodity exports.',
        'form': form,
        'selected_product': initial_data.get('product', ''),
    }
    return render(request, 'core/contact.html', context)


@require_POST
def submit_inquiry(request):
    """
    Handles B2B inquiry form submissions.
    Supports both AJAX JSON requests and traditional POST submissions.
    Saves inquiry to DB first, then attempts notification email fail-safely.
    """
    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        'application/json' in request.headers.get('Accept', '') or
        request.POST.get('is_ajax') == '1'
    )
    
    form = InquiryForm(request.POST)
    if form.is_valid():
        inquiry = form.save(commit=False)
        inquiry.ip_address = get_client_ip(request)
        inquiry.save()

        # Send notification email if configured (fail-silently to prevent losing inquiry)
        try:
            subject = f"[New Trade Inquiry] {inquiry.product} - {inquiry.name} ({inquiry.country})"
            message_body = (
                f"New Commercial Inquiry Received on Website:\n\n"
                f"Name: {inquiry.name}\n"
                f"Email: {inquiry.email}\n"
                f"Company: {inquiry.company_name or 'Not specified'}\n"
                f"Mobile: {inquiry.mobile_number}\n"
                f"Country: {inquiry.country}\n"
                f"Product: {inquiry.product}\n"
                f"Requirements / Quantity: {inquiry.product_details or 'None'}\n"
                f"Remarks: {inquiry.remarks or 'None'}\n"
                f"Received At: {timezone.now().strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
                f"IP: {inquiry.ip_address}\n\n"
                f"View in CRM: {request.build_absolute_uri(reverse('admin_panel:inquiry_detail', args=[inquiry.id]))}"
            )
            send_mail(
                subject=subject,
                message=message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[getattr(settings, 'COMPANY_NOTIFICATION_EMAIL', 'kailashglobalimpex@gmail.com')],
                fail_silently=True,
            )
        except Exception as exc:
            logger.warning(f"Failed to dispatch inquiry notification email: {exc}")

        success_msg = "Thank you! Your inquiry has been submitted successfully. Our trade desk will review your requirements and respond promptly."
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': success_msg,
                'inquiry_id': inquiry.id,
            })
        messages.success(request, success_msg)
        return redirect(request.META.get('HTTP_REFERER', reverse('core:home')) + '#inquiry-success')

    else:
        error_msg = "Please verify your input fields. " + " ".join([
            f"{field.replace('_', ' ').capitalize()}: {', '.join(errs)}"
            for field, errs in form.errors.items() if field != 'website_url'
        ])
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': error_msg,
            }, status=400)
        messages.error(request, error_msg)
        return redirect(request.META.get('HTTP_REFERER', reverse('core:contact')))


def robots_txt(request):
    """Dynamic robots.txt view ensuring Googlebot compatibility and correct sitemap reference."""
    host = request.get_host()
    scheme = 'https' if not settings.DEBUG else request.scheme
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /admin-panel/

Sitemap: {scheme}://{host}/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


def sitemap_xml(request):
    """
    Standard XML sitemap view powered by django.contrib.sitemaps.
    Returns compliant XML sitemap for search engine crawlers.
    """
    return django_sitemap_view(request, sitemaps=sitemaps)


def custom_404(request, exception=None):
    """Branded 404 Not Found error page."""
    return render(request, 'errors/404.html', {'page_title': 'Page Not Found | Kailash Global Impex'}, status=404)


def custom_500(request):
    """Branded 500 Server Error page."""
    return render(request, 'errors/500.html', {'page_title': 'Server Error | Kailash Global Impex'}, status=500)
