from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'converter'

urlpatterns = [
    path('', views.redirect_to_loading, name='redirect'),  # redirect from `/` to `/loading/`
    path('loading/', views.loading_screen, name='loading'),  # loading screen
    path('home/', views.home, name='home'),                 # actual homepage
    path('result/', views.result, name='result'),
    path('process/', views.process, name='process'),
    path('video-upload/', views.video_upload, name='video_upload'),  # video upload processing
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),  # API for search suggestions
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
