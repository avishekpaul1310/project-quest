from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Mission, Question, UserMissionProgress
from django.db.models import Sum

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('game:dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'game/login.html')

def logout_view(request):
    logout(request)
    return redirect('game:login')

@login_required
def dashboard(request):
    missions = Mission.objects.filter(is_active=True)
    progress_data = {}
    
    for mission in missions:
        progress = UserMissionProgress.objects.filter(
            user=request.user,
            mission=mission
        ).first()
        progress_data[mission.id] = progress
    
    return render(request, 'game/dashboard.html', {
        'missions': missions,
        'progress_data': progress_data,
        'user_profile': request.user.userprofile
    })

@login_required
def mission_learning(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    progress = UserMissionProgress.objects.filter(
        user=request.user,
        mission=mission
    ).first()
    
    return render(request, 'game/mission_learning.html', {
        'mission': mission,
        'progress': progress
    })

@login_required
def take_quiz(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    questions = mission.questions.all()
    
    if request.method == 'POST':
        score = 0
        for question in questions:
            answer = request.POST.get(f'question_{question.id}')
            if answer == question.correct_option:
                score += 20  # 20 points per correct answer
        
        # Update mission progress
        progress, created = UserMissionProgress.objects.get_or_create(
            user=request.user,
            mission=mission
        )
        progress.score = score
        progress.completed = True
        progress.save()
        
        # Update total score and XP
        profile = request.user.userprofile
        total_score = UserMissionProgress.objects.filter(
            user=request.user,
            completed=True
        ).aggregate(Sum('score'))['score__sum'] or 0
        profile.total_score = total_score
        profile.xp_points += mission.xp_reward
        
        # Update title based on XP
        if profile.xp_points >= 300:
            profile.title = "Royal Project Consultant"
        if profile.xp_points >= 600:
            profile.title = "King's Chief Project Manager"
            
        profile.save()
        
        return redirect('game:mission_results', mission_id=mission.id)
    
    return render(request, 'game/take_quiz.html', {
        'mission': mission,
        'questions': questions
    })

@login_required
def mission_results(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    progress = get_object_or_404(UserMissionProgress, 
        user=request.user,
        mission=mission
    )
    
    return render(request, 'game/mission_results.html', {
        'mission': mission,
        'progress': progress
    })