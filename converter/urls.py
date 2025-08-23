from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

app_name = 'converter'

urlpatterns = [
    path('', views.redirect_to_loading, name='redirect'),  # redirect from `/` to `/loading/`
    path('loading/', views.loading_screen, name='loading'),  # loading screen
    path('home/', views.home, name='home'),                 # actual homepage
    path('result/', views.result, name='result'),
    path('process/', views.process, name='process'),

    # Google Search Console verification file
    path(
        "googlef7a4e737ec62d8fa.html",
        TemplateView.as_view(template_name="googlef7a4e737ec62d8fa.html"),
        name="google-site-verification",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
