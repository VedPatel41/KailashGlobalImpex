import csv
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from core.models import Inquiry, Product, Certificate
from .forms import AdminLoginForm, InquiryUpdateForm, ProductForm, CertificateForm


def is_staff_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def admin_login(request):
    """Custom branded CRM login view."""
    if request.user.is_authenticated and is_staff_user(request.user):
        return redirect('admin_panel:dashboard')

    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                next_url = request.GET.get('next') or 'admin_panel:dashboard'
                return redirect(next_url)
            else:
                messages.error(request, "Access restricted. Staff administrator privileges required.")
        else:
            messages.error(request, "Invalid username or password. Please check your credentials.")
    else:
        form = AdminLoginForm()

    return render(request, 'admin_panel/login.html', {
        'form': form,
        'page_title': 'Trade Portal Login | Kailash Global Impex CRM',
    })


def admin_logout(request):
    """Custom CRM logout view."""
    logout(request)
    messages.info(request, "You have been logged out securely.")
    return redirect('admin_panel:login')


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def dashboard(request):
    """Custom CRM executive dashboard."""
    total_inquiries = Inquiry.objects.count()
    new_inquiries = Inquiry.objects.filter(status=Inquiry.STATUS_NEW).count()
    read_inquiries = Inquiry.objects.filter(status=Inquiry.STATUS_READ).count()
    contacted_inquiries = Inquiry.objects.filter(status=Inquiry.STATUS_CONTACTED).count()
    closed_inquiries = Inquiry.objects.filter(status=Inquiry.STATUS_CLOSED).count()

    recent_inquiries = Inquiry.objects.all().order_by('-created_at')[:8]
    
    last_30_days = timezone.now() - timedelta(days=30)
    inquiries_last_30 = Inquiry.objects.filter(created_at__gte=last_30_days).count()

    product_stats = (
        Inquiry.objects.values('product')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    products_list = Product.objects.all().order_by('display_order', 'name')
    total_certificates = Certificate.objects.count()
    active_certificates = Certificate.objects.filter(is_active=True).count()
    certificates_list = Certificate.objects.all().order_by('-created_at')[:4]

    context = {
        'page_title': 'Executive Trade Dashboard | Kailash Global Impex CRM',
        'total_inquiries': total_inquiries,
        'new_inquiries': new_inquiries,
        'read_inquiries': read_inquiries,
        'contacted_inquiries': contacted_inquiries,
        'closed_inquiries': closed_inquiries,
        'inquiries_last_30': inquiries_last_30,
        'recent_inquiries': recent_inquiries,
        'product_stats': product_stats,
        'total_products': total_products,
        'active_products': active_products,
        'products_list': products_list,
        'total_certificates': total_certificates,
        'active_certificates': active_certificates,
        'certificates_list': certificates_list,
        'active_menu': 'dashboard',
    }
    return render(request, 'admin_panel/dashboard.html', context)


# =========================================================================
# INQUIRY MANAGEMENT
# =========================================================================

@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def inquiries_list(request):
    """Inquiry management table with search, product, status, and date filtering."""
    queryset = Inquiry.objects.all()

    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) |
            Q(email__icontains=q) |
            Q(company_name__icontains=q) |
            Q(country__icontains=q) |
            Q(mobile_number__icontains=q) |
            Q(product_details__icontains=q) |
            Q(remarks__icontains=q)
        )

    status_filter = request.GET.get('status', '').strip()
    if status_filter in [Inquiry.STATUS_NEW, Inquiry.STATUS_READ, Inquiry.STATUS_CONTACTED, Inquiry.STATUS_CLOSED]:
        queryset = queryset.filter(status=status_filter)

    product_filter = request.GET.get('product', '').strip()
    if product_filter:
        queryset = queryset.filter(product=product_filter)

    date_filter = request.GET.get('date_range', '').strip()
    now = timezone.now()
    if date_filter == 'today':
        queryset = queryset.filter(created_at__date=now.date())
    elif date_filter == '7days':
        queryset = queryset.filter(created_at__gte=now - timedelta(days=7))
    elif date_filter == '30days':
        queryset = queryset.filter(created_at__gte=now - timedelta(days=30))

    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['-created_at', 'created_at', 'name', '-name', 'company_name', 'status']
    if sort_by in valid_sorts:
        queryset = queryset.order_by(sort_by)
    else:
        queryset = queryset.order_by('-created_at')

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Trade Inquiries CRM | Kailash Global Impex',
        'inquiries': page_obj,
        'page_obj': page_obj,
        'total_count': paginator.count,
        'q': q,
        'selected_status': status_filter,
        'selected_product': product_filter,
        'selected_date_range': date_filter,
        'selected_sort': sort_by,
        'status_choices': Inquiry.STATUS_CHOICES,
        'product_choices': Inquiry.PRODUCT_CHOICES,
        'active_menu': 'inquiries',
    }
    return render(request, 'admin_panel/inquiries.html', context)


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def inquiry_detail(request, pk):
    """Detailed view and status/notes updater for a single trade lead."""
    inquiry = get_object_or_404(Inquiry, pk=pk)

    if inquiry.status == Inquiry.STATUS_NEW:
        inquiry.status = Inquiry.STATUS_READ
        inquiry.save(update_fields=['status', 'updated_at'])

    if request.method == 'POST':
        form = InquiryUpdateForm(request.POST, instance=inquiry)
        if form.is_valid():
            form.save()
            messages.success(request, f"✓ Inquiry #{inquiry.id} updated successfully.")
            return redirect('admin_panel:inquiry_detail', pk=inquiry.pk)
    else:
        form = InquiryUpdateForm(instance=inquiry)

    context = {
        'page_title': f"Inquiry #{inquiry.id} — {inquiry.name} | CRM",
        'inquiry': inquiry,
        'form': form,
        'active_menu': 'inquiries',
    }
    return render(request, 'admin_panel/inquiry_detail.html', context)


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
@require_POST
def update_inquiry_status_ajax(request, pk):
    """Quick inline status updater via AJAX."""
    inquiry = get_object_or_404(Inquiry, pk=pk)
    new_status = request.POST.get('status')
    if new_status in [Inquiry.STATUS_NEW, Inquiry.STATUS_READ, Inquiry.STATUS_CONTACTED, Inquiry.STATUS_CLOSED]:
        inquiry.status = new_status
        inquiry.save(update_fields=['status', 'updated_at'])
        return JsonResponse({
            'success': True,
            'message': f"✓ Status updated to {inquiry.get_status_display()}",
            'new_status': inquiry.status,
            'status_display': inquiry.get_status_display(),
        })
    return JsonResponse({'success': False, 'message': 'Invalid status provided.'}, status=400)


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def inquiry_delete(request, pk):
    """
    Permanently delete an inquiry/feedback record from the database.
    Supports both AJAX POST with JSON response and traditional POST/GET with confirm_delete page.
    """
    inquiry = get_object_or_404(Inquiry, pk=pk)

    if request.method == 'POST':
        inquiry_id = inquiry.id
        inquiry_name = inquiry.name
        inquiry.delete()

        is_ajax = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            'application/json' in request.headers.get('Accept', '')
        )

        success_msg = f"Feedback #{inquiry_id} from {inquiry_name} deleted successfully."
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': success_msg,
                'deleted_id': inquiry_id,
            })

        messages.success(request, success_msg)
        return redirect('admin_panel:inquiries_list')

    return render(request, 'admin_panel/confirm_delete.html', {
        'page_title': f"Delete Feedback #{inquiry.id} | Admin Portal",
        'item_type': 'Feedback',
        'item_name': f"#{inquiry.id} — {inquiry.name} ({inquiry.email})",
        'cancel_url': 'admin_panel:inquiries_list',
        'active_menu': 'inquiries',
    })


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def export_inquiries_csv(request):
    """Export filtered or all inquiries to a formatted CSV."""
    queryset = Inquiry.objects.all().order_by('-created_at')

    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) |
            Q(email__icontains=q) |
            Q(company_name__icontains=q) |
            Q(country__icontains=q)
        )

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    product_filter = request.GET.get('product', '').strip()
    if product_filter:
        queryset = queryset.filter(product=product_filter)

    response = HttpResponse(content_type='text/csv')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="KGI_Inquiries_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Inquiry ID',
        'Date Received',
        'Status',
        'Contact Name',
        'Email Address',
        'Company Name',
        'Mobile Number',
        'Country / Destination',
        'Product of Interest',
        'Requirements / Specifications',
        'Remarks',
        'Internal Admin Notes',
        'IP Address',
    ])

    for item in queryset:
        writer.writerow([
            item.id,
            item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            item.get_status_display(),
            item.name,
            item.email,
            item.company_name or 'N/A',
            item.mobile_number,
            item.country,
            item.product,
            item.product_details.replace('\r', ' ').replace('\n', ' ') if item.product_details else '',
            item.remarks.replace('\r', ' ').replace('\n', ' ') if item.remarks else '',
            item.admin_notes.replace('\r', ' ').replace('\n', ' ') if item.admin_notes else '',
            item.ip_address or '',
        ])

    return response


