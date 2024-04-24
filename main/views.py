from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home.html')

def article(request):
    return render(request, 'article.html')

def author(request):
    return render(request, 'author.html')

def index_(request):
    return render(request, 'index.html')