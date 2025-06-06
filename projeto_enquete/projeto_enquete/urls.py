from django.contrib import admin
from django.urls import path, include
from enquete import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('enquete.urls')),
    path('api/', include('enquete.api.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]