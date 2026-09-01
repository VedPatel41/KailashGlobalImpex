import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files import File
from django.conf import settings
from core.models import Product

User = get_user_model()


class Command(BaseCommand):
    help = "Seed authentic Kailash Global Impex products and default administrative user"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Kailash Global Impex authentic data...")

        # 1. Ensure Superuser / Staff User
        username = os.environ.get('KGI_ADMIN_USER', 'admin')
        email = os.environ.get('KGI_ADMIN_EMAIL', 'info@kailashglobalimpex.com')
        password = os.environ.get('KGI_ADMIN_PASS')

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': True, 'is_superuser': True}
        )

        if created:
            if password:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created admin user: {username} (configured via KGI_ADMIN_PASS)"))
            else:
                if settings.DEBUG:
                    user.set_password('Kailash@2026Export')
                    user.save()
                    self.stdout.write(self.style.WARNING(f"Created admin user: {username} (local development mode)"))
                else:
                    user.set_unusable_password()
                    user.save()
                    self.stdout.write(self.style.WARNING(
                        f"Created admin user: {username} without password. "
                        "Set KGI_ADMIN_PASS in Render Environment Variables to enable login."
                    ))
        else:
            user.is_staff = True
            user.is_superuser = True
            if email and not user.email:
                user.email = email
            if password:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Updated admin user: {username} (credentials updated from KGI_ADMIN_PASS)"))
            else:
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Admin user verified: {username} (permissions active)"))

        # 2. Seed Authentic Products
        base_dir = settings.BASE_DIR
        tobacco_asset = base_dir / 'static' / 'images' / 'products' / 'tobacco.png'
        moringa_asset = base_dir / 'static' / 'images' / 'products' / 'moringa.png'

        # Raw Tobacco Leaf
        tobacco, t_created = Product.objects.update_or_create(
            slug='raw-tobacco-leaf',
            defaults={
                'name': 'Raw Tobacco Leaf',
                'botanical_name': '',
                'part_used': 'Leaves',
                'origin': 'India',
                'tagline': 'Authentic Indian origin tobacco leaves sourced to precise buyer specifications',
                'short_description': 'Export-grade raw tobacco leaves sourced directly from established growing tracts across India, sorted and graded to international buyer requirements.',
                'overview': (
                    'Kailash Global Impex facilitates the export of raw tobacco leaf from premier Indian agricultural belts. '
                    'We work closely with commercial importers, processors, and trading houses worldwide to source, grade, and supply '
                    'raw tobacco leaves that match exact buyer-specified leaf characteristics, moisture tolerance, and curing grades.'
                ),
                'key_highlights': (
                    "Indian Agricultural Origin\n"
                    "Customized Sourcing by Leaf Grade & Type\n"
                    "Rigorous Moisture & Handling Controls\n"
                    "Bulk Export Packaging Suited for Ocean Transit\n"
                    "Subject to Strict Inspection and Regulatory Readiness"
                ),
                'sourcing_details': (
                    'Direct sourcing from established tobacco-growing belts in India. Sourcing is tailored specifically to '
                    'buyer order parameters, ensuring grade uniformity and dependable supply pipelines.'
                ),
                'quality_parameters': (
                    'Grade, leaf length, color, texture, moisture tolerance, and aroma parameters are aligned strictly with '
                    'buyer purchase contracts, commercial specifications, and export handling standards.'
                ),
                'packaging_details': (
                    'Packed in seaworthy export bales, corrugated master cartons, or custom export packaging with protective '
                    'inner liners to preserve leaf integrity and prevent moisture damage during shipping.'
                ),
                'applications': (
                    'Commercial processing, blending, shisha and hookah formulation, industrial extraction, and international commodity trade.'
                ),
                'is_active': True,
                'display_order': 1,
            }
        )
        tobacco_has_file = bool(tobacco.image) and tobacco.image.storage.exists(tobacco.image.name)
        if tobacco_asset.exists() and not tobacco_has_file:
            with open(tobacco_asset, 'rb') as f:
                tobacco.image.save('tobacco.png', File(f), save=True)
        self.stdout.write(self.style.SUCCESS("Product ready: Raw Tobacco Leaf"))

        # Moringa Leaf Powder
        moringa, m_created = Product.objects.update_or_create(
            slug='moringa-leaf-powder',
            defaults={
                'name': 'Moringa Leaf Powder',
                'botanical_name': 'Moringa oleifera',
                'part_used': 'Leaves',
                'origin': 'India',
                'tagline': 'Finely milled pure Indian Moringa oleifera leaf powder for commercial formulations',
                'short_description': '100% pure, fine green Moringa oleifera leaf powder cultivated and processed in India, suitable for food, nutraceutical, and plant-based commercial applications.',
                'overview': (
                    'Derived from freshly harvested and hygienically dehydrated leaves of Moringa oleifera in India, '
                    'our Moringa leaf powder is processed into a fine, free-flowing green botanical powder. '
                    'Kailash Global Impex supplies bulk quantities to international food manufacturers, beverage formulators, '
                    'dietary supplement producers, and commercial trading partners seeking dependable Indian origin botanicals.'
                ),
                'key_highlights': (
                    "Botanical Name: Moringa oleifera\n"
                    "Part Used: 100% Dehydrated Leaves\n"
                    "Fine Mesh Powder Form\n"
                    "Rich Natural Green Appearance\n"
                    "Bulk Supply for Food & Plant-Based Formulations\n"
                    "Customized Packaging per Buyer Specifications"
                ),
                'sourcing_details': (
                    'Sourced from dedicated moringa cultivation regions across India. Leaves are carefully harvested, '
                    'washed, low-temperature dried, and pulverized under hygienic conditions to retain botanical color and properties.'
                ),
                'quality_parameters': (
                    'Screened for mesh size, moisture content, natural aroma, and leaf cleanliness in accordance with buyer '
                    'purchase agreements and export destination guidelines.'
                ),
                'packaging_details': (
                    'Food-grade double polythene lined multi-wall paper bags, HDPE drums, or vacuum-sealed foil packs '
                    '(10 kg, 20 kg, 25 kg) according to buyer specifications and destination handling requirements.'
                ),
                'applications': (
                    'Functional foods, herbal teas, health blends, smoothies, dietary supplements, cosmetic ingredients, and plant-based protein formulations.'
                ),
                'is_active': True,
                'display_order': 2,
            }
        )
        moringa_has_file = bool(moringa.image) and moringa.image.storage.exists(moringa.image.name)
        if moringa_asset.exists() and not moringa_has_file:
            with open(moringa_asset, 'rb') as f:
                moringa.image.save('moringa.png', File(f), save=True)
        self.stdout.write(self.style.SUCCESS("Product ready: Moringa Leaf Powder"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded authentic products and administrative user."))
