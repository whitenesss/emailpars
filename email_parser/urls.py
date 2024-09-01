
from django.contrib import admin
from django.urls import path
from parsers import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('email-massage/', views.email_massage, name='email_massage'),
    path('fetch-messages/', views.fetch_messages_view, name='fetch_messages'),
]

