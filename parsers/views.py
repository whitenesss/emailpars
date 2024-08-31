
from rest_framework.generics import get_object_or_404

from django.shortcuts import render, get_object_or_404

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
from imapclient import IMAPClient
from parsers.models import EmailAccount, EmailMassage


# Create your views here.
def email_massage(request):
    return render(request, 'parsers/email_massage.html')


# def fetch_messages(account_id):
#     account = get_object_or_404(EmailAccount, id=account_id)
#     channel_layer = get_channel_layer()
#     messages_fetched = 0
#
#     with IMAPClient('imap.yandex.ru') as server:
#         server.login(account.email, account.password)
#         server.select_folder('INBOX')
#         response = server.search(['ALL'])
#         total_messages = len(response)
#
#         for msg_id in response:
#             msg = server.fetch([msg_id], ['ENVELOPE', 'BODY[]'])
#             envelope = msg[msg_id][b'ENVELOPE']
#             body = msg[msg_id][b'BODY[]'].decode()
#
#             email_message = EmailMassage.objects.create(
#                 account=account,
#                 subject=envelope.subject.decode(),
#                 sent_date=envelope.date,
#                 received_date=time.time(),
#                 body=body,
#                 attachments=[]
#             )
#
#             messages_fetched += 1
#             progress = int((messages_fetched / total_messages) * 100)
#
#             async_to_sync(channel_layer.group_send)(
#                 'fetch_messages_group',
#                 {
#                     'type': 'update_progress',
#                     'progress': progress,
#                     'message': {
#                         'id': email_message.id,
#                         'subject': email_message.subject,
#                         'sent_date': email_message.sent_date.strftime('%Y-%m-%d %H:%M:%S'),
#                         'received_date': email_message.received_date.strftime('%Y-%m-%d %H:%M:%S'),
#                         'body': email_message.body,
#                         'attachments': email_message.attachments,
#                     }
#                 }
#
#             )