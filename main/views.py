from django.shortcuts import render, redirect
import hashlib
from django.views.decorators.csrf import csrf_exempt
from .forms import RegistrationForm, LoginForm, CreatePostForm, CreateCommentForm, ChangeUserDataForm,ChangePasswordForm,ImageUploadForm
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Authors, Posts, Comments
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .serializers import AuthorSerializer, UserSerializer, CommentSerializer
import markdown
import time


# Create your views here.
DEFAULT_LOGO_PATH = 'static/img/pngegg.png'

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
    user = request.user
    if user.is_authenticated:
        try:
            author = Authors.objects.get(auth=user)
        except Exception as e:
            return HttpResponseBadRequest('Something went wrong')
        if author.user_images:
            logo_link = author.user_images.url[5:]
        else:
            logo_link = DEFAULT_LOGO_PATH
    else:
        logo_link = DEFAULT_LOGO_PATH

    return render(request, 'home.html', context={'posts': posts, 'logo_link':logo_link})


def article(request):
    return render(request, 'article.html')


def author(request):
    return redirect('home')
    user = request.user
    if user.is_authenticated:
        try:
            author = Authors.objects.get(auth=user)
        except Exception as e:
            return HttpResponseBadRequest('Something went wrong')
        if author.user_images:
            logo_link = author.user_images.url[5:]
        else:
            logo_link = DEFAULT_LOGO_PATH
    else:
        logo_link = DEFAULT_LOGO_PATH

    author_id = request.GET.get('author')
    try:
        author_ = Authors.objects.get(id=author_id)
        user = author_.auth
        posts = Posts.objects.filter(author=author_)
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    return render(request, 'author.html', context={'author': author_, 'user': user, 'posts': posts})


def new(request):

    logo_link = DEFAULT_LOGO_PATH
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
        return render(request, 'new.html', context={'form': RegistrationForm(), 'logo_link': logo_link})


def login_(request):
    logo_link = DEFAULT_LOGO_PATH
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

    return render(request, 'login.html', context={'form': LoginForm(), 'logo_link': logo_link})



def myaccount(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    try:
        author = Authors.objects.get(auth=user)
    except Exception as e:
        return HttpResponseBadRequest('Something went wrong')
    if author.user_images:
        logo_link = author.user_images.url[5:]
    else:
        logo_link = DEFAULT_LOGO_PATH
    initial_data = {'username': user.username, 'first_name': author.first_name, 'last_name': author.last_name,
                    'email': user.email, 'bio': author.about_me}
    form = ChangeUserDataForm(initial=initial_data)
    if request.method == 'POST':
        if request.POST.get('request_type') == 'change_data':
            form = ChangeUserDataForm(request.POST)
            if form.is_valid():
                author.first_name = form.cleaned_data['first_name']
                author.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
                user.username = form.cleaned_data['username']
                author.about_me = form.cleaned_data['bio']
                author.save()
                user.save()
                initial_data = {'username': user.username, 'first_name': author.first_name,
                                'last_name': author.last_name,
                                'email': user.email, 'bio': author.about_me}
                form = ChangeUserDataForm(initial=initial_data)
                return render(request, 'myaccount.html', context={'form': form, 'logo_link': logo_link,
                                                                  'ChangePasswordForm': ChangePasswordForm(),
                                                                  'ImageForm': ImageUploadForm()})
            else:
                return HttpResponseBadRequest('form is not valid')

        elif request.POST.get('request_type') == 'change_password':
            form = ChangePasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['password'])
                user.save()
                return redirect('home')

        elif request.POST.get('request_type') == 'photo_change':
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                author.user_images = form.cleaned_data['image']
                author.save()
                initial_data = {'username': user.username, 'first_name': author.first_name,
                                'last_name': author.last_name,
                                'email': user.email, 'bio': author.about_me}
                form = ChangeUserDataForm(initial=initial_data)
                return render(request, 'myaccount.html', context={'form': form, 'logo_link': logo_link,
                                                                  'ChangePasswordForm': ChangePasswordForm(),
                                                                  'ImageForm': ImageUploadForm()})

    return render(request, 'myaccount.html', context={'form': form, 'logo_link': logo_link,
                                                      'ChangePasswordForm': ChangePasswordForm(),
                                                      'ImageForm': ImageUploadForm()})



