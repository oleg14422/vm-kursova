from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('article', views.article, name='article'),
    path('author', views.author, name='author'),
    path('wild', views.index_, name='wild')
]