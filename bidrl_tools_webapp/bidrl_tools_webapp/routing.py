from django.urls import path
from auto_bid import consumers

websocket_urlpatterns = [
    path('ws/open-items/', consumers.OpenItemsConsumer.as_asgi()),
]