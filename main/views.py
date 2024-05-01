from django.shortcuts import render, redirect
from rest_framework import status
import hashlib
import time
from django.views.decorators.csrf import csrf_exempt
from .forms import RegistrationForm, LoginForm, CreatePostForm, CreateCommentForm
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Authors, Posts, Comments
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AuthorSerializer, UserSerializer, CommentSerializer


# Create your views here.


class AuthorsView(APIView):
    def get(self, request):
        queryset = Authors.objects.all()
        id_ = request.query_params.get('id', None)
        first_name = request.query_params.get('first_name', None)
        last_name = request.query_params.get('last_name', None)
        tg_id = request.query_params.get('tg_id', None)

        if id_:
            queryset = queryset.filter(id=id_)
        if first_name:
            queryset = queryset.filter(first_name=first_name)
        if last_name:
            queryset = queryset.filter(last_name=last_name)
        if tg_id:
            queryset = queryset.filter(tg_id=tg_id)

        serializer = AuthorSerializer(
            instance=queryset, many=True
        )
        return Response(serializer.data)


class CommentView(APIView):
    def get(self, request):
        queryset = Comments.objects.all()
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)


def home(request):
    posts = Posts.objects.order_by('-created')[:10]
    return render(request, 'home.html', context={'posts': posts})


def article(request):
    return render(request, 'article.html')


def author(request):
    author_id = request.GET.get('author')
    try:
        author_ = Authors.objects.get(id=author_id)
        user = author_.auth
        posts = Posts.objects.filter(author=author_)
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    return render(request, 'author.html', context={'author': author_, 'user': user, 'posts': posts})



def new(request):
    '''
    Сторінка реєстрації нових користувачів
    Використовується вбудована модель User
    та власна модель Authors яка пов'язана з моделью User
    '''
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if User.objects.filter(username=data['username']).exists():
                # Якщо існує, обробка помилки або повідомлення користувачеві
                # Наприклад, виведення повідомлення про помилку на сторінці
                return HttpResponseBadRequest("Користувач з таким ім'ям вже існує")

            user = User.objects.create_user(username=data['username'], email=data.get('email'), password=data['password'])
            author = Authors(first_name=data['first_name'], last_name=data.get('last_name'), auth=user, tg_id=None)
            author.save()

            return redirect('home')


        else:
            return HttpResponseBadRequest('Something went wrong')
    else:
        return render(request, 'new.html', context={'form': RegistrationForm()})


def login_(request):
    '''
    Сторінка для входу в акаунт за допомогою вбудованого функціоналу Django
    Вхід здійснюється за допомогою username та password
    '''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                login(request, user)
                return redirect('home')
            else:
                return HttpResponseBadRequest('Не правильний логін або пароль')
        else:
            return HttpResponseBadRequest('Something went wrong')

    return render(request, 'login.html', context={'form': LoginForm()})


@login_required
def myaccount(request):
    '''
    Сторінка для перегляду інформації про власний акаунт
    Інформація береться з моделей User та Authors
    Для перегляду необхідно увійти в акаунт
    '''
    return render(request, 'myaccount.html', context={'user': request.user, 'author': Authors.objects.get(auth=request.user)})



def create_post(request):
    '''
    Сторінка на якій користувачі можуть створювати нові статті
    Якщо запит GET повертається форма для створення посту
    Якщо запит POST запит на створення форми обробляється
    Стаття зберігається в моделі Posts і зв'язана через ForeignKey
    з автором який її створив
    '''
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = CreatePostForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user_ = request.user
            author_ = Authors.objects.get(auth=user_)
            if not author_:
                return HttpResponseBadRequest('your account is invalid')
            post_ = Posts(title=data['title'], content=data['content'], short_description=data['short_description'],
                          author=author_, likes=0, views=0)
            post_.save()
            return redirect('myaccount')
        else:
            return HttpResponseBadRequest('smth went wrong ;/')
    return render(request, 'create_post.html', context={'form': CreatePostForm()})


def post_view(request):
    #перевірка існування статті
    post_id = request.GET.get('post')
    try:
        post = Posts.objects.get(id=post_id)
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    comments = Comments.objects.filter(post=post)
    if request.method == 'POST':
        #if request.POST.get('request_type') == 'create_comment':
        # Створення коментаря
        form = CreateCommentForm(request.POST)
        if form.is_valid():
            try:
                user_ = Authors.objects.get(auth=request.user)
            except Exception as e:
                return HttpResponseBadRequest(e)
            data = form.cleaned_data
            comment = Comments(author=user_, post=post, content=data['comment_text'], likes=0)
            comment.save()
            return render(request, 'article_.html', context={'post': post, 'comments': comments, 'CommentForm': CreateCommentForm(initial={'request_type': 'create_comment'})})
        else:
            return HttpResponseBadRequest('smth went wrong')
    #Звичайне відображення сайту (GET)
    if request.user.is_authenticated:
        return render(request, 'article_.html', context={'post': post, 'comments': comments, 'CommentForm': CreateCommentForm(initial={'request_type': 'create_comment'})})
    else:
        return render(request, 'article_.html', context={'post': post,'comments': comments})

@csrf_exempt
def tg_new(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        id_ = request.POST.get('id')
        user_ = User.objects.filter(username=username)
        if user_.exists():
            return HttpResponseBadRequest('username already exist')
        user_ = Authors.objects.filter(tg_id=id)
        if user_.exists():
            return HttpResponseBadRequest('You are already registered')
        try:
            user = User.objects.create_user(username=username, password=password)
            author = Authors(auth=user, first_name=first_name, last_name=last_name, tg_id = id_)
            author.save()
        except Exception as e:
            print(f'tg_new: error: {e}')
        return HttpResponse('created')
    else:
        return HttpResponseBadRequest('post only')


@csrf_exempt
def tg_login(request):
    SECRET_KEY = 'adsriugperjhbkjvlgnrsh JSKLGHJSV Lvh LSEJH Vslkhjasdhflknavsl12417 69oiyavnhvn9uioqrh '
    id_ = request.GET.get('id')
    time_ = request.GET.get('time')
    token = request.GET.get('token')
    if not id_ or not time_ or not token:
        print(id_, time_, token)
        return HttpResponseBadRequest('invalid login')
    check_token = hashlib.sha256(str(SECRET_KEY+str(id_)+str(time_)).encode()).hexdigest()
    if not Authors.objects.filter(tg_id=id_).exists():
        return HttpResponseBadRequest('User does not exist')
    if check_token != token:
        print('invalid token')
        return HttpResponseBadRequest('invalid login')
    user = Authors.objects.get(tg_id=id_).auth
    login(request, user)
    return redirect('myaccount')