def create_post(request):
    '''
    Сторінка на якій користувачі можуть створювати нові статті
    Якщо запит GET повертається форма для створення посту
    Якщо запит POST запит на створення форми обробляється
    Стаття зберігається в моделі Posts і зв'язана через ForeignKey
    з автором який її створив
    '''
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    try:
        author = Authors.objects.get(auth=user)
    except Exception as e:
        return HttpResponseBadRequest('Something went wrong')
    if author.user_images:
        logo_link = author.user_images.url[5:]
    else:
        logo_link = DEFAULT_LOGO_PATH

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
    return render(request, 'create_post.html', context={'form': CreatePostForm(), 'logo_link': logo_link})


def post_view(request):
    #перевірка існування статті
    post_id = request.GET.get('post')
    user = request.user
    if user.is_authenticated:
        try:
            author = Authors.objects.get(auth=user)
        except Exception as e:
            return HttpResponseBadRequest('Something went wrong')
        if author.user_images:
            logo_link = author.user_images.url[5:]
        else:
            logo_link = DEFAULT_LOGO_PATH
    else:
        logo_link = DEFAULT_LOGO_PATH
    try:
        post = Posts.objects.get(id=post_id)
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    content = post.content
    md_content = markdown.markdown(content)
    comments = Comments.objects.filter(post=post)
    if request.method == 'POST':
        # if request.POST.get('request_type') == 'create_comment':
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
            print('logo_link: ',logo_link)
            return render(request, 'article_.html', context={'post': post, 'logo_link': logo_link, 'content': md_content, 'comments': comments, 'CommentForm': CreateCommentForm(initial={'request_type': 'create_comment'})})
        else:
            return HttpResponseBadRequest('smth went wrong')

    # Звичайне відображення сайту (GET)
    if request.user.is_authenticated:
        return render(request, 'article_.html', context={'post': post,  'logo_link': logo_link ,'content': md_content, 'comments': comments, 'CommentForm': CreateCommentForm(initial={'request_type': 'create_comment'})})
    else:
        return render(request, 'article_.html', context={'post': post, 'logo_link': logo_link, 'content': md_content, 'comments': comments})

@csrf_exempt
def tg_new(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        id_ = request.POST.get('id')
        user_ = Authors.objects.filter(tg_id=id)
        if user_.exists():
            return HttpResponseBadRequest('You are already registered')
        user_ = User.objects.filter(username=username)
        if user_.exists():
            return HttpResponseBadRequest('username already exist')

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
    time_ = int(request.GET.get('time'))
    token = request.GET.get('token')
    if not id_ or not time_ or not token:
        print(id_, time_, token)
        return HttpResponseBadRequest('invalid login')

    check_token = hashlib.sha256(str(SECRET_KEY+str(id_)+str(time_)).encode()).hexdigest()
    if not Authors.objects.filter(tg_id=id_).exists():
        return HttpResponseBadRequest('User does not exist')
    if check_token != token:
        print('invalid token')
        print(token, check_token)
        return HttpResponseBadRequest('invalid login')
    if time.time() - time_ > 300:
        return HttpResponseBadRequest('link expired')
    user = Authors.objects.get(tg_id=id_).auth
    login(request, user)
    return redirect('myaccount')


def searchPage(request):
    query = request.GET.get('q')  # Отримати значення пошукового запиту з параметру 'q' у URL
    user = request.user
    if user.is_authenticated:
        try:
            author = Authors.objects.get(auth=user)
        except Exception as e:
            return HttpResponseBadRequest('Something went wrong')
        if author.user_images:
            logo_link = author.user_images.url[5:]
        else:
            logo_link = DEFAULT_LOGO_PATH
    else:
        logo_link = DEFAULT_LOGO_PATH
    if query:
        # Створюємо об'єкт Q для кожного ключового слова
        keywords = query.split()  # Розділити рядок запиту на окремі слова
        q_objects = Q()
        for keyword in keywords:
            q_objects |= Q(title__icontains=keyword) | Q(content__icontains=keyword) # Пошук у полі field_name за збігом з ключовим словом

        # Виконати запит до бази даних, використовуючи об'єкти Q
        results = Posts.objects.filter(q_objects)
        print(results)
        # Тепер results містить об'єкти, які відповідають будь-якому з ключових слів
        # Відобразіть результати у шаблоні або поверніть їх у відповідь JSON, якщо ви використовуєте API
    else:
        results = None
        # Логіка для випадку, коли пошуковий запит порожній


    return render(request, 'search.html', context={'results': results, 'logo_link':logo_link})