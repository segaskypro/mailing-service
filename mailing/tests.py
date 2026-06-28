from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Recipient, Message, Mailing, Attempt
from .services import send_mailing

class MailingModelTest(TestCase):
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.recipient = Recipient.objects.create(
            email='test@mail.ru',
            full_name='Test User',
            comment='Test comment'
        )
        self.message = Message.objects.create(
            subject='Test Subject',
            body='Test Body'
        )
        self.mailing = Mailing.objects.create(
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1),
            message=self.message,
            owner=self.user
        )
        self.mailing.recipients.add(self.recipient)

    def test_mailing_status(self):
        """Тест: проверка статуса рассылки"""
        status = self.mailing.get_status()
        self.assertEqual(status, 'Запущена')

    def test_send_mailing(self):
        """Тест: отправка рассылки создаёт попытки"""
        send_mailing(self.mailing.id)
        attempts = Attempt.objects.filter(mailing=self.mailing)
        self.assertEqual(attempts.count(), 1)
        self.assertEqual(attempts.first().status, 'Успешно')