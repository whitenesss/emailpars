from django.urls import re_path
from .consumers import FetchMessagesConsumer

websocket_urlpatterns = [
    re_path(r'ws/fetch_messages/$', FetchMessagesConsumer.as_asgi()),
]