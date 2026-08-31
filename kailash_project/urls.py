from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    # Custom Modern Corporate CRM Admin Panel
    path('admin-panel/', include('admin_panel.urls', namespace='admin_panel')),
    
    # Internal Standard Django Admin
    path('admin/', admin.site.urls),
    
    # Core Public Website
    path('', include('core.urls', namespace='core')),
]

# Custom Error Handlers
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'

# Media & Static Files Serving
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Ensure media files are accessible in production environment
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
