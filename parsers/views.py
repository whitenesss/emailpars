from django.shortcuts import render
import html
from django.views.decorators.csrf import csrf_exempt
from email.utils import parsedate_to_datetime
from django.http import JsonResponse
from imapclient import IMAPClient
from email import message_from_bytes, header
from django.utils import timezone
from parsers.models import EmailAccount, EmailMessage
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from bs4 import BeautifulSoup


def email_massage(request):
    """Отображения HTML страницы с формой для работы с письмами"""
    return render(request, 'parsers/email_massage.html')


@csrf_exempt  # Отключаем защиту от CSRF
def fetch_messages_view(request):
    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        if account_id:
            try:
                account_id = int(account_id)  # Преобразуем account_id в целое число
                fetch_messages(account_id)  # Вызываем функцию для получения сообщений
                return JsonResponse({'status': 'success'})  # Возвращаем успешный ответ
            except ValueError:
                return JsonResponse({'error': 'Invalid account_id'},
                                    status=400)  # Возвращаем ошибку при некорректном account_id
            except EmailAccount.DoesNotExist:
                return JsonResponse({'error': 'Account not found'},
                                    status=404)  # Возвращаем ошибку, если аккаунт не найден
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)  # Возвращаем ошибку при возникновении исключения
        return JsonResponse({'error': 'No account_id provided'},
                            status=400)  # Возвращаем ошибку при отсутствии account_id
    return JsonResponse({'error': 'Invalid request method'},
                        status=400)  # Возвращаем ошибку при неправильном методе запроса


def decode_mime_header(header_value):
    # Декодируем заголовок MIME (например, заголовок темы письма)
    decoded_header = header.decode_header(header_value)
    decoded_str = ''
    for part, encoding in decoded_header:
        if isinstance(part, bytes):
            decoded_str += part.decode(encoding or 'utf-8')  # Декодируем байтовые части заголовка
        else:
            decoded_str += part  # Добавляем текстовые части заголовка
    return decoded_str


def get_imap_settings(email):
    # Получаем домен из email адреса
    domain = email.split('@')[-1].lower()

    # Определяем настройки сервера в зависимости от домена
    if domain == 'yandex.ru':
        return {
            'server': 'imap.yandex.ru',
            'port': 993,
            'use_ssl': True
        }
    elif domain == 'gmail.com':
        return {
            'server': 'imap.gmail.com',
            'port': 993,
            'use_ssl': True
        }
    elif domain == 'mail.ru':
        return {
            'server': 'imap.mail.ru',
            'port': 993,
            'use_ssl': True
        }
    else:
        raise ValueError(f'IMAP settings for domain {domain} are not configured')


def fetch_messages(account_id):
    try:
        # Получаем объект EmailAccount по account_id
        account = EmailAccount.objects.get(id=account_id)
        channel_layer = get_channel_layer()  # Получаем канал для отправки сообщений
        messages_fetched = 0
        imap_settings = get_imap_settings(account.email)

        # Подключаемся к IMAP серверу
        with IMAPClient(imap_settings['server'], port=imap_settings['port'], use_uid=True, ssl=imap_settings['use_ssl']) as server:
            server.login(account.email, account.password)  # Выполняем логин
            server.select_folder('INBOX')  # Выбираем папку 'INBOX'
            response = server.search(['ALL'])  # Ищем все сообщения
            total_messages = len(response)  # Получаем общее количество сообщений

            for msg_id in response:
                # Получаем сырой формат сообщения
                raw_message = server.fetch([msg_id], ['ENVELOPE', 'BODY[]'])[msg_id][b'BODY[]']
                email_message = message_from_bytes(raw_message)  # Преобразуем в объект сообщения
                uid = email_message.get('Message-ID', str(msg_id))  # Получаем уникальный идентификатор сообщения

                # Проверяем, существует ли уже сообщение с таким UID в базе данных
                if EmailMessage.objects.filter(uid=uid).exists():
                    continue  # Пропускаем сообщение, если оно уже существует

                # Декодируем тему сообщения
                subject = decode_mime_header(email_message['Subject']) if email_message['Subject'] else "(No Subject)"

                # Декодируем тело сообщения
                body = ""
                plain_text_parts = []

                if email_message.is_multipart():
                    # Если сообщение многосоставное
                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            plain_text_parts.append(
                                part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore'))
                        elif content_type == "text/html" and "attachment" not in content_disposition:
                            html_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                            soup = BeautifulSoup(html_content, 'html.parser')
                            plain_text_parts.append(soup.get_text())  # Конвертируем HTML в текст
                else:
                    # Если сообщение не многосоставное
                    if email_message.get_content_type() == "text/plain":
                        body = email_message.get_payload(decode=True).decode(
                            email_message.get_content_charset() or 'utf-8', errors='ignore')
                    elif email_message.get_content_type() == "text/html":
                        html_content = email_message.get_payload(decode=True).decode(
                            email_message.get_content_charset() or 'utf-8', errors='ignore')
                        soup = BeautifulSoup(html_content, 'html.parser')
                        body = soup.get_text()  # Конвертируем HTML в текст

                # Объединяем все части текста в одно тело
                body = "\n".join(plain_text_parts) if plain_text_parts else body

                # Парсим дату из заголовка сообщения
                sent_date = parsedate_to_datetime(email_message['Date']) if email_message['Date'] else timezone.now()

                # Создаем объект EmailMessage
                email_msg_obj = EmailMessage.objects.create(
                    account=account,
                    uid=uid,  # Сохраняем уникальный идентификатор
                    title=subject,
                    body=body,
                    sent_date=sent_date,
                    received_date=timezone.now(),
                    attachments=[]  # Обработка вложений при необходимости
                )

                messages_fetched += 1
                progress = int((messages_fetched / total_messages) * 100)  # Рассчитываем прогресс загрузки

                # Отправляем информацию о прогрессе в канал
                async_to_sync(channel_layer.group_send)(
                    'fetch_messages_group',
                    {
                        'type': 'update_progress',
                        'progress': progress,
                        'message': {
                            'id': email_msg_obj.id,
                            'title': email_msg_obj.title,
                            'sent_date': email_msg_obj.sent_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'received_date': email_msg_obj.received_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'body': email_msg_obj.body,
                            'attachments': email_msg_obj.attachments
                        }
                    }
                )

    except Exception as e:
        print(f'Error in fetch_messages: {e}')  # Логируем ошибку, если она произошла
