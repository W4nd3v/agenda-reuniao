from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('agenda/', include('agenda.urls', namespace='agenda')),
    path('admin/', admin.site.urls),
]
