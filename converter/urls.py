from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap
from . import views
from .sitemaps import StaticViewSitemap  # we already made this earlier

app_name = 'converter'

# Google verification
def google_verification(request):
    return HttpResponse("google-site-verification: googlef7a4e737ec62d8fa.html", content_type="text/plain")

# robots.txt
def robots_txt(request):
    content = """User-agent: *
Disallow: /process/
Allow: /

Sitemap: https://himigtube.onrender.com/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")

# Sitemap dict
sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', views.redirect_to_loading, name='redirect'),
    path('loading/', views.loading_screen, name='loading'),
    path('home/', views.home, name='home'),
    path('result/', views.result, name='result'),
    path('process/', views.process, name='process'),

    # Google Search Console verification
    path("googlef7a4e737ec62d8fa.html", google_verification, name="google-site-verification"),

    # Sitemap
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name="sitemap"),

    # Robots.txt
    path("robots.txt", robots_txt, name="robots"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
