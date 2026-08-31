from django.contrib import admin
from .models import Product, Inquiry, Certificate


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'botanical_name', 'origin', 'is_active', 'display_order', 'updated_at')
    list_filter = ('is_active', 'origin')
    search_fields = ('name', 'botanical_name', 'short_description', 'overview')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'display_order')


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'country', 'product', 'mobile_number', 'status', 'created_at')
    list_filter = ('status', 'product', 'created_at')
    search_fields = ('name', 'email', 'company_name', 'country', 'product_details', 'remarks')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'ip_address')
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'company_name', 'mobile_number', 'country')
        }),
        ('Inquiry Details', {
            'fields': ('product', 'product_details', 'remarks')
        }),
        ('CRM Processing', {
            'fields': ('status', 'admin_notes', 'ip_address', 'created_at', 'updated_at')
        }),
    )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('title', 'issue_date', 'expiry_date', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('is_active',)
