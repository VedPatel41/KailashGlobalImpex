from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('our-approach/', views.our_approach, name='our_approach'),
    path('certificates/', views.certificates, name='certificates'),
    path('contact/', views.contact, name='contact'),
    path('submit-inquiry/', views.submit_inquiry, name='submit_inquiry'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('favicon.ico', views.favicon_view, name='favicon'),
    path('site.webmanifest', views.site_manifest_view, name='site_manifest'),
    path('manifest.json', views.site_manifest_view, name='manifest_json'),
]
