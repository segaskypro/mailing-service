from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import Attempt


def send_mailing(mailing_id):
    """
    Функция для отправки рассылки по её ID.
    Использует bulk_create для массового создания попыток.
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
        return

    # 2. Получаем всех получателей
    recipients = mailing.recipients.all()
    if not recipients.exists():
        print(f"Ошибка: У рассылки {mailing_id} нет получателей")
        return

    print(f"Начинаем отправку рассылки {mailing_id}")
    print(f"Сообщение: {mailing.message.subject}")
    print(f"Получателей: {recipients.count()}")

    # 3. Собираем данные для массового создания попыток
    attempts_to_create = []

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

            # Готовим запись об успешной попытке (НО пока не сохраняем!)
            attempts_to_create.append(
                Attempt(
                    status='Успешно',
                    server_response='Письмо отправлено успешно',
                    mailing=mailing
                )
            )
            print(f" Письмо отправлено на {recipient.email}")

        except Exception as e:
            # Готовим запись о неудачной попытке
            attempts_to_create.append(
                Attempt(
                    status='Не успешно',
                    server_response=str(e),
                    mailing=mailing
                )
            )
            print(f" Ошибка при отправке на {recipient.email}: {e}")

    # 4. ОДНИМ ЗАПРОСОМ сохраняем все попытки в БД (batch-операция!)
    if attempts_to_create:
        Attempt.objects.bulk_create(attempts_to_create)
        print(f"Сохранено {len(attempts_to_create)} попыток в БД")

    print(f"Рассылка {mailing_id} завершена")