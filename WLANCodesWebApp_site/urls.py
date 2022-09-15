from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('WLANCodesWebApp.urls')),
    path('codeimport/', include('codeimport.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
