from django.utils import timezone
from django.core.cache import cache

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # User ki last activity ko 5 minute ke liye cache mein save karein
            cache.set(f'seen_{request.user.id}', timezone.now(), 300)
        return self.get_response(request)