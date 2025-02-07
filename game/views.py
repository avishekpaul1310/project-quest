from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Mission, Question, PlayerProfile
from django.contrib import messages

@login_required
def dashboard(request):
    """Display available missions and user progress."""
    player_profile = request.user.playerprofile
    missions = Mission.objects.filter(is_active=True).order_by('order')
    
    context = {
        'player_profile': player_profile,
        'missions': missions,
    }
    return render(request, 'game/dashboard.html', context)

@login_required
def mission_detail(request, mission_id):
    """Display mission details and questions."""
    mission = get_object_or_404(Mission, pk=mission_id)
    player_profile = request.user.playerprofile
    
    # Check if user can access this mission
    if not player_profile.can_access_mission(mission):
        messages.error(request, 'You need to complete previous missions first!')
        return redirect('game:dashboard')
    
    context = {
        'mission': mission,
        'player_profile': player_profile,
    }
    return render(request, 'game/mission_detail.html', context)