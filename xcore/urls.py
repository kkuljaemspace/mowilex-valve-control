"""
URL configuration for xcore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.views.static import serve
from django.urls import path, re_path, include

admin.site.site_header = "Mowilex"
admin.site.site_title = "Mowilex"
admin.site.index_title = "Selamat Datang di Portal Administrator Mowilex"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('select2/', include('django_select2.urls')),
    path('', include('otentifikasi.urls')),
    path('', include('project.urls')),
    path('', include('pwa.urls')),
    path('serviceworker.js', TemplateView.as_view(
        template_name='project/serviceworker.js',
        content_type='application/javascript')),
    re_path(r'^media/(?P<path>.*)$', login_required(serve), {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
