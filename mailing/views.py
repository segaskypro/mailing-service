from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Recipient, Mailing
from .forms import RegisterForm


def index(request):
    """Главная страница со статистикой"""
    total_mailings = Mailing.objects.count()

    active_mailings = 0
    for mailing in Mailing.objects.all():
        if mailing.get_status() == 'Запущена':
            active_mailings += 1

    total_recipients = Recipient.objects.count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'total_recipients': total_recipients,
    }
    return render(request, 'mailing/index.html', context)



@login_required
def mailing_list(request):
    """Список всех рассылок (только свои)"""
    mailings = Mailing.objects.all()
    return render(request, 'mailing/mailing_list.html', {'mailings': mailings})




def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('mailing:index')
    else:
        form = RegisterForm()
    return render(request, 'mailing/register.html', {'form': form})


def user_login(request):
    """Вход пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('mailing:index')
        else:
            return render(request, 'mailing/login.html', {'error': 'Неверный логин или пароль'})
    return render(request, 'mailing/login.html')


def user_logout(request):
    """Выход пользователя"""
    logout(request)
    return redirect('mailing:index')