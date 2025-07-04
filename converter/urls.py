from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'converter'

urlpatterns = [
	path('loading/', views.loading_screen, name='loading'),
    path('', views.home, name='home'),
    path('result/', views.result, name='result'),
    path("process/", views.process, name="process"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

