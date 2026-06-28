from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Mailing


class Command(BaseCommand):
    help = 'Создаёт группы пользователей и права доступа'

    def handle(self, *args, **options):
        # Создаём группу "Менеджер"
        manager_group, created = Group.objects.get_or_create(name='Менеджер')

        # Получаем права для модели Mailing
        content_type = ContentType.objects.get_for_model(Mailing)

        # Права на просмотр (только чтение)
        view_permission = Permission.objects.get(
            codename='view_mailing',
            content_type=content_type,
        )

        # Добавляем права менеджеру
        manager_group.permissions.add(view_permission)

        self.stdout.write(self.style.SUCCESS('Группы и права успешно созданы'))