from django.urls import path
from cardapio.views import index

urlpatterns = [
    path('', index)
]
