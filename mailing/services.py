from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import Attempt


def send_mailing(mailing_id):
    """
    Функция для отправки рассылки по её ID.
    """
    from .models import Mailing

    try:
        mailing = Mailing.objects.get(id=mailing_id)
    except Mailing.DoesNotExist:
        print(f"Рассылка с ID {mailing_id} не найдена")
        return

    # 1. Проверяем, можно ли отправлять
    now = timezone.now()
    if not (mailing.start_time <= now <= mailing.end_time):
        print(f"Ошибка: Рассылка {mailing_id} не активна в данный момент")
        print(f"  - start_time: {mailing.start_time}")
        print(f"  - end_time: {mailing.end_time}")
        print(f"  - сейчас: {now}")
        return

    # 2. Получаем всех получателей
    recipients = mailing.recipients.all()
    if not recipients.exists():
        print(f"Ошибка: У рассылки {mailing_id} нет получателей")
        return

    print(f"Начинаем отправку рассылки {mailing_id}")
    print(f"Сообщение: {mailing.message.subject}")
    print(f"Получателей: {recipients.count()}")

    # 3. Отправляем каждому получателю
    for recipient in recipients:
        try:
            # Отправляем письмо
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

            # Создаём запись об успешной попытке
            Attempt.objects.create(
                status='Успешно',
                server_response='Письмо отправлено успешно',
                mailing=mailing
            )
            print(f" Письмо отправлено на {recipient.email}")

        except Exception as e:
            # Создаём запись о неудачной попытке
            Attempt.objects.create(
                status='Не успешно',
                server_response=str(e),
                mailing=mailing
            )
            print(f" Ошибка при отправке на {recipient.email}: {e}")

    print(f"Рассылка {mailing_id} завершена")