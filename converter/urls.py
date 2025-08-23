from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap
from . import views
from .sitemaps import StaticViewSitemap  # you'll create this file next

app_name = 'converter'

# Function to serve Google verification file
def google_verification(request):
    return HttpResponse("google-site-verification: googlef7a4e737ec62d8fa.html", content_type="text/plain")

# Sitemap dictionary
sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', views.redirect_to_loading, name='redirect'),  # redirect from `/` to `/loading/`
    path('loading/', views.loading_screen, name='loading'),  # loading screen
    path('home/', views.home, name='home'),                 # actual homepage
    path('result/', views.result, name='result'),
    path('process/', views.process, name='process'),

    # Google Search Console verification route
    path("googlef7a4e737ec62d8fa.html", google_verification, name="google-site-verification"),

    # Sitemap
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name="sitemap"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
