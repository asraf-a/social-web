from functools import wraps
from django.http import HttpResponseBadRequest


def ajax_required(f):
    """
    Decorator to ensure a view is only called via an AJAX request.
    Note: request.is_ajax() was deprecated in Django 3.1 and removed in Django 4.0+.
    The modern, standard Django replacement checks the X-Requested-With header.
    """
    @wraps(f)
    def wrap(request, *args, **kwargs):
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        if not is_ajax:
            return HttpResponseBadRequest('Invalid request: AJAX required')
        return f(request, *args, **kwargs)
    return wrap
