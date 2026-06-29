from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from .models import EmailVerification
import uuid


def generate_verification_token(user):
    """Генерирует уникальный токен для подтверждения email"""
    token = str(uuid.uuid4())
    EmailVerification.objects.update_or_create(
        user=user,
        defaults={'token': token}
    )
    return token


def send_verification_email(request, user):
    """Отправляет письмо со ссылкой для подтверждения email"""
    token = generate_verification_token(user)
    verification_link = f"http://{get_current_site(request).domain}/verify-email/{token}/"

    subject = 'Подтверждение email для сервиса рассылок'
    message = f"""
    Здравствуйте, {user.username}!

    Перейдите по ссылке, чтобы подтвердить свой email:
    {verification_link}

    Ссылка действительна 24 часа.

    С уважением,
    Сервис управления рассылками
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def verify_email(token):
    """Проверяет токен и активирует пользователя"""
    try:
        verification = EmailVerification.objects.get(token=token)
        if verification.is_expired():
            return False, 'Срок действия ссылки истёк'

        user = verification.user
        user.is_active = True
        user.save()
        verification.delete()  # Удаляем токен после активации
        return True, 'Email успешно подтверждён'
    except EmailVerification.DoesNotExist:
        return False, 'Неверная ссылка подтверждения'