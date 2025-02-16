from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Mission, Question, UserMissionProgress, UserProfile

@login_required
def dashboard(request):
    missions = Mission.objects.filter(is_active=True).order_by('order')
    user_progress = UserMissionProgress.objects.filter(user=request.user)
    
    mission_status = []
    completed_missions = 0
    previous_completed = True
    
    for mission in missions:
        progress = user_progress.filter(mission=mission).first()
        completed = progress.completed if progress else False
        if completed:
            completed_missions += 1
        
        mission_status.append({
            'mission': mission,
            'completed': completed,
            'score': progress.score if progress else 0,
            'accessible': previous_completed
        })
        previous_completed = completed
    
    context = {
        'mission_status': mission_status,
        'completed_missions': completed_missions,
    }
    
    return render(request, 'game/dashboard.html', context)

@login_required
def mission_detail(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    user_progress = UserMissionProgress.objects.filter(
        user=request.user,
        mission=mission
    ).first()
    
    context = {
        'mission': mission,
        'completed': user_progress.completed if user_progress else False
    }
    
    return render(request, 'game/mission_detail.html', context)

@login_required
def mission_quiz(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    questions = Question.objects.filter(mission=mission)
    
    if not questions.exists():
        messages.warning(request, "No questions available for this mission yet.")
        return redirect('game:mission_detail', mission_id=mission_id)
    
    if request.method == 'POST':
        score = 0
        quiz_results = []
        
        for question in questions:
            answer = request.POST.get(f'question_{question.id}')
            is_correct = answer == question.correct_option
            if is_correct:
                score += 10
            
            quiz_results.append({
                'question': question,
                'user_answer': answer,
                'correct_answer': question.correct_option,
                'is_correct': is_correct,
                'explanation': question.explanation
            })
        
        progress, created = UserMissionProgress.objects.get_or_create(
            user=request.user,
            mission=mission,
            defaults={'completed': True, 'score': score}
        )
        
        if not created:
            progress.completed = True
            progress.score = score
            progress.save()
        
        profile = request.user.userprofile
        profile.total_score = UserMissionProgress.objects.filter(
            user=request.user
        ).aggregate(Sum('score'))['score__sum'] or 0
        
        if created:
            profile.total_xp += mission.xp_reward
        
        if profile.total_xp >= 300:
            profile.title = "Royal Project Consultant"
        if profile.total_xp >= 600:
            profile.title = "King's Chief Project Manager"
        profile.save()
        
        return render(request, 'game/quiz_results.html', {
            'mission': mission,
            'quiz_results': quiz_results,
            'score': score,
            'xp_earned': mission.xp_reward if created else 0
        })
    
    return render(request, 'game/mission_quiz.html', {
        'mission': mission,
        'questions': questions,
    })