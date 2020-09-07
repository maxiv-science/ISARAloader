"""mysite URL Configuration

[...]
"""
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('isara/', views.load_isara, name="load_isara"),
    path('duo_login/', views.duo_login, name="duo_login"),
    path('duo_logout/', views.duo_logout, name="duo_logout"),
    path('safe_pucks/', views.safe_pucks, name="safe_pucks"),
    
    path('', views.load_isara),

]