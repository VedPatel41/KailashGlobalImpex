from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from core.models import Inquiry, Product, Certificate


class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username / Email Address",
        widget=forms.TextInput(attrs={
            'class': 'admin-form-input',
            'placeholder': 'Enter your username or email',
            'autofocus': True,
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'admin-form-input',
            'placeholder': '••••••••••••',
            'autocomplete': 'current-password',
        })
    )


class InquiryUpdateForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'admin-form-select'}),
            'admin_notes': forms.Textarea(attrs={
                'class': 'admin-form-textarea',
                'rows': 4,
                'placeholder': 'Add internal follow-up notes, quotation details, or shipping communication notes here...'
            }),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'botanical_name', 'part_used', 'origin', 'tagline',
            'short_description', 'overview', 'key_highlights', 'applications',
            'quality_parameters', 'packaging_details', 'image', 'is_active', 'display_order'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'admin-form-input',
                'placeholder': 'e.g. Raw Tobacco Leaf or Moringa Leaf Powder'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'admin-form-input',
                'placeholder': 'e.g. raw-tobacco-leaf (auto-generated if empty)'
            }),
            'botanical_name': forms.TextInput(attrs={
                'class': 'admin-form-input',
                'placeholder': 'e.g. Moringa oleifera (optional)'
            }),
            'part_used': forms.TextInput(attrs={
                'class': 'admin-form-input',
                'placeholder': 'e.g. Leaves (optional)'
            }),
            'origin': forms.TextInput(attrs={
                'class': 'admin-form-input',
                'placeholder': 'e.g. India'
            }),
            'tagline': forms.TextInput(attrs={
                'class': 'admin-form-input',
                'placeholder': 'Short commercial highlight'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'admin-form-textarea',
                'rows': 3,
                'placeholder': 'Concise overview for cards and meta descriptions...'
            }),
            'overview': forms.Textarea(attrs={
                'class': 'admin-form-textarea',
                'rows': 5,
                'placeholder': 'Detailed product description...'
            }),
            'key_highlights': forms.Textarea(attrs={
                'class': 'admin-form-textarea',
                'rows': 4,
                'placeholder': 'One highlight per line\ne.g. Indian Agricultural Origin\nCustomized Sourcing by Leaf Grade'
            }),
            'applications': forms.Textarea(attrs={
                'class': 'admin-form-textarea',
                'rows': 3,
                'placeholder': 'Commercial applications (food, processing, etc.)...'
            }),
            'quality_parameters': forms.Textarea(attrs={
                'class': 'admin-form-textarea',
                'rows': 3,
                'placeholder': 'Handling and quality alignment...'
            }),
            'packaging_details': forms.Textarea(attrs={
                'class': 'admin-form-textarea',
                'rows': 3,
                'placeholder': 'Bulk export packaging details...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'admin-form-file'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'admin-form-input',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'admin-form-checkbox'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['image'].required = False

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'content_type'):
            valid_types = ['image/jpeg', 'image/png', 'image/webp']
            if image.content_type not in valid_types:
                raise ValidationError("Please upload a valid image file (PNG, JPG, or WEBP).")
            if image.size > 10 * 1024 * 1024:
                raise ValidationError("Image file size should not exceed 10MB.")
        return image


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['title', 'description', 'document', 'issue_date', 'expiry_date', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'admin-form-input',
                'placeholder': 'e.g. Export Registration Certificate / Phytosanitary Authority'
            }),
            'description': forms.Textarea(attrs={
                'class': 'admin-form-textarea',
                'rows': 3,
                'placeholder': 'Issuing authority, certificate scope, or regulatory references...'
            }),
            'document': forms.FileInput(attrs={
                'class': 'admin-form-file'
            }),
            'issue_date': forms.DateInput(attrs={
                'class': 'admin-form-input',
                'type': 'date'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'admin-form-input',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'admin-form-checkbox'
            }),
        }

    def clean_document(self):
        doc = self.cleaned_data.get('document')
        if doc and hasattr(doc, 'content_type'):
            valid_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp']
            if doc.content_type not in valid_types:
                raise ValidationError("Allowed document formats: PDF, PNG, JPG, WEBP.")
            if doc.size > 15 * 1024 * 1024:
                raise ValidationError("Document file size must not exceed 15MB.")
        return doc