# =========================================================================
# PRODUCT CMS MANAGEMENT
# =========================================================================

@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def products_view(request):
    """View products catalog in CRM."""
    products = Product.objects.all().order_by('display_order', 'name')
    return render(request, 'admin_panel/products.html', {
        'page_title': 'Products Catalog Management | Kailash Global Impex CRM',
        'products': products,
        'active_menu': 'products',
    })


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def product_add(request):
    """Add new product to the catalog."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            if not product.slug:
                product.slug = slugify(product.name)
            # Ensure unique slug
            orig_slug = product.slug
            counter = 1
            while Product.objects.filter(slug=product.slug).exists():
                product.slug = f"{orig_slug}-{counter}"
                counter += 1
            product.save()
            messages.success(request, f"✓ Product '{product.name}' created successfully.")
            return redirect('admin_panel:products_view')
    else:
        form = ProductForm()

    return render(request, 'admin_panel/product_form.html', {
        'page_title': 'Add New Product | CRM',
        'form': form,
        'action_title': 'Add New Export Product',
        'active_menu': 'products',
    })


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def product_edit(request, pk):
    """Edit product details in CRM."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            if not product.slug:
                product.slug = slugify(product.name)
            product.save()
            messages.success(request, f"✓ Product '{product.name}' updated successfully.")
            return redirect('admin_panel:products_view')
    else:
        form = ProductForm(instance=product)

    return render(request, 'admin_panel/product_form.html', {
        'page_title': f"Edit Product: {product.name} | CRM",
        'product': product,
        'form': form,
        'action_title': f"Edit Product: {product.name}",
        'active_menu': 'products',
    })


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def product_toggle(request, pk):
    """Quick toggle active status for a product."""
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save(update_fields=['is_active'])
    status_str = "Activated" if product.is_active else "Deactivated"
    messages.success(request, f"✓ Product '{product.name}' has been {status_str}.")
    return redirect('admin_panel:products_view')


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def product_delete(request, pk):
    """Safely delete or deactivate a product with confirmation."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f"✓ Product '{product_name}' deleted successfully.")
        return redirect('admin_panel:products_view')

    return render(request, 'admin_panel/confirm_delete.html', {
        'page_title': f"Delete Product: {product.name} | CRM",
        'item_type': 'Product',
        'item_name': product.name,
        'cancel_url': 'admin_panel:products_view',
        'active_menu': 'products',
    })


# =========================================================================
# CERTIFICATE CMS MANAGEMENT
# =========================================================================

@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def certificates_view(request):
    """Manage compliance certificates in CRM."""
    certs = Certificate.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/certificates.html', {
        'page_title': 'Certificates Management | Kailash Global Impex CRM',
        'certificates': certs,
        'active_menu': 'certificates',
    })


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def certificate_add(request):
    """Add new compliance certificate in CRM."""
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save()
            messages.success(request, f"✓ Certificate '{cert.title}' added successfully.")
            return redirect('admin_panel:certificates_view')
    else:
        form = CertificateForm()

    return render(request, 'admin_panel/certificate_form.html', {
        'page_title': 'Add New Certificate | CRM',
        'form': form,
        'action_title': 'Add Compliance Certificate',
        'active_menu': 'certificates',
    })


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def certificate_edit(request, pk):
    """Edit compliance certificate in CRM."""
    cert = get_object_or_404(Certificate, pk=pk)
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES, instance=cert)
        if form.is_valid():
            form.save()
            messages.success(request, f"✓ Certificate '{cert.title}' updated successfully.")
            return redirect('admin_panel:certificates_view')
    else:
        form = CertificateForm(instance=cert)

    return render(request, 'admin_panel/certificate_form.html', {
        'page_title': f'Edit Certificate: {cert.title} | CRM',
        'form': form,
        'cert': cert,
        'action_title': f'Edit Certificate: {cert.title}',
        'active_menu': 'certificates',
    })


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def certificate_toggle(request, pk):
    """Quick toggle active status for a certificate."""
    cert = get_object_or_404(Certificate, pk=pk)
    cert.is_active = not cert.is_active
    cert.save(update_fields=['is_active'])
    status_str = "Published" if cert.is_active else "Unpublished"
    messages.success(request, f"✓ Certificate '{cert.title}' has been {status_str}.")
    return redirect('admin_panel:certificates_view')


@login_required(login_url='admin_panel:login')
@user_passes_test(is_staff_user, login_url='admin_panel:login')
def certificate_delete(request, pk):
    """Safely delete a certificate with confirmation."""
    cert = get_object_or_404(Certificate, pk=pk)
    if request.method == 'POST':
        title = cert.title
        cert.delete()
        messages.success(request, f"✓ Certificate '{title}' deleted successfully.")
        return redirect('admin_panel:certificates_view')

    return render(request, 'admin_panel/confirm_delete.html', {
        'page_title': f"Delete Certificate: {cert.title} | CRM",
        'item_type': 'Certificate',
        'item_name': cert.title,
        'cancel_url': 'admin_panel:certificates_view',
        'active_menu': 'certificates',
    })
