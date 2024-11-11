from django.shortcuts import render
from .models import ItemUserInput
import time
from pathlib import Path
import sys
from django.urls import URLPattern, URLResolver, get_resolver

# add parent directory (repository directory) to the path so that config file can be read
bidrl_tools_directory = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(bidrl_tools_directory))

from config import user_name, local_ip_address


### helper functions ###

def convert_seconds_to_time_string(seconds):
    days, seconds = divmod(seconds, 86400)  # 60 seconds * 60 minutes * 24 hours
    hours, seconds = divmod(seconds, 3600)  # 60 seconds * 60 minutes
    minutes, seconds = divmod(seconds, 60)
    time_string = ''

    if days >= 1:
        #time_string += f"{days}d, {hours}h"
        time_string += f"{days}d, {hours}h, {minutes}m, {seconds}s"
    elif hours >= 1:
        #time_string += f"{hours}h, {minutes}m"
        time_string += f"{hours}h, {minutes}m, {seconds}s"
    else:
        time_string += f"{minutes}m, {seconds}s"

    return time_string

def get_all_url_patterns(urlpatterns, prefix=''):
        urls = []
        for pattern in urlpatterns:
            if isinstance(pattern, URLPattern):
                url_to_add = prefix + str(pattern.pattern)
                if url_to_add != '':
                    urls.append(url_to_add)
            elif isinstance(pattern, URLResolver):
                nested_prefix = prefix + str(pattern.pattern)
                urls.extend(get_all_url_patterns(pattern.url_patterns, nested_prefix))
        return urls



### views ###

def index(request):
    data = ItemUserInput.objects.all()
    # Extract all URL patterns
    raw_urls = get_all_url_patterns(get_resolver().url_patterns)
    urls = [f'http://{local_ip_address}:8000/' + url for url in raw_urls]
    return render(request, 'index.html', {'data': data, 'urls': urls})

def auto_bid_view(request):
    current_unix_time = int(time.time())
    all_items = ItemUserInput.objects.all().order_by('-end_time_unix') # all items in order of descending end_time_unix

    all_closed_items = ItemUserInput.objects.filter(end_time_unix__lt=current_unix_time, max_desired_bid__gt=0).order_by('-end_time_unix') # end_time_unix < current time and max_desired_bid > 0
    # run calculations and field editions for all_closed_items
    for item in all_closed_items:
        item.is_lost = item.highbidder_username != user_name
        item.sold_date = time.strftime('%m/%d/%y', time.localtime(item.end_time_unix))

    all_open_items = ItemUserInput.objects.filter(end_time_unix__gte=current_unix_time, max_desired_bid__gt=0).order_by('end_time_unix') # end_time_unix >= current time and max_desired_bid > 0
    # run calculations and field editions for all_open_items
    for item in all_open_items:
        item.remaining_time = item.end_time_unix - current_unix_time
        item.remaining_time_string = convert_seconds_to_time_string(item.end_time_unix - current_unix_time)
        item.is_lost = item.current_bid >= item.max_desired_bid

    return render(request, 'auto_bid.html', {'all_items': all_items
                                             , 'all_open_items': all_open_items
                                             , 'all_closed_items': all_closed_items})