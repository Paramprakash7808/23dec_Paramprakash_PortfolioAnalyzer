from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class BlockUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if user has a profile and is blocked
            profile = getattr(request.user, 'profile', None)
            if profile and profile.is_blocked:
                # Allow access to 'blocked' page and 'logout'
                allowed_paths = [reverse('blocked'), reverse('logout')]
                if request.path not in allowed_paths:
                    return redirect('blocked')
        
        response = self.get_response(request)
        return response
