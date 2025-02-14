from django.utils import timezone
from datetime import timedelta

class GameSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = request.user.userprofile
            
            # Check if this is a new day
            if profile.last_session_start:
                current_date = timezone.now().date()
                last_session_date = profile.last_session_start.date()
                
                if current_date > last_session_date:
                    # Start new session if it's a new day
                    profile.start_new_session()

        response = self.get_response(request)
        return response