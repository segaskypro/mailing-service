from django.contrib import admin
from mailing.models import Recipient, Message, Mailing, Attempt

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'comment']
    search_fields = ['full_name', 'email']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'body_preview']
    search_fields = ['subject']

    def body_preview(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    body_preview.short_description = "Тело (предпросмотр)"

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'start_time', 'end_time', 'get_status', 'recipients_count']
    filter_horizontal = ['recipients']

    def recipients_count(self, obj):
        return obj.recipients.count()
    recipients_count.short_description = "Кол-во получателей"


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'mailing', 'attempt_time', 'status', 'server_response_preview']
    list_filter = ['status', 'mailing']
    search_fields = ['server_response']

    def server_response_preview(self, obj):
        return obj.server_response[:50] + '...' if len(obj.server_response) > 50 else obj.server_response

    server_response_preview.short_description = "Ответ сервера"