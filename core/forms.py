import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Inquiry


class InquiryForm(forms.ModelForm):
    # Honeypot field for anti-bot spam protection (hidden in CSS)
    website_url = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'tabindex': '-1',
            'class': 'hidden-honeypot',
            'aria-hidden': 'true',
        })
    )

    class Meta:
        model = Inquiry
        fields = [
            'name',
            'email',
            'company_name',
            'mobile_number',
            'country',
            'product',
            'product_details',
            'remarks',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. John Doe / Global Trade Director',
                'required': 'required',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'procurement@company.com',
                'required': 'required',
                'autocomplete': 'email',
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Company / Trading House Name',
                'autocomplete': 'organization',
            }),
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+1 555 123 4567 / +971 50 123 4567',
                'required': 'required',
                'autocomplete': 'tel',
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. United Arab Emirates / Germany / USA',
                'required': 'required',
            }),
            'product': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
            'product_details': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Specify quantity (e.g. 5 MT, 1 FCL), required grade, target destination port, or specific leaf parameters...',
                'rows': 3,
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Any delivery timeline, packaging preferences, or specific inquiries...',
                'rows': 2,
            }),
        }

    def clean_website_url(self):
        """If honeypot is filled, it is automated spam."""
        val = self.cleaned_data.get('website_url')
        if val:
            raise ValidationError("Spam detected.")
        return val

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number', '').strip()
        # Basic validation to ensure plausible phone number length and characters
        cleaned = re.sub(r'[\s\-\(\)\.]', '', mobile)
        if len(cleaned) < 6 or len(cleaned) > 25:
            raise ValidationError("Please provide a valid international phone/mobile number.")
        return mobile

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise ValidationError("Please provide a valid contact name.")
        return name
