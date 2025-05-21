from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('find_pp2m.urls', namespace='find_pp2m')),
    path('admin/', admin.site.urls),
]
