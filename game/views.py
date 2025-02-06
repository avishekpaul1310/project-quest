from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Mission, Question, Choice, PlayerAnswer

@login_required
def dashboard(request):
    return render(request, 'game/dashboard.html')

@login_required
def mission_detail(request, mission_id):
    return render(request, 'game/mission_detail.html')

@login_required
def submit_answer(request, mission_id):
    if request.method == 'POST':
        return redirect('game:mission_detail', mission_id=mission_id)
    return redirect('game:mission_detail', mission_id=mission_id)