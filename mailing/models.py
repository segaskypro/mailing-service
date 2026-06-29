from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User



class Recipient(models.Model):
    """
    Модель получателя рассылки.
    В базе данных это будет таблица с колонками: email, full_name, comment.
    """
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name="Email"
    )
    full_name = models.CharField(
        max_length=150,
        verbose_name="Ф. И. О."
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий"
    )

    def __str__(self):
        # Это отвечает за то, как объект будет отображаться в админке и в списках
        return f"{self.full_name} ({self.email})"

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"

class Message(models.Model):
    """
    Модель сообщения (письма) для рассылки.
    """
    subject = models.CharField(
        max_length=255,
        verbose_name="Тема письма"
    )
    body = models.TextField(
        verbose_name="Тело письма"
    )

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

class Mailing(models.Model):
    """
    Модель рассылки.
    Связывает сообщение, получателей и временные рамки.
    """
    start_time = models.DateTimeField(
        verbose_name="Дата и время начала отправки"
    )
    end_time = models.DateTimeField(
        verbose_name="Дата и время окончания отправки"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name="Сообщение"
    )
    recipients = models.ManyToManyField(
        Recipient,
        verbose_name="Получатели"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Рассылка #{self.id} ({self.message.subject})"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def get_status(self):
        """
        Динамически вычисляем статус рассылки:
        - 'Создана' - текущая дата раньше start_time
        - 'Запущена' - текущая дата между start_time и end_time
        - 'Завершена' - текущая дата позже end_time
        """
        now = timezone.now()

        if now < self.start_time:
            return "Создана"
        elif self.start_time <= now <= self.end_time:
            return "Запущена"
        else:
            return "Завершена"


class Attempt(models.Model):
    """
    Модель попытки отправки письма.
    Сохраняет историю каждой отправки.
    """
    STATUS_CHOICES = [
        ('Успешно', 'Успешно'),
        ('Не успешно', 'Не успешно'),
    ]

    attempt_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время попытки"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="Статус"
    )
    server_response = models.TextField(
        blank=True,
        verbose_name="Ответ почтового сервера"
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        verbose_name="Рассылка"
    )

    def __str__(self):
        return f"Попытка #{self.id} - {self.status}"

    class Meta:
        verbose_name = "Попытка"
        verbose_name_plural = "Попытки"


class EmailVerification(models.Model):
    """Модель для хранения токенов подтверждения email"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        """Токен действителен 24 часа"""
        from django.utils import timezone
        return (timezone.now() - self.created_at).days >= 1

    def __str__(self):
        return f"Токен для {self.user.email}"