from django.shortcuts import render
from .models import ItemUserInput
import time

def index(request):
    data = ItemUserInput.objects.all()
    return render(request, 'index.html', {'data': data})

def auto_bid_view(request):
    current_unix_time = int(time.time())
    all_items = ItemUserInput.objects.all().order_by('-end_time_unix') # all items in order of descending end_time_unix
    all_open_items = ItemUserInput.objects.filter(end_time_unix__gte=current_unix_time).order_by('end_time_unix') # end_time_unix >= current time
    all_closed_items = ItemUserInput.objects.filter(end_time_unix__lt=current_unix_time).order_by('-end_time_unix') # end_time_unix < current time
    return render(request, 'auto_bid.html', {'all_items': all_items
                                             , 'all_open_items': all_open_items
                                             , 'all_closed_items': all_closed_items})