# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ItemUserInput
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# @receiver(post_save, sender=ItemUserInput)
# def notify_item_update(sender, instance, created, **kwargs):
#     # This function will be called after an ItemUserInput instance is saved
#     print(f"Item updated: {instance.item_id}")  # Debugging line to ensure the signal is triggered

#     # Get the channel layer
#     channel_layer = get_channel_layer()

#     # Send a message to the WebSocket group
#     async_to_sync(channel_layer.group_send)(
#         "open_items_group",  # Group name
#         {
#             "type": "item_update",
#             "message": {
#                 "description": instance.description,
#                 "max_desired_bid": instance.max_desired_bid,
#                 "item_bid_group_id": instance.item_bid_group_id,
#                 "ibg_items_to_win": instance.ibg_items_to_win,
#                 "current_bid": instance.current_bid,
#                 "highbidder_username": instance.highbidder_username,
#             }
#         }
#     )