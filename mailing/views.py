from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.views.decorators.cache import cache_page
from .models import Recipient, Mailing
from .forms import RegisterForm
from .utils import send_verification_email, verify_email
from django.http import HttpResponse



def is_manager(user):
    """Проверяет, является ли пользователь менеджером (группа 'Менеджер')"""
    return user.groups.filter(name='Менеджер').exists()


@cache_page(60 * 15)
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
    """Список рассылок (фильтрация по владельцу)"""
    user = request.user

    # Если менеджер — видит все рассылки
    if is_manager(user):
        mailings = Mailing.objects.all()
    else:
        # Обычный пользователь — видит только свои рассылки
        mailings = Mailing.objects.filter(owner=user)

    return render(request, 'mailing/mailing_list.html', {'mailings': mailings})


def register(request):
    """Регистрация нового пользователя с отправкой письма для подтверждения email"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(request, user)
            return render(request, 'mailing/registration_confirm.html', {'email': user.email})
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

def verify_email_view(request, token):
    """Представление для подтверждения email по токену"""
    success, message = verify_email(token)
    return render(request, 'mailing/verification_result.html', {
        'success': success,
        'message': message
    })