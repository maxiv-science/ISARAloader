from django.contrib import admin
from django.urls import path
from laser.views import main


urlpatterns = [
    path("admin/", admin.site.urls),
    path("isara/", main.load_isara, name="load_isara"),
    path("duo_login/", main.duo_login, name="duo_login"),
    path("duo_logout/", main.duo_logout, name="duo_logout"),
    path("safe_pucks/", main.safe_pucks, name="safe_pucks"),
    path("", main.load_isara),
]
