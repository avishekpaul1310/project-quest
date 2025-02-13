from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Mission, Question, UserMissionProgress

@login_required
def dashboard(request):
    missions = Mission.objects.filter(is_active=True)
    user_progress = UserMissionProgress.objects.filter(user=request.user)
    
    mission_status = []
    for mission in missions:
        progress = user_progress.filter(mission=mission).first()
        mission_status.append({
            'mission': mission,
            'completed': progress.completed if progress else False,
            'score': progress.score if progress else 0
        })
    
    return render(request, 'game/dashboard.html', {
        'mission_status': mission_status
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
                score += 10
        
        progress, created = UserMissionProgress.objects.get_or_create(
            user=request.user,
            mission=mission
        )
        progress.score = score
        progress.completed = True
        progress.save()
        
        return redirect('game:quiz_results', mission_id=mission_id)
    
    return render(request, 'game/take_quiz.html', {
        'mission': mission,
        'questions': questions
    })

@login_required
def quiz_results(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    progress = get_object_or_404(
        UserMissionProgress,
        user=request.user,
        mission=mission
    )
    
    return render(request, 'game/quiz_results.html', {
        'mission': mission,
        'score': progress.score
    })