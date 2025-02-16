from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Mission, Question, UserMissionProgress
from django.db.models import Sum
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

@login_required
def dashboard(request):
    missions = Mission.objects.filter(is_active=True).order_by('order')
    user_progress = UserMissionProgress.objects.filter(user=request.user)
    
    mission_status = []
    completed_missions = 0
    previous_completed = True  # First mission is always accessible
    
    for mission in missions:
        progress = user_progress.filter(mission=mission).first()
        completed = progress.completed if progress else False
        if completed:
            completed_missions += 1
        
        mission_status.append({
            'mission': mission,
            'completed': completed,
            'score': progress.score if progress else 0,
            'accessible': previous_completed  # Only accessible if previous mission is completed
        })
        previous_completed = completed  # Update for next iteration
    
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
                'explanation': question.explanation  # Add this field to your Question model
            })
        
        # Save progress and update profile as before
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
        
        # Render results page instead of redirecting
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

# Add this class for proper logout handling
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')