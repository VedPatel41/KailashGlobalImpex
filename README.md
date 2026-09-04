# Kailash Global Impex

> **Production B2B agricultural commodity export website** built with Django, deployed on Render with a managed PostgreSQL database and a custom domain.

[![Live Website](https://img.shields.io/badge/Live-kailashglobalimpex.com-green?style=for-the-badge&logo=google-chrome)](https://kailashglobalimpex.com)
[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Managed-blue?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-purple?style=for-the-badge&logo=render)](https://render.com/)

---

## Live Demo

**[https://kailashglobalimpex.com](https://kailashglobalimpex.com)**

---

## Overview

Kailash Global Impex is a fully functional production web application for a Gujarat-based agricultural commodity export business. The website presents the company's product portfolio (Raw Tobacco Leaf and Moringa Leaf Powder), handles international B2B trade inquiries, and provides a secure internal admin CRM panel for managing products, inquiries, and compliance certificates.

The project is deployed on Render's managed cloud infrastructure with PostgreSQL as the production database, WhiteNoise (with Brotli compression) for static file serving, and a custom domain with HTTPS and HSTS security headers.

---

## Features

### Public Website
- **Homepage** — Hero image carousel with product showcase and company introduction
- **Product Listing & Detail Pages** — SEO-optimized pages for each export commodity with key highlights, sourcing details, quality parameters, packaging information, and industry applications
- **Our Approach Page** — Company's 3-pillar sourcing philosophy: Source Right, Match Requirements, Deliver Reliably
- **Quality & Compliance Page** — Certificate management with active/coming-soon states
- **Contact / Trade Inquiry Form** — Full B2B inquiry form with AJAX and traditional POST support; captures company, mobile, country, product, quantity, specifications, and remarks
- **Custom 404 & 500 Error Pages** — Branded error pages with correct HTTP status codes

### Admin CRM Panel (`/admin-panel/`)
- Secure login-protected internal dashboard
- **Product Management** — Add, edit, and delete products with image uploads
- **Inquiry Management** — View all trade inquiries, update workflow status (New → Read → Contacted → Closed), add internal admin notes
- **Certificate Management** — Upload and manage quality/compliance certificates

### SEO & Infrastructure
- Dynamic XML sitemap (`/sitemap.xml`) with `X-Robots-Tag` removal for Google Search Console compatibility
- Dynamic `robots.txt` with Googlebot directives and sitemap reference
- Structured page titles and meta descriptions on every view
- Full favicon set (ICO, PNG in multiple sizes) and `site.webmanifest`
- Email notifications via SMTP on new inquiry submissions
- IP address capture on inquiry submissions

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | Django 5.2 |
| Language | Python 3.x |
| Database (Production) | PostgreSQL (Render managed) |
| Database (Local Dev) | SQLite (automatic fallback when `DATABASE_URL` is unset) |
| Static Files | WhiteNoise 6.8 with Brotli compression |
| Media/Images | Pillow |
| WSGI Server | Gunicorn |
| Deployment Platform | Render |
| Environment Config | python-dotenv |
| Email | Django SMTP backend (Hostinger SMTP) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |

---

## Project Structure

```
KailashGlobalImpex/
├── kailash_project/            # Django project settings and root URLs
│   ├── settings.py
│   └── urls.py
├── core/                       # Public-facing app
│   ├── models.py               # Product, Inquiry, Certificate models
│   ├── views.py                # All public views + inquiry form handler
│   ├── forms.py                # InquiryForm
│   ├── sitemaps.py
│   └── management/commands/
│       └── seed_kgi_data.py    # Seeds products and admin account
├── admin_panel/                # Internal CRM panel
│   ├── views.py
│   └── forms.py
├── templates/
│   ├── base.html               # Shared layout
│   ├── core/                   # Public page templates
│   ├── admin_panel/            # CRM templates
│   └── errors/                 # 404 and 500 pages
├── static/
│   ├── css/                    # main.css, admin.css
│   ├── js/                     # main.js, admin.js
│   └── images/                 # Branding, favicons, product/hero images
├── media/                      # Uploaded product images, founder photos
├── build.sh                    # Render build script
├── render.yaml                 # Render Blueprint (infrastructure as code)
├── requirements.txt
└── .env.example                # Environment variable template
```

---

## Database Models

### `Product`
Stores all product information for the export catalog.

| Field | Description |
|-------|-------------|
| `name`, `slug` | Product name and URL slug (auto-generated) |
| `botanical_name`, `part_used` | Scientific classification |
| `tagline`, `short_description`, `overview` | Layered product content |
| `key_highlights` | Newline-separated bullet point list |
| `sourcing_details`, `quality_parameters` | Export-grade specifications |
| `packaging_details`, `applications` | Bulk packaging and industry use |
| `image` | Product photo upload |
| `is_active`, `display_order` | Visibility and sort control |

### `Inquiry`
Captures all B2B trade inquiry form submissions.

| Field | Description |
|-------|-------------|
| `name`, `email`, `company_name`, `mobile_number` | Contact details |
| `country` | Destination country or port |
| `product` | Raw Tobacco Leaf / Moringa Leaf Powder / General |
| `product_details`, `remarks` | Quantity, specs, timeline |
| `status` | New → Read → Contacted → Closed |
| `admin_notes`, `ip_address` | Internal tracking |

### `Certificate`
Quality and compliance certificate management.

---

## Environment Configuration

Copy `.env.example` to `.env` for local development:

```env
# Django Core
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (leave empty to use SQLite locally)
DATABASE_URL=

# CSRF
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# Email (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
COMPANY_NOTIFICATION_EMAIL=your-email@gmail.com

# Seed Data (admin account)
KGI_ADMIN_USER=admin
KGI_ADMIN_EMAIL=admin@example.com
KGI_ADMIN_PASS=AdminPassword123
```

---

## Deployment on Render

This project uses a **Render Blueprint** (`render.yaml`) for infrastructure-as-code deployment. It automatically provisions:
- A **Web Service** running `gunicorn kailash_project.wsgi:application`
- A **Managed PostgreSQL database** (Starter plan)
- All required environment variables (with `DJANGO_SECRET_KEY` auto-generated)

### Build Script (`build.sh`)

Render executes `build.sh` on every deploy:

```bash
pip install -r requirements.txt            # Install dependencies
python manage.py collectstatic --no-input  # Collect and compress static files
python manage.py migrate                   # Apply database migrations
python manage.py seed_kgi_data             # Seed products and admin account
```

### Static Files

Static files are served using **WhiteNoise** with **Brotli compression** directly from the Django application, with no external CDN or reverse proxy required.

### Domains

- **Primary:** `https://kailashglobalimpex.com`
- **Alternate:** `https://vedop.fun`
- **Render subdomain:** `https://kailashglobalimpex.onrender.com`

---

## Local Development Setup

### Prerequisites
- Python 3.10+

### Steps

```bash
# Clone the repository
git clone https://github.com/VedPatel41/KailashGlobalImpex.git
cd KailashGlobalImpex

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Apply migrations (uses SQLite by default locally)
python manage.py migrate

# Seed initial data
python manage.py seed_kgi_data

# Run development server
python manage.py runserver
```

- **Public site:** `http://127.0.0.1:8000/`
- **Admin CRM:** `http://127.0.0.1:8000/admin-panel/`

> `DATABASE_URL` is not required locally. When unset, the app uses SQLite automatically.

---

## Dependencies

```
Django>=5.2.0,<5.3.0
dj-database-url>=3.1.0
psycopg[binary]>=3.1.0
whitenoise>=6.8.0
gunicorn>=23.0.0
pillow>=11.0.0
python-dotenv>=1.0.0
```

---

## Author

**Ved Patel** — B.Tech Computer Engineering Student  
[GitHub](https://github.com/VedPatel41) · [LinkedIn](https://www.linkedin.com/in/ved-patel-0bb446376)

