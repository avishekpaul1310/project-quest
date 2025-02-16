from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Mission, Question, UserMissionProgress
from django.db.models import Sum

@login_required
def dashboard(request):
    missions = Mission.objects.filter(is_active=True).order_by('order')
    user_progress = UserMissionProgress.objects.filter(user=request.user)
    
    mission_status = []
    completed_missions = 0
    
    for mission in missions:
        progress = user_progress.filter(mission=mission).first()
        completed = progress.completed if progress else False
        if completed:
            completed_missions += 1
            
        mission_status.append({
            'mission': mission,
            'completed': completed,
            'score': progress.score if progress else 0,
        })
    
    context = {
        'mission_status': mission_status,
        'completed_missions': completed_missions,
    }
    
    return render(request, 'game/dashboard.html', context)

@login_required
def mission_detail(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    progress = UserMissionProgress.objects.filter(
        user=request.user, mission=mission
    ).first()
    
    if progress and progress.completed:
        messages.info(request, "You've already completed this mission!")
        return redirect('game:dashboard')
    
    return render(request, 'game/mission_detail.html', {
        'mission': mission,
    })

@login_required
def mission_quiz(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    questions = Question.objects.filter(mission=mission)
    
    if request.method == 'POST':
        score = 0
        total_questions = questions.count()
        
        for question in questions:
            answer = request.POST.get(f'question_{question.id}')
            if answer == question.correct_option:
                score += 10
        
        # Save progress and award XP
        progress, created = UserMissionProgress.objects.get_or_create(
            user=request.user,
            mission=mission,
            defaults={'completed': True, 'score': score}
        )
        
        if not created:
            progress.completed = True
            progress.score = score
            progress.save()
        
        # Update user profile score and XP
        profile = request.user.userprofile
        profile.total_score = UserMissionProgress.objects.filter(
            user=request.user
        ).aggregate(Sum('score'))['score__sum'] or 0
        
        # Award XP if mission was not previously completed
        if created:
            profile.total_xp += mission.xp_reward
        
        # Update title based on XP
        if profile.total_xp >= 300:
            profile.title = "Royal Project Consultant"
        if profile.total_xp >= 600:
            profile.title = "King's Chief Project Manager"
        profile.save()
        
        messages.success(
            request,
            f'Mission completed! You scored {score} points and earned {mission.xp_reward} XP!'
        )
        return redirect('game:dashboard')