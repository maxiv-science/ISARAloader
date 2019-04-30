"""mysite URL Configuration

[...]
"""
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('isara/', views.load_isara),
    path('', views.load_isara),

]