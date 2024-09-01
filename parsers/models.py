from django.db import models


# Create your models here.

class EmailAccount(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.email}'

    class Meta:
        verbose_name = 'Email Account'


class EmailMassage(models.Model):
    account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE, related_name='messages')
    title = models.CharField(max_length=255, verbose_name='зоголовок')
    body = models.TextField(verbose_name='тело письма')
    sent_date = models.DateTimeField()
    received_date = models.DateTimeField()
    attachments = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Email Massage'
        verbose_name_plural = 'Email Massages'
