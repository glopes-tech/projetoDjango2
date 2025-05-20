from django.contrib import admin
from django.urls import path, include
from enquete import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('enquete/', include('enquete.urls', namespace='enquete')),
]