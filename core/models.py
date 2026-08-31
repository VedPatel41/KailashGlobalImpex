from django.db import models
from django.utils.text import slugify


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True, help_text="Product name, e.g. Raw Tobacco Leaf")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    botanical_name = models.CharField(max_length=200, blank=True, default="", help_text="Botanical name if applicable, e.g. Moringa oleifera")
    part_used = models.CharField(max_length=100, blank=True, default="", help_text="e.g. Leaves")
    origin = models.CharField(max_length=100, default="India")
    tagline = models.CharField(max_length=255, blank=True, default="", help_text="Short product highlight")
    short_description = models.TextField(help_text="Concise description for homepage and listing cards")
    overview = models.TextField(help_text="Detailed overview of the product")
    key_highlights = models.TextField(blank=True, default="", help_text="Newline-separated list of key highlights")
    sourcing_details = models.TextField(blank=True, default="", help_text="Information about Indian origin and sourcing consistency")
    quality_parameters = models.TextField(blank=True, default="", help_text="Quality, grade, and buyer-specific handling")
    packaging_details = models.TextField(blank=True, default="", help_text="Bulk export packaging information")
    applications = models.TextField(blank=True, default="", help_text="End-use and industry applications")
    image = models.ImageField(upload_to="products/", help_text="Product main image")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def highlights_list(self):
        if not self.key_highlights:
            return []
        return [line.strip() for line in self.key_highlights.splitlines() if line.strip()]


class Inquiry(models.Model):
    STATUS_NEW = "NEW"
    STATUS_READ = "READ"
    STATUS_CONTACTED = "CONTACTED"
    STATUS_CLOSED = "CLOSED"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_READ, "Read"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_CLOSED, "Closed"),
    ]

    PRODUCT_CHOICES = [
        ("Raw Tobacco Leaf", "Raw Tobacco Leaf"),
        ("Moringa Leaf Powder", "Moringa Leaf Powder"),
        ("General / Other Sourcing Inquiry", "General / Other Sourcing Inquiry"),
    ]

    name = models.CharField(max_length=150, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email Address")
    company_name = models.CharField(max_length=200, blank=True, default="", verbose_name="Company Name")
    mobile_number = models.CharField(max_length=30, verbose_name="Mobile / Phone Number")
    country = models.CharField(max_length=100, verbose_name="Country / Destination Port")
    product = models.CharField(max_length=120, choices=PRODUCT_CHOICES, default="Raw Tobacco Leaf", verbose_name="Product of Interest")
    product_details = models.TextField(blank=True, default="", verbose_name="Requirements / Quantity / Specifications")
    remarks = models.TextField(blank=True, default="", verbose_name="Additional Remarks / Timeline")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    admin_notes = models.TextField(blank=True, default="", help_text="Internal notes for administrators")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Inquiry"
        verbose_name_plural = "Inquiries"

    def __str__(self):
        return f"{self.name} - {self.company_name or self.country} ({self.product}) [{self.get_status_display()}]"


class Certificate(models.Model):
    title = models.CharField(max_length=200, verbose_name="Certificate / Compliance Title")
    description = models.TextField(blank=True, default="", verbose_name="Description / Authority")
    document = models.FileField(upload_to="certificates/", blank=True, null=True, verbose_name="Certificate File / Image")
    issue_date = models.DateField(blank=True, null=True, verbose_name="Issue Date")
    expiry_date = models.DateField(blank=True, null=True, verbose_name="Expiry Date")
    is_active = models.BooleanField(default=False, help_text="Only active certificates will be displayed publicly")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"

    def __str__(self):
        return self.title
