from django.shortcuts import render
from .models import Bid, Item, Affiliate, Auction, Invoice, Image


def index(request):
    data = Item.objects.all()
    return render(request, 'index.html', {'data': data})