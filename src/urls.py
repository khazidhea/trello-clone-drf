from django.contrib import admin
from django.urls import path
from rest_framework.authtoken import views


from src.apps.tasks.api import urlpatterns as tasks_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', views.obtain_auth_token)
] + tasks_api
