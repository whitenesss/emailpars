import json
from channels.generic.websocket import AsyncWebsocketConsumer

# Веб-сокетный потребитель для обработки процесса получения сообщений электронной почты
class FetchMessagesConsumer(AsyncWebsocketConsumer):
    # Метод, вызываемый при установке веб-сокетного соединения
    async def connect(self):
        # Добавление текущего веб-сокета в группу 'fetch_messages_group'
        await self.channel_layer.group_add(
            'fetch_messages_group',  # Имя группы, к которой присоединяется веб-сокет
            self.channel_name  # Имя канала веб-сокета
        )
        # Принятие веб-сокетного соединения
        await self.accept()

    # Метод, вызываемый при отключении веб-сокетного соединения
    async def disconnect(self, close_code):
        # Удаление текущего веб-сокета из группы 'fetch_messages_group'
        await self.channel_layer.group_discard(
            'fetch_messages_group',  # Имя группы, от которой отсоединяется веб-сокет
            self.channel_name  # Имя канала веб-сокета
        )

    # Метод для обработки события обновления прогресса
    async def update_progress(self, event):
        progress = event['progress']  # Извлечение прогресса из события
        message = event['message']  # Извлечение сообщения из события

        # Отправка данных обратно клиенту через веб-сокет
        await self.send(text_data=json.dumps({
            'progress': progress,  # Прогресс процесса получения сообщений
            'message': message  # Детали сообщения (заголовок, дата и т.д.)
        }))
