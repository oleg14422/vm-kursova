from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('article', views.article, name='article'),
    path('author', views.author, name='author'),
    path('new', views.new, name='new'),
    path('login', views.login_, name='login'),
    path('myaccount', views.myaccount, name='myaccount'),
    path('create_post', views.create_post, name='create_post'),
    path('article_', views.post_view, name='post_view'),
    path('tg_new', views.tg_new, name='tg_new'),
    path('api', views.CommentView.as_view(), name='api'),
    path('api/authors', views.AuthorsView.as_view(), name='api_author'),
    path('tg_login', views.tg_login, name='tg_login')
]