from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile, UserMissionProgress

@login_required
def custom_logout(request):
    # Reset user's profile
    if hasattr(request.user, 'userprofile'):
        user_profile = request.user.userprofile
        user_profile.total_score = 0
        user_profile.total_xp = 0
        user_profile.title = "Apprentice Project Manager"  # Your default title
        user_profile.save()
    
    # Clear all mission progress
    UserMissionProgress.objects.filter(user=request.user).delete()
    
    # Perform logout
    logout(request)
    return redirect('login')