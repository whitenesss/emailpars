from django.db import models



class EmailAccount(models.Model):
    """Модель для представления учетной записи электронной почты"""
    email = models.EmailField(unique=True)  # Поле для хранения адреса электронной почты
    password = models.CharField(
        max_length=128)  # Поле для хранения пароля электронной почты

    def __str__(self):
        return f'{self.email}'

    class Meta:
        verbose_name = 'Email Account'
        verbose_name_plural = 'Email Accounts'


class EmailMessage(models.Model):
    """Модель для представления сообщения электронной почты"""
    account = models.ForeignKey(
        EmailAccount,
        on_delete=models.CASCADE,
        related_name='messages'
    )  # Связь с учетной записью электронной почты. Удаление учетной записи приведет к удалению связанных сообщений
    title = models.CharField(max_length=255,
                             verbose_name='заголовок')  # Поле для хранения заголовка сообщения, максимальная длина 255 символов
    body = models.TextField(verbose_name='тело письма')  # Поле для хранения текста сообщения
    sent_date = models.DateTimeField()  # Поле для хранения даты и времени отправки сообщения
    received_date = models.DateTimeField()  # Поле для хранения даты и времени получения сообщения
    attachments = models.JSONField(null=True, blank=True)  # Поле для хранения вложений в формате JSON.
    uid = models.CharField(max_length=255, unique=True, null=True,
                           blank=True)  # Поле для хранения уникального идентификатора сообщения

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Email Message'
        verbose_name_plural = 'Email Messages'
