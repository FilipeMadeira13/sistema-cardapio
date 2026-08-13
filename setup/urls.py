from django.contrib import admin
from django.urls import include, path

from cardapio.views import index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("cardapio.urls")),
]
