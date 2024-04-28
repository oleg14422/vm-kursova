from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm, CreatePostForm, CreateCommentForm
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from .models import Authors, Posts, Comments
# Create your views here.


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


@login_required()
def create_post(request):
    '''
    Сторінка на якій користувачі можуть створювати нові статті
    Якщо запит GET повертається форма для створення посту
    Якщо запит POST запит на створення форми обробляється
    Стаття зберігається в моделі Posts і зв'язана через ForeignKey
    з автором який її створив
    '''
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


