import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils import timezone
from .models import Product, Inquiry, Certificate
from .forms import InquiryForm

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
    """Homepage with hero, intro, authentic products, approach, trade visual, and inquiry form."""
    products = Product.objects.filter(is_active=True).order_by('display_order', 'name')
    form = InquiryForm()
    context = {
        'page_title': 'Connecting Markets, Delivering Excellence | Kailash Global Impex',
        'meta_description': 'Kailash Global Impex is an international B2B agricultural export company based in Gujarat, India, specializing in Raw Tobacco Leaf and Moringa Leaf Powder sourcing.',
        'products': products,
        'form': form,
        'canonical_url': request.build_absolute_uri(reverse('core:home')),
    }
    return render(request, 'core/home.html', context)


def about(request):
    """About page detailing corporate profile, vision, mission, and leadership (Partners)."""
    context = {
        'page_title': 'About Us | Kailash Global Impex — Authentic Indian Agricultural Sourcing',
        'meta_description': 'Learn about Kailash Global Impex, our agricultural export foundations in Visnagar, Gujarat, and our leadership partners Henil Patel and Nihar Patel.',
        'canonical_url': request.build_absolute_uri(reverse('core:about')),
    }
    return render(request, 'core/about.html', context)


def product_list(request):
    """Product catalog page."""
    products = Product.objects.filter(is_active=True).order_by('display_order', 'name')
    context = {
        'page_title': 'Export Products | Kailash Global Impex',
        'meta_description': 'Explore export-grade agricultural products from India: Premium Raw Tobacco Leaf and Pure Moringa Leaf Powder for global commercial buyers.',
        'products': products,
        'canonical_url': request.build_absolute_uri(reverse('core:product_list')),
    }
    return render(request, 'core/product_list.html', context)


def product_detail(request, slug):
    """Product detail page with authentic sourcing and specification guidelines."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    other_products = Product.objects.filter(is_active=True).exclude(id=product.id)
    
    context = {
        'product': product,
        'other_products': other_products,
        'page_title': f'{product.name} | Sourcing & Export — Kailash Global Impex',
        'meta_description': product.short_description or f'Authentic Indian {product.name} exported worldwide by Kailash Global Impex according to buyer specifications.',
        'canonical_url': request.build_absolute_uri(reverse('core:product_detail', args=[product.slug])),
    }
    return render(request, 'core/product_detail.html', context)


def our_approach(request):
    """Our Approach page highlighting the 3-pillar philosophy: Source Right, Match Requirements, Deliver Reliably."""
    context = {
        'page_title': 'Our Approach | Kailash Global Impex',
        'meta_description': 'Source Right. Match Requirements. Deliver Reliably. Discover our disciplined B2B agricultural export methodology.',
        'canonical_url': request.build_absolute_uri(reverse('core:our_approach')),
    }
    return render(request, 'core/our_approach.html', context)


def certificates(request):
    """Quality & Compliance page with intentional Coming Soon state or active certs."""
    active_certificates = Certificate.objects.filter(is_active=True).order_by('-created_at')
    context = {
        'page_title': 'Certificates & Compliance | Kailash Global Impex',
        'meta_description': 'Quality and compliance documentation for agricultural exports at Kailash Global Impex.',
        'certificates': active_certificates,
        'has_certificates': active_certificates.exists(),
        'canonical_url': request.build_absolute_uri(reverse('core:certificates')),
    }
    return render(request, 'core/certificates.html', context)


def contact(request):
    """Contact page with verified communication channels and full inquiry form."""
    product_param = request.GET.get('product', '').strip()
    initial_data = {}
    
    # Map slug or query text to exact product choices
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
        'page_title': 'Contact & Commercial Inquiries | Kailash Global Impex',
        'meta_description': 'Get in touch with Kailash Global Impex in Visnagar, Gujarat, India for bulk trade inquiries, commercial pricing, and shipping schedules.',
        'form': form,
        'selected_product': initial_data.get('product', ''),
        'canonical_url': request.build_absolute_uri(reverse('core:contact')),
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
    """Dynamic robots.txt view."""
    domain = request.build_absolute_uri('/')[:-1]
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /admin-panel/

Sitemap: {domain}/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    """Dynamic XML sitemap view."""
    domain = request.build_absolute_uri('/')[:-1]
    now = timezone.now().strftime('%Y-%m-%d')
    
    static_urls = [
        {'loc': f"{domain}/", 'priority': '1.0', 'changefreq': 'weekly'},
        {'loc': f"{domain}/about/", 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': f"{domain}/products/", 'priority': '0.9', 'changefreq': 'weekly'},
        {'loc': f"{domain}/our-approach/", 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': f"{domain}/certificates/", 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': f"{domain}/contact/", 'priority': '0.8', 'changefreq': 'monthly'},
    ]
    
    product_urls = []
    for p in Product.objects.filter(is_active=True):
        product_urls.append({
            'loc': f"{domain}/products/{p.slug}/",
            'priority': '0.9',
            'changefreq': 'weekly',
            'lastmod': p.updated_at.strftime('%Y-%m-%d')
        })

    xml_entries = []
    for item in static_urls:
        xml_entries.append(f"""  <url>
    <loc>{item['loc']}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>{item['changefreq']}</changefreq>
    <priority>{item['priority']}</priority>
  </url>""")

    for item in product_urls:
        xml_entries.append(f"""  <url>
    <loc>{item['loc']}</loc>
    <lastmod>{item['lastmod']}</lastmod>
    <changefreq>{item['changefreq']}</changefreq>
    <priority>{item['priority']}</priority>
  </url>""")

    xml_body = "\n".join(xml_entries)
    full_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{xml_body}
</urlset>"""
    return HttpResponse(full_xml, content_type="application/xml")


def custom_404(request, exception=None):
    """Branded 404 Not Found error page."""
    return render(request, 'errors/404.html', {'page_title': 'Page Not Found | Kailash Global Impex'}, status=404)


def custom_500(request):
    """Branded 500 Server Error page."""
    return render(request, 'errors/500.html', {'page_title': 'Server Error | Kailash Global Impex'}, status=500)
