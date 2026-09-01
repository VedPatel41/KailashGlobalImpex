from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    
    # Inquiries CRM
    path('inquiries/', views.inquiries_list, name='inquiries_list'),
    path('inquiries/<int:pk>/', views.inquiry_detail, name='inquiry_detail'),
    path('inquiries/<int:pk>/update-status/', views.update_inquiry_status_ajax, name='update_inquiry_status_ajax'),
    path('inquiries/<int:pk>/delete/', views.inquiry_delete, name='inquiry_delete'),
    path('inquiries/export/csv/', views.export_inquiries_csv, name='export_inquiries_csv'),
    
    # Products CMS
    path('products/', views.products_view, name='products_view'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/toggle/', views.product_toggle, name='product_toggle'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Certificates CMS
    path('certificates/', views.certificates_view, name='certificates_view'),
    path('certificates/add/', views.certificate_add, name='certificate_add'),
    path('certificates/<int:pk>/edit/', views.certificate_edit, name='certificate_edit'),
    path('certificates/<int:pk>/toggle/', views.certificate_toggle, name='certificate_toggle'),
    path('certificates/<int:pk>/delete/', views.certificate_delete, name='certificate_delete'),
]
