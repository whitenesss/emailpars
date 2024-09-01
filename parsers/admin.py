from django.contrib import admin
from django.utils.html import format_html

from parsers.models import EmailAccount, EmailMessage


# Register your models here.
@admin.register(EmailAccount)
class EmailAccountAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "password")


@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ("account", "title", "body")
    readonly_fields = ('body',)  # Если вы не хотите, чтобы поле редактировалось

    def body(self, obj):
        return format_html(obj.body)

    body.short_description = 'Body'


