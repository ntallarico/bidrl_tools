from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('auto_bid/', views.auto_bid_view, name='auto_bid'),
    path('fetch-data/', views.fetch_data, name='fetch-data'),
    path('update-bids/', views.update_bids, name='update_bids'),
]