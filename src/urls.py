from django.contrib import admin
from django.urls import path

from src.apps.tasks.api import urlpatterns as tasks_api

urlpatterns = [
    path('admin/', admin.site.urls),
] + tasks_api
