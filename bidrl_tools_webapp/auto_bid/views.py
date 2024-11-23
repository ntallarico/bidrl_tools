import sys
import time
import json
from django.shortcuts import render
from pathlib import Path
from django.urls import URLPattern, URLResolver, get_resolver
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from .models import ItemUserInput

# add parent directory (repository directory) to the path so that config file can be read
bidrl_tools_directory = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(bidrl_tools_directory))

from config import user_name
import bidrl_functions as bf

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

# returns a list of open favorited items from the database, with some additional calculated fields
# note: return a list, not a QuerySet. 
def get_fav_open_items_list():
    current_unix_time = int(time.time())
    fav_open_items = ItemUserInput.objects.filter(end_time_unix__gte=current_unix_time, max_desired_bid__gt=0).order_by('end_time_unix') # end_time_unix >= current time and max_desired_bid > 0
    
    fav_open_items_list = []
    for item in fav_open_items:
        item_dict = model_to_dict(item)  # Convert model instance to dictionary
        # Add additional computed fields
        item_dict.update({
            'remaining_time_string': convert_seconds_to_time_string(item.end_time_unix - current_unix_time)
            , 'is_lost': item.current_bid >= item.max_desired_bid
            # Add any other computed fields here
        })
        fav_open_items_list.append(item_dict)
    
    return fav_open_items_list

### functions for javascript? not views directly or helper functions. update this title when this section expands ###

def fetch_data(request):
    current_unix_time = int(time.time())
    fav_open_items_list = get_fav_open_items_list()
    return JsonResponse({'fav_open_items_list': fav_open_items_list})

@csrf_exempt
def update_bids(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            for bid in data['bids']:
                try:
                    item = ItemUserInput.objects.get(item_id=bid['item_id'])
                    item.max_desired_bid = float(bid['max_desired_bid'])
                    item.save()
                except ItemUserInput.DoesNotExist:
                    return JsonResponse({'success': False, 'error': f"Item with ID {bid['item_id']} does not exist"}, status=404)
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


### views ###

def index(request):
    data = ItemUserInput.objects.all()
    # Extract all URL patterns
    raw_urls = get_all_url_patterns(get_resolver().url_patterns)
    local_ip_address = bf.get_local_ip()
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

    fav_open_items_list = get_fav_open_items_list()

    return render(request, 'auto_bid.html', {'all_items': all_items
                                             , 'fav_open_items': fav_open_items_list
                                             , 'all_closed_items': all_closed_items})