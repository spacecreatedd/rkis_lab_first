from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from . import forms
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from .models import Post
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from .models import Post, Choice, Profile
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

def index(request):
    posts = Post.objects.filter(expiration_time__gt=timezone.now())
    return render(request, 'main/index.html', {'posts': posts})

def about(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    try:
        profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        # Обработка случая отсутствия профиля
        # Можно вывести сообщение или выполнить другие действия
        return HttpResponse("Profile does not exist")

    choices = Choice.objects.filter(post=post)
    if request.method == 'POST':
        # Обработка голосования
        choice_id = request.POST.get('choice')
        choice = get_object_or_404(Choice, pk=choice_id)

        if request.user.is_authenticated:
            # Проверка, проголосовал ли пользователь уже
            if profile.voted_users.filter(pk=post_id).exists():
                # Если пользователь уже проголосовал, отобразить только результаты
                return HttpResponseRedirect(request.path_info, {'post': post})

            # Создание объекта голоса
            vote = profile.voted_users.add(post)

            # Увеличение счетчика голосов
            choice.vote_count += 1
            choice.save()

            return HttpResponseRedirect(reverse('about', args=[post_id]))

    total_votes = sum(choice.vote_count for choice in choices)
    if total_votes != 0:
        percentages = [(choice.text, choice.vote_count * 100 / total_votes) for choice in choices]
    else:
        percentages=[]

    return render(request, 'main/about.html', {'post': post, 'choices': choices, 'percentages': percentages})

@login_required()
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Ваш аккаунт был обновлен!')
            return redirect('profile')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'web/profile.html', context)
def login(request):
    return render(request, 'registration/login.html')

def register(request):
    return render(request, 'registration/register.html')



#Авторизация, вход и выход
class RegisterUserView(CreateView):
    model = User
    form_class = forms.RegisterUserForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        # Создаем пользователя
        user = form.save()

        # Создаем профиль пользователя
        Profile.objects.create(user=user)

        return super().form_valid(form)

class LoginUserView(LoginView):
    template_name = "registration/login.html"

def logout_view(request):
    logout(request)
    return redirect("login")






def home(request):
    posts = Post.objects.filter(expiration_time__gt=timezone.now())

    return render(request, 'index.html', {'posts': posts})
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    choices = Choice.objects.filter(post=post)

    if request.method == 'POST':
        choice_id = request.POST.get('choice')
        choice = get_object_or_404(Choice, pk=choice_id)
        if request.user.is_authenticated and not choice.voted_users.filter(id=request.user.id).exists():
            choice.voted_users.add(request.user)
            choice.vote_count += 1
            choice.save()
        return HttpResponseRedirect(request.path_info)

    total_votes = sum(choice.vote_count for choice in choices)
    percentages = [(choice.text, choice.vote_count * 100 / total_votes) for choice in choices]

    return render(request, 'about.html', {'post': post, 'choices': choices, 'percentages': percentages})