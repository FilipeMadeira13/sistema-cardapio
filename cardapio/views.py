from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("<h1>Cardápio Online</h1><p>Bem-vindo ao cardápio online</p>")
