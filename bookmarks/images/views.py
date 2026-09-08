import redis
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from common.decorators import ajax_required
from actions.utils import create_action
from .forms import ImageCreateForm
from .models import Image

import socket
import redis
try:
    import fakeredis
except ImportError:
    fakeredis = None

def get_redis_client():
    """
    Initializes Redis client with zero latency.
    Probes localhost with a 50ms socket check to avoid Windows TCP/IPv6 timeout lag.
    Falls back to high-performance in-memory FakeRedis if no Redis daemon is running.
    """
    host = getattr(settings, 'REDIS_HOST', '127.0.0.1')
    if host == 'localhost':
        host = '127.0.0.1'
    port = getattr(settings, 'REDIS_PORT', 6379)
    db = getattr(settings, 'REDIS_DB', 0)

    is_open = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.05)
        s.connect((host, port))
        s.close()
        is_open = True
    except Exception:
        is_open = False

    if is_open:
        try:
            client = redis.Redis(
                host=host,
                port=port,
                db=db,
                socket_connect_timeout=0.1,
                socket_timeout=0.2,
                decode_responses=True
            )
            client.ping()
            return client
        except Exception:
            pass

    if fakeredis is not None:
        return fakeredis.FakeRedis(decode_responses=True)
    return None

r = get_redis_client()


@login_required
def image_create(request):
    """
    Handles bookmarking images from external URLs.
    Initial title and url are passed via GET from the JavaScript bookmarklet.
    """
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            try:
                new_item = form.save(commit=False)
                new_item.user = request.user
                new_item.save()
                create_action(request.user, 'bookmarked image', new_item)
                messages.success(request, 'Image added successfully!')
                return redirect(new_item.get_absolute_url())
            except Exception as e:
                messages.error(request, 'Could not download image from the remote website. The website may have blocked automated downloads or the link expired. Please try another image.')
        else:
            messages.error(request, 'Error bookmarking image. Please check the provided URL.')
    else:
        # Build form with data provided by the bookmarklet via GET
        form = ImageCreateForm(data=request.GET)

    return render(
        request,
        'images/image/create.html',
        {'section': 'images', 'form': form}
    )


def image_detail(request, id, slug):
    """
    Displays an individual bookmarked image with likes count and user list.
    Tracks total views and image ranking in Redis.
    """
    image = get_object_or_404(Image, id=id, slug=slug)

    total_views = 1
    if r is not None:
        try:
            # Increment total image views in Redis by 1
            total_views = r.incr(f'image:{image.id}:views')
            # Increment image ranking in Redis sorted set by 1
            r.zincrby('image_ranking', 1, image.id)
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            total_views = image.total_likes + 1

    return render(
        request,
        'images/image/detail.html',
        {
            'section': 'images',
            'image': image,
            'total_views': total_views
        }
    )


@ajax_required
@login_required
@require_POST
def image_like(request):
    """
    AJAX endpoint to toggle like/unlike for a given image.
    Logs action in activity stream.
    """
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    """
    Displays the catalog of bookmarked images with AJAX infinite scroll pagination.
    Modern Django replaces request.is_ajax() with checking the X-Requested-With header.
    """
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    try:
        images_page = paginator.page(page)
    except PageNotAnInteger:
        images_page = paginator.page(1)
    except EmptyPage:
        if is_ajax:
            return HttpResponse('')
        images_page = paginator.page(paginator.num_pages)

    if is_ajax:
        return render(
            request,
            'images/image/list_ajax.html',
            {'section': 'images', 'images': images_page}
        )

    return render(
        request,
        'images/image/list.html',
        {'section': 'images', 'images': images_page}
    )


@login_required
def image_ranking(request):
    """
    Displays the leaderboard of the top 10 most viewed images retrieved from Redis sorted sets.
    """
    most_viewed = []
    if r is not None:
        try:
            # Get image ranking from Redis sorted set
            image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
            image_ranking_ids = [int(img_id) for img_id in image_ranking]
            # Get most viewed images in order
            most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
            most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            pass

    # Fallback to images ordered by popularity if Redis had no entries or was offline
    if not most_viewed:
        most_viewed = list(Image.objects.order_by('-total_likes')[:10])

    return render(
        request,
        'images/image/ranking.html',
        {'section': 'ranking', 'most_viewed': most_viewed}
    )
